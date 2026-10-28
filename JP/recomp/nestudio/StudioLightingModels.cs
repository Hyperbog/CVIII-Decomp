namespace NEStudio;

public sealed record StudioLightDetails(int Slot,int Angle,int Spread,int Width,
    int AnimationSpeed,int AnimationStrength,int StyleLink,string Group);
public sealed record StudioLightKit(int Slot,string Name,int Count)
{
    public string Label => $"{Slot+1:00}  {Name}  ({Count} emitters)";
}
public sealed record StudioGlobalStyle(int Slot,string Name,int Radius,
    int Energy,int Red,int Green,int Blue,int Shape,int Angle,int Spread,
    int Width,int Flicker,int AnimationSpeed,int AnimationStrength)
{
    public string Label => $"{Slot+1:00}  {Name}";
}
public sealed record StudioLightMask(int Slot,int X,int Y,int Width,int Height,
    int Opacity,int Softness)
{
    public string Label => $"Mask {Slot+1:00}  ({X},{Y}) {Width}×{Height}";
}
public sealed record StudioParticle(int Slot,string Name,int Kind,int X,int Y,
    int Width,int Height,int Density,int Speed,int Wind,int Opacity,int Size,
    int Red,int Green,int Blue,int LightLink,int Layer,int Glow)
{
    public string Label => $"{Slot+1:00}  {Name} · {new[]{"Dust","Embers","Fog","Ash","Snow","Rain","Fireflies"}[Math.Clamp(Kind,0,6)]}";
}
public sealed record StudioWeather(int Slot,string Name,int Kind,int Density,
    int Speed,int Wind,int Opacity,int Size,int Chance,int Period,int Seed,
    int Layer,int Red,int Green,int Blue)
{
    public string Label => $"{Slot+1:00}  {Name}";
}
public sealed record StudioLightingSnapshot(int Ambient,int SceneStrength,int SceneRed,
    int SceneGreen,int SceneBlue,int SkyStrength,int SkyRed,int SkyGreen,
    int SkyBlue,int SkyFacing,int Exposure,int Temperature,int Saturation,
    bool ParticlesEnabled,int ActiveWeather,int CascadeQuality,bool Enabled,
    uint RawRoom,IReadOnlyDictionary<int,StudioLightDetails> LightDetails,
    IReadOnlyList<StudioLightKit> Kits,IReadOnlyList<StudioGlobalStyle> Styles,
    IReadOnlyList<StudioLightMask> Masks,IReadOnlyList<StudioParticle> Particles,
    IReadOnlyList<StudioWeather> Weather);
