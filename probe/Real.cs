// Verbatim from ASCII_FPS/Mathg.cs:69 and ASCII_FPS/AsciiTexture.cs:33
using System;using System.Runtime.Serialization;using System.Reflection;
using Microsoft.Xna.Framework;
class Real {
  public static byte ColorTo8Bit(Vector3 c){        // Mathg.cs:69
    byte r=(byte)(Cl(c.X,0,0.9f)*8); byte g=(byte)(Cl(c.Y,0,0.9f)*8); byte b=(byte)(Cl(c.Z,0,0.8f)*4);
    return (byte)(r+(g<<3)+(b<<6));
  }
  static float Cl(float v,float a,float b)=>v<a?a:(v>b?b:v);
  const string FOG="@&#8x*,:. ";                    // Rasterizer.cs:22
  public static char Fog2(int i)=>FOG[i];
  public static int FogId(float z,float off)=>z<0?0:Math.Min((int)(Math.Pow(z,10)*FOG.Length+off),FOG.Length-1);
  // AsciiTexture.cs:35  -- verbatim indexing, private array injected by reflection
  public static Vector3 Sample(Vector3[,] colors, Vector2 uv)
    => colors[(int)(uv.X*256)&0xff,(int)(uv.Y*256)&0xff];
}
