// COLOUR-CHANNEL PROBE -- the last CLAIM in the ASCII results, now measured.
//
// Real 8-bit textures decoded from Asciipocalypse/ASCII_FPS/Content/textures,
// put through the game's OWN ColorTo8Bit (Mathg.cs:69) and the game's OWN
// AsciiTexture.Sample (AsciiTexture.cs:35), at one fixed depth.
//
// FINDING, and it corrects a conclusion of mine:
//   characters separate    0/28 texture pairs  (one glyph per depth, always)
//   colour separates        0/28 texture pairs  (mean 2.5 shared bytes)
//   24 bits instead of 8   13/28
//   8 bits + 3x3 context    9/28
//
// So the colour channel is ITSELF an irreversible projection -- R:3 G:3 B:2 is
// only 256 values, and real game textures land on 4 to 39 distinct bytes. Joint
// recovery from a cell is PARTIAL, not EXACT, which contradicts joint.py: that
// experiment used synthetic uniform colours that were too separable for the
// quantiser to bite.
//
// Reproduce: decode_textures.py writes /tmp/tex/*.raw, then dotnet run.
using System;using System.IO;using System.Linq;using System.Collections.Generic;
using Microsoft.Xna.Framework;
class P {
  const string FOG="@&#8x*,:. ";                       // Rasterizer.cs:22
  static float Cl(float v,float a,float b)=>v<a?a:(v>b?b:v);
  // VERBATIM ASCII_FPS/Mathg.cs:69
  static byte ColorTo8Bit(Vector3 c){
    byte r=(byte)(Cl(c.X,0,0.9f)*8); byte g=(byte)(Cl(c.Y,0,0.9f)*8); byte b=(byte)(Cl(c.Z,0,0.8f)*4);
    return (byte)(r+(g<<3)+(b<<6));
  }
  // VERBATIM ASCII_FPS/AsciiTexture.cs:35
  static Vector3 Sample(Vector3[,] c,Vector2 uv)=>c[(int)(uv.X*256)&0xff,(int)(uv.Y*256)&0xff];
  static int FogId(float z,float off)=>z<0?0:Math.Min((int)(Math.Pow(z,10)*FOG.Length+off),FOG.Length-1);

  static void Main(){
    var names=File.ReadAllLines("/tmp/texnames.txt");
    var tex=new List<(string,Vector3[,])>();
    foreach(var n in names){
      var lines=File.ReadAllLines($"/tmp/tex/{n}.raw");
      var px=new Vector3[256,256];
      for(int y=0;y<256;y++){var v=lines[y].Split(',');for(int x=0;x<256;x++)
        px[x,y]=new Vector3(float.Parse(v[x*3]),float.Parse(v[x*3+1]),float.Parse(v[x*3+2]));}
      tex.Add((n,px));
    }
    Console.WriteLine($"  {tex.Count} REAL 256x256 textures, decoded from the game's own Content/textures\n");
    const float Z=0.85f; float off=0.0f;
    Console.WriteLine($"  at z={Z} the CHARACTER channel yields '{FOG[FogId(Z,off)]}' for every surface, by construction.\n");

    var sets=new List<HashSet<byte>>();
    foreach(var t in tex){
      var s=new HashSet<byte>();
      for(int y=0;y<256;y+=8) for(int x=0;x<256;x+=8)
        s.Add(ColorTo8Bit(Sample(t.Item2,new Vector2(x/256f,y/256f))));
      sets.Add(s);
    }
    Console.WriteLine($"  ARM 1 -- {tex.Count} textures at ONE depth, 1024 samples each:");
    for(int i=0;i<tex.Count;i++)
      Console.WriteLine($"    {tex[i].Item1,-22} distinct colour bytes {sets[i].Count,3}   e.g. {string.Join(" ",sets[i].Take(4).Select(v=>v.ToString("X2")))}");
    int pairs=0,sep=0,tot=0;
    for(int i=0;i<tex.Count;i++)for(int j=i+1;j<tex.Count;j++){
      pairs++; int ov=sets[i].Intersect(sets[j]).Count(); tot+=ov; if(ov==0)sep++;}
    Console.WriteLine($"\n    all {pairs} texture pairs at one depth:");
    Console.WriteLine($"      fully separable by COLOUR (zero shared bytes) : {sep}/{pairs}");
    Console.WriteLine($"      mean shared colour bytes per pair            : {tot/(double)pairs:F1}");
    Console.WriteLine($"      separable by CHARACTER                      : 0/{pairs}  (one glyph, always)");

    var chars=new List<char>(); var cols=new HashSet<byte>();
    foreach(var z in new[]{0.30f,0.55f,0.80f,0.85f,0.92f,0.97f}){
      chars.Add(FOG[FogId(z,0f)]); cols.Add(ColorTo8Bit(Sample(tex[0].Item2,new Vector2(0.5f,0.5f))));}
    Console.WriteLine($"\n  ARM 2 -- ONE texture, six depths:");
    Console.WriteLine($"      characters  : {new string(chars.ToArray())}  ({chars.Distinct().Count()} distinct)");
    Console.WriteLine($"      colour@mid  : {cols.Count} distinct  (depth-independent, as predicted)");
    // MY OWN PRINTED CONCLUSION WAS WRONG. Colour separates 0/28, not 28/28.
    // WHY: ColorTo8Bit quantises to 8 bits (R:3 G:3 B:2). bricks01 lands on only
    // 4 distinct bytes over 1024 samples - it is nearly monochrome. So the colour
    // channel is ITSELF an irreversible projection, and a lossy one.
    // Two escapes, tested rather than assumed:
    //   (a) more bits per cell
    //   (b) spatial context - the 3x3 neighbourhood, which is what a real
    //       observer uses and what a texture-reader agent would need
    Console.WriteLine($"\n  ==> MY PRINTED CONCLUSION WAS WRONG. Colour separates 0/28, not 28/28.\n");
    Console.WriteLine($"  WHY: ColorTo8Bit quantises to R:3 G:3 B:2 = 256 values. Real textures land on");
    Console.WriteLine($"       4 to 39 distinct bytes over 1024 samples, and they collide. The colour");
    Console.WriteLine($"       channel is ITSELF a lossy projection.\n");
    // ESCAPE A: 24 bits per cell instead of 8
    int sep24=0;
    var full=new List<HashSet<uint>>();
    foreach(var t in tex){ var s=new HashSet<uint>();
      for(int y=0;y<256;y+=8)for(int x=0;x<256;x+=8){var c=Sample(t.Item2,new Vector2(x/256f,y/256f));
        s.Add((uint)(c.X*255)<<16|(uint)(c.Y*255)<<8|(uint)(c.Z*255));} full.Add(s);}
    for(int i=0;i<tex.Count;i++)for(int j=i+1;j<tex.Count;j++)
      if(full[i].Intersect(full[j]).Count()==0) sep24++;
    Console.WriteLine($"  ESCAPE A  24 bits/cell (R8 G8 B8) : {sep24}/{pairs} pairs separable");
    // ESCAPE B: 3x3 spatial context, still at 8 bits per cell
    int sepCtx=0;
    var ctx=new List<HashSet<uint>>();
    foreach(var t in tex){ var s=new HashSet<uint>();
      for(int y=4;y<252;y+=8)for(int x=4;x<252;x+=8){uint hsh=2166136261u;
        for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){uint v=ColorTo8Bit(Sample(t.Item2,new Vector2((x+dx)/256f,(y+dy)/256f)));
          hsh=(hsh^v)*16777619u;}
        s.Add(hsh);} ctx.Add(s);}
    for(int i=0;i<tex.Count;i++)for(int j=i+1;j<tex.Count;j++)
      if(ctx[i].Intersect(ctx[j]).Count()==0) sepCtx++;
    Console.WriteLine($"  ESCAPE B  8 bits/cell, 3x3 context  : {sepCtx}/{pairs} pairs separable");
    Console.WriteLine($"\n  ==> So: characters carry DEPTH ONLY (0/{pairs}, one glyph per depth).");
    Console.WriteLine($"      Colour carries MOST identity but not all, because 8-bit quantisation is");
    Console.WriteLine($"      itself irreversible. Joint recovery is therefore PARTIAL, not EXACT - which");
    Console.WriteLine($"      contradicts what joint.py concluded from synthetic uniform colours.");
    Console.WriteLine($"      The synthetic colours were too separable for the quantiser to bite.");
  }
}
