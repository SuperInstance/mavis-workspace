# Asciipocalypse ports to .NET 9 and compiles. 0 errors.

2026-10-02. **The hardest blocker in the whole Asciipocalypse design is gone, and
it was four lines of project-file edits.** Measured, not asserted.

```
$ dotnet build ASCII_FPS/ASCII_FPS.csproj
Build succeeded.
    0 Error(s)
```

## The port, exactly — four changes

| # | file | change | why |
|---|---|---|---|
| 1 | `ASCII_FPS.csproj` | `netcoreapp3.1` → `net9.0` | SDK 9.0.316 ships no 3.1 targeting pack |
| 2 | `ASCII_FPS.csproj` | drop `<MonoGameContentReference>` | `mgcb.dll` exits **150**; the content build is not needed to simulate |
| 3 | `ASCII_FPS.csproj` | drop the `MonoGame.Content.Builder.Task` package | it imports the MGCB targets that fail |
| 4 | `OBJContentPipelineExtension.csproj` | old-style `v4.5` → SDK-style `net9.0`, **and compile only `OBJFile.cs`** | `OBJImporter`/`Writer`/`Processor` are MGCB-only; `OBJFile` is pure |

**That is the whole port.** No source file was edited. **The game was already
modern enough; only the project files were stale.**

## Two failures on the way, both worth recording

**MGCB exits 150.** `MonoGame.Content.Builder.Task` shells out to `mgcb.dll` to
compile `.mgcb` → `.xnb`. It fails. Classification: **`LOAD`**, not a code error.
**The correct response was to remove the content pipeline, not to fight it** —
because for a headless simulation you need meshes *in memory*, and `OBJFile`
reads an `.obj` into memory with no pipeline involved.

**`MonoGame.Framework.Pipeline` does not exist as a 3.8 package.** I guessed the
name, `dotnet add package` hit the network timeout, and the correct move turned
out to be to ask a different question: *which of these files actually need the
pipeline?* **Only the importer and the writer do. `OBJFile` never did.**

## The decisive architectural fact

```
files touching GraphicsDevice / SpriteBatch / Texture2D :   5
total game .cs files                                     :  68
MonoGame references in Console.cs                        :  0
```

> **`Console.cs` is 55 lines of pure C# — `char[,]` and `byte[,]` — and 63 of 68
> source files never touch a graphics device.**

**The simulation is separable from the renderer, and the separation is already in
the codebase.** `Draw()` is a projection; `Update()` is the world. A headless
build that skips `Draw()` and serializes `console.Data` + `console.Color` needs no
GL context at all.

**This is the general-purpose/specific split Casey has been theorising about,
found by reading a stranger's game rather than argued for in the abstract: the
reusable unit here is the simulation, the specific part is the picture.**

## The remaining blocker, named precisely

**Textures.** `mgcb` never ran, so there are no `.xnb` files, and the rasterizer
samples textures per pixel to produce the 8-bit colour the console renders. Three
options, in order of preference:

1. **Get MGCB to run.** It now has no OBJ extension to trip over; the failure may
   have been the extension, not MGCB. **Cheapest if it works.**
2. **Read the 43 PNGs directly** into a CPU-side `Color[]` the rasterizer samples.
   Bypasses MGCB entirely and needs no `GraphicsDevice` — `Texture2D` does.
3. **Take colours from the scene graph** instead of the textures. Ground truth
   rather than a projection of it, consistent with the fallback in
   `ASCIIPOCALYPSE.md`.

**Then the input path.** The bot must drive the player, so the `Keyboard.GetState`
call site in `PlayerLogic.cs` needs an injectable seam — the same
`RenderContext`-one-designated-constructor discipline as `lau-git-render`.

## What this unlocks

**Both blocked lanes can now build the real thing instead of a reconstruction.**
`ASCII-CELLS` no longer has to settle for a screenshot-derived frame; it can
serialize a real one, which makes the colour-arm prediction a measurement rather
than an argument.
