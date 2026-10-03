using System;using System.Runtime.Serialization;using System.Reflection;
using Microsoft.Xna.Framework;

class P {
  // VERBATIM from Rasterizer.cs:22,36,129-131
  const string fogString = "@&#8x*,:. ";
  static int FogId(float z, float off){
    return z < 0 ? 0 : Math.Min((int)(Math.Pow(z,10)*fogString.Length + off), fogString.Length-1);
  }
  static void Main(){
    // 1. real Console type, from the game
    var con = new ASCII_FPS.Console(9, 3);
    Console.WriteLine($"real Console: {con.Width}x{con.Height}, Data type {con.Data.GetType().Name}, Color {con.Color.GetType().Name}");

    // 2. real AsciiTexture.Sample via an uninitialized object + injected array.
    //    Proves Sample() needs no GraphicsDevice -- it is a pure array read.
    var at = (ASCII_FPS.AsciiTexture)FormatterServices.GetUninitializedObject(typeof(ASCII_FPS.AsciiTexture));
    var field = typeof(ASCII_FPS.AsciiTexture).GetField("colors", BindingFlags.NonPublic|BindingFlags.Instance);
    var arr = new Vector3[256,256];
    for(int i=0;i<256;i++) for(int j=0;j<256;j++) arr[i,j]=new Vector3(0.25f,0.5f,0.75f);
    field.SetValue(at, arr);
    var s = at.Sample(new Vector2(0.5f,0.5f));
    Console.WriteLine($"real Sample() headless: ({s.X},{s.Y},{s.Z})  <- no GraphicsDevice, no Texture2D, no .xnb");

    // 3. the real offset RNG, drawn ONCE per cell as the constructor does
    var rnd = new Random();               // UNSEEDED, exactly as Rasterizer.cs:26
    var off = new float[9,3];
    for(int i=0;i<9;i++) for(int j=0;j<3;j++) off[i,j]=(float)rnd.NextDouble()-0.5f;
    Console.WriteLine($"real offset[0,0] = {off[0,0]:F6}  (one draw per cell, never redrawn)");

    // 4. THE CLAIM UNDER TEST: what fraction of uniform depth in [0,1] reads '@'?
    int n=200000, at_ch=0; var rnd2=new Random(7);
    for(int k=0;k<n;k++){ double z=rnd2.NextDouble(); if(FogId((float)z,0f)=='@') at_ch++; }
    Console.WriteLine($"REAL C#: uniform z in [0,1] -> '@' in {at_ch*100.0/n:F2}% of cells");

    // 5. the same, in REAL C#, with the real per-cell offsets
    int at_real=0; var rnd3=new Random(7);
    for(int k=0;k<n;k++){ double z=rnd3.NextDouble(); float o=(float)rnd3.NextDouble()-0.5f;
      if(FogId((float)z,o)=='@') at_real++; }
    Console.WriteLine($"REAL C#: same, with real dither  -> '@' in {at_real*100.0/n:F2}%");

    // 6. glyph histogram
    var hist=new int[10]; var rnd4=new Random(7);
    for(int k=0;k<n;k++){ double z=rnd4.NextDouble(); hist[FogId((float)z,0f)]++; }
    Console.Write("REAL C# glyph occupancy: ");
    for(int i=0;i<10;i++) Console.Write($"{fogString[i]}={hist[i]*100.0/n:F1}%  ");
    Console.WriteLine();
  }
}
