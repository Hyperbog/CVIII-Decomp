using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using UserControl = System.Windows.Controls.UserControl;
using TextBox = System.Windows.Controls.TextBox;
using ListBox = System.Windows.Controls.ListBox;
using Button = System.Windows.Controls.Button;

namespace NEStudio;

/// <summary>
/// Native-feeling WPF lighting authoring. No overlay is drawn over the game.
/// A versioned C11/SDL thread remains the only owner of saved lighting state.
/// </summary>
public partial class LightingWorkbench : UserControl
{
    public Action<int,int,int,int,string?>? Send;
    public Action? EditRequested;
    public Action? PlayRequested;
    public Action<int>? LightSelected;
    private StudioScene? _scene;
    private int _selected=-1;
    private bool _refreshing;
    private bool _pendingEdit;
    private int _selectedKit=-1,_selectedStyle=-1,_selectedMask=-1;
    private int _selectedFx=-1,_selectedWeather=-1;
    private readonly Dictionary<string,string> _fingerprints=new();

    public LightingWorkbench()
    {
        InitializeComponent();
        Builtins.SelectedIndex=0;
        FxKind.SelectedIndex=0;
        WeatherTemplate.SelectedIndex=0;
    }

    private void Post(int op,int a=0,int b=0,int c=0,string? label=null)
    {
        if(_scene is null)
        {
            WorkStatus.Text="Attach a private native game before editing.";
            return;
        }
        if(!_scene.Editing && !_pendingEdit)
        {
            _pendingEdit=true;
            EditRequested?.Invoke();
        }
        Send?.Invoke(op,a,b,c,label);
        WorkStatus.Text="Editing live room 0x"+_scene.Room.ToString("X8")+
            " · Changes are undoable and saved by native engine";
    }
    private void PostSet(params (int Op,int A,int B,int C)[] changes)
    {
        foreach(var x in changes)Post(x.Op,x.A,x.B,x.C);
    }
    private static int Field(TextBox text,int min,int max,int fallback)
    {
        return int.TryParse(text.Text,out int v) && v>=min && v<=max?
            v:fallback;
    }
    private static bool GoodName(string text,int cap)
    {
        return text.Length>0 && text.Length<cap &&
            text.All(c=>c is >= ' ' and <= '~');
    }
    private void TextCommand(int operation,int a,string value,int cap)
    {
        if(!GoodName(value,cap))
        {
            WorkStatus.Text=$"Use a printable ASCII name (1–{cap-1} characters).";
            return;
        }
        Post(operation,a,0,0,value);
    }
    private static void RefreshList<T>(ListBox list,IEnumerable<T> source,
        string key,Dictionary<string,string> fingerprints,int selectedSlot,
        Func<T,int> slot)
    {
        var items=source.ToList();
        string fingerprint=string.Join("|",items.Select(x=>x is null?"":x.ToString()));
        if(fingerprints.TryGetValue(key,out string? prev) && prev==fingerprint)
            return;
        fingerprints[key]=fingerprint;
        list.ItemsSource=items;
        list.SelectedItem=items.FirstOrDefault(x=>slot(x)==selectedSlot);
    }
    private static void UpdateSlider(Slider control,int value)
    {
        if(!control.IsMouseCaptureWithin)control.Value=Math.Clamp(value,
            (int)control.Minimum,(int)control.Maximum);
    }
    private void UpdateLightList()
    {
        if(_scene is null)return;
        string term=Search.Text.Trim();
        IEnumerable<StudioLight> matches=_scene.Lights;
        if(term.Length>0)
            matches=matches.Where(l=>
                l.Name.Contains(term,StringComparison.OrdinalIgnoreCase) ||
                (_scene.Lighting.LightDetails.TryGetValue(l.Slot,out var d) &&
                 d.Group.Contains(term,StringComparison.OrdinalIgnoreCase)));
        RefreshList(LightList,matches,"lights:"+term,_fingerprints,_selected,l=>l.Slot);
    }
    public void UpdateScene(StudioScene scene,int selectedLight)
    {
        bool switched=_selected!=selectedLight;
        _scene=scene;_selected=selectedLight;
        if(scene.Editing)_pendingEdit=false;
        var lighting=scene.Lighting;
        _refreshing=true;
        try
        {
            UpdateLightList();
            StudioLight? current=scene.Lights.FirstOrDefault(l=>l.Slot==_selected);
            if(current is not null)
            {
                lighting.LightDetails.TryGetValue(_selected,out var details);
                SelectedName.Text=current.Label;
                if(switched)
                {
                    NameBox.Text=current.Name;
                    GroupBox.Text=details?.Group??"";
                }
                if(!WorldX.IsKeyboardFocusWithin)WorldX.Text=current.X.ToString();
                if(!WorldY.IsKeyboardFocusWithin)WorldY.Text=current.Y.ToString();
                UpdateSlider(Radius,current.Radius);UpdateSlider(Power,current.Power);
                UpdateSlider(Red,current.Red);UpdateSlider(Green,current.Green);
                UpdateSlider(Blue,current.Blue);
                ShapeBox.SelectedIndex=Math.Clamp(current.Shape,0,2);
                Flicker.SelectedIndex=Math.Clamp(current.Flicker,0,4);
                MuteBox.IsChecked=current.Muted!=0;
                if(details is not null)
                {
                    UpdateSlider(Angle,details.Angle);
                    UpdateSlider(Spread,details.Spread==0?30:details.Spread);
                    UpdateSlider(ShaftWidth,details.Width==0?32:details.Width);
                    UpdateSlider(Speed,details.AnimationSpeed);
                    UpdateSlider(Strength,details.AnimationStrength);
                }
            }
            else SelectedName.Text="Select a light in the viewport or list";
            EnableLighting.IsChecked=lighting.Enabled;
            RendererChoice.SelectedIndex=Math.Clamp(scene.Renderer,0,2);
            UpdateSlider(CascadeQuality,lighting.CascadeQuality);
            UpdateSlider(Ambient,lighting.SceneStrength);
            UpdateSlider(AmbientRed,lighting.SceneRed);
            UpdateSlider(AmbientGreen,lighting.SceneGreen);
            UpdateSlider(AmbientBlue,lighting.SceneBlue);
            UpdateSlider(SkyPower,lighting.SkyStrength);
            UpdateSlider(SkyR,lighting.SkyRed);UpdateSlider(SkyG,lighting.SkyGreen);
            UpdateSlider(SkyB,lighting.SkyBlue);
            SkyDirection.SelectedIndex=Math.Clamp(lighting.SkyFacing+1,0,2);
            UpdateSlider(Exposure,lighting.Exposure);
            UpdateSlider(Temperature,lighting.Temperature);
            UpdateSlider(Saturation,lighting.Saturation);
            FxEnabled.IsChecked=lighting.ParticlesEnabled;
            RefreshList(KitList,lighting.Kits,"kits",_fingerprints,_selectedKit,k=>k.Slot);
            RefreshList(StyleList,lighting.Styles,"styles",_fingerprints,_selectedStyle,g=>g.Slot);
            RefreshList(MaskList,lighting.Masks,"masks",_fingerprints,_selectedMask,m=>m.Slot);
            RefreshList(FxList,lighting.Particles,"fx",_fingerprints,_selectedFx,p=>p.Slot);
            RefreshList(WeatherList,lighting.Weather,"weather",_fingerprints,_selectedWeather,w=>w.Slot);
            WeatherStatus.Text=lighting.ActiveWeather<0?"Current room: no weather":
                $"Current room: weather slot {lighting.ActiveWeather}";
            if(lighting.Styles.FirstOrDefault(g=>g.Slot==_selectedStyle) is { } gs)
            {
                UpdateSlider(StyleRadius,gs.Radius);UpdateSlider(StylePower,gs.Energy);
                UpdateSlider(StyleRed,gs.Red);UpdateSlider(StyleGreen,gs.Green);
                UpdateSlider(StyleBlue,gs.Blue);
                StyleShape.SelectedIndex=Math.Clamp(gs.Shape,0,2);
                StyleFlicker.SelectedIndex=Math.Clamp(gs.Flicker,0,4);
                UpdateSlider(StyleAngle,gs.Angle);
                UpdateSlider(StyleSpread,gs.Spread==0?30:gs.Spread);
                UpdateSlider(StyleWidth,gs.Width==0?32:gs.Width);
                UpdateSlider(StyleSpeed,gs.AnimationSpeed);
                UpdateSlider(StyleStrength,gs.AnimationStrength);
            }
            if(lighting.Masks.FirstOrDefault(m=>m.Slot==_selectedMask) is { } mask)
            {
                UpdateSlider(MaskOpacity,mask.Opacity);UpdateSlider(MaskSoftness,mask.Softness);
                UpdateSlider(MaskWidth,mask.Width);UpdateSlider(MaskHeight,mask.Height);
                if(!MaskX.IsKeyboardFocusWithin)MaskX.Text=mask.X.ToString();
                if(!MaskY.IsKeyboardFocusWithin)MaskY.Text=mask.Y.ToString();
            }
            if(lighting.Particles.FirstOrDefault(p=>p.Slot==_selectedFx) is { } fx)
            {
                UpdateSlider(FxDensity,fx.Density);UpdateSlider(FxSpeed,fx.Speed);
                UpdateSlider(FxWind,fx.Wind);UpdateSlider(FxOpacity,fx.Opacity);
                UpdateSlider(FxSize,fx.Size);UpdateSlider(FxGlow,fx.Glow);
                UpdateSlider(FxWidth,fx.Width);UpdateSlider(FxHeight,fx.Height);
                UpdateSlider(FxRed,fx.Red);UpdateSlider(FxGreen,fx.Green);
                UpdateSlider(FxBlue,fx.Blue);
                FxLayer.SelectedIndex=Math.Clamp(fx.Layer,0,1);
                if(!FxWorldX.IsKeyboardFocusWithin)FxWorldX.Text=fx.X.ToString();
                if(!FxWorldY.IsKeyboardFocusWithin)FxWorldY.Text=fx.Y.ToString();
            }
            if(lighting.Weather.FirstOrDefault(w=>w.Slot==_selectedWeather) is { } weather)
            {
                UpdateSlider(WeatherDensity,weather.Density);
                UpdateSlider(WeatherSpeed,weather.Speed);
                UpdateSlider(WeatherWind,weather.Wind);
                UpdateSlider(WeatherOpacity,weather.Opacity);
                UpdateSlider(WeatherChance,weather.Chance);
                UpdateSlider(WeatherPeriod,weather.Period);
                UpdateSlider(WeatherSize,weather.Size);
                UpdateSlider(WeatherRed,weather.Red);
                UpdateSlider(WeatherGreen,weather.Green);
                UpdateSlider(WeatherBlue,weather.Blue);
                WeatherKind.SelectedIndex=Math.Clamp(weather.Kind,0,6);
                WeatherLayer.SelectedIndex=Math.Clamp(weather.Layer,0,1);
                if(!WeatherSeed.IsKeyboardFocusWithin)WeatherSeed.Text=weather.Seed.ToString();
            }
            WorkStatus.Text=scene.Editing?
                $"EDIT · room 0x{scene.Room:X8} · {scene.Lights.Count} lights · drag handles in viewport":
                "PLAY · click Edit / Pause to author effects";
        }
        finally {_refreshing=false;}
    }
    private void Edit_Click(object sender,RoutedEventArgs e)=>EditRequested?.Invoke();
    private void Play_Click(object sender,RoutedEventArgs e)=>PlayRequested?.Invoke();
    private void Undo_Click(object sender,RoutedEventArgs e)=>Post(8);
    private void Redo_Click(object sender,RoutedEventArgs e)=>Post(9);
    private void Search_Changed(object sender,TextChangedEventArgs e)
    {
        if(!IsLoaded || _scene is null)return;
        _refreshing=true;
        try{UpdateLightList();}finally{_refreshing=false;}
    }
    private void Light_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || LightList.SelectedItem is not StudioLight l)return;
        _selected=l.Slot;
        EditRequested?.Invoke();
        LightSelected?.Invoke(l.Slot);
    }
    private void LightSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || sender is not Slider slider || _selected<0)return;
        if(!int.TryParse(slider.Tag?.ToString(),out int property))return;
        Post(3,_selected);Post(4,property,(int)Math.Round(slider.Value));
    }
    private void SceneSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || sender is not Slider slider)return;
        var parts=slider.Tag?.ToString()?.Split(':');
        if(parts?.Length!=2 || !int.TryParse(parts[0],out int op) ||
           !int.TryParse(parts[1],out int property))return;
        Post(op,property,(int)Math.Round(slider.Value));
    }
    private void Shape_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || _selected<0 || ShapeBox.SelectedIndex<0)return;
        Post(3,_selected);Post(4,7,ShapeBox.SelectedIndex);
    }
    private void Flicker_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || _selected<0 || Flicker.SelectedIndex<0)return;
        Post(3,_selected);Post(4,12,Flicker.SelectedIndex);
    }
    private void Mute_Changed(object sender,RoutedEventArgs e)
    {
        if(_refreshing || _selected<0)return;
        Post(3,_selected);Post(4,11,MuteBox.IsChecked==true?1:0);
    }
    private void EnableLighting_Changed(object sender,RoutedEventArgs e)
    {
        if(_refreshing)return;
        Post(4,0,EnableLighting.IsChecked==true?1:0);
    }
    private void FxEnabled_Changed(object sender,RoutedEventArgs e)
    {
        if(_refreshing)return;
        Post(31,FxEnabled.IsChecked==true?1:0);
    }
    private void Renderer_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || RendererChoice.SelectedIndex<0)return;
        Post(10,RendererChoice.SelectedIndex);
    }
    private void Cascade_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || _scene is null)return;
        Post(11,(int)Math.Round(CascadeQuality.Value));
    }
    private void SkyDirection_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || SkyDirection.SelectedIndex<0)return;
        Post(22,4,SkyDirection.SelectedIndex-1);
    }
    private void Kit_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || KitList.SelectedItem is not StudioLightKit k)return;
        _selectedKit=k.Slot;KitSlot.Text=k.Slot.ToString();KitName.Text=k.Name;
    }
    private void Style_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || StyleList.SelectedItem is not StudioGlobalStyle g)return;
        _selectedStyle=g.Slot;StyleSlot.Text=g.Slot.ToString();StyleName.Text=g.Name;
    }
    private void Mask_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && MaskList.SelectedItem is StudioLightMask m)_selectedMask=m.Slot;
    }
    private void Fx_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || FxList.SelectedItem is not StudioParticle p)return;
        _selectedFx=p.Slot;FxName.Text=p.Name;
    }
    private void Weather_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(_refreshing || WeatherList.SelectedItem is not StudioWeather w)return;
        _selectedWeather=w.Slot;WeatherSlot.Text=w.Slot.ToString();WeatherName.Text=w.Name;
    }
    private void StyleSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || _selectedStyle<0 || sender is not Slider slider)return;
        if(int.TryParse(slider.Tag?.ToString(),out int property))
            Post(28,_selectedStyle,property,(int)Math.Round(slider.Value));
    }
    private void MaskSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || _selectedMask<0 || sender is not Slider slider)return;
        if(int.TryParse(slider.Tag?.ToString(),out int property))
            Post(30,_selectedMask,property,(int)Math.Round(slider.Value));
    }
    private void FxSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || _selectedFx<0 || sender is not Slider slider)return;
        if(int.TryParse(slider.Tag?.ToString(),out int property))
            Post(33,_selectedFx,property,(int)Math.Round(slider.Value));
    }
    private void StyleShape_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && _selectedStyle>=0 && StyleShape.SelectedIndex>=0)
            Post(28,_selectedStyle,7,StyleShape.SelectedIndex);
    }
    private void StyleFlicker_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && _selectedStyle>=0 && StyleFlicker.SelectedIndex>=0)
            Post(28,_selectedStyle,12,StyleFlicker.SelectedIndex);
    }
    private void FxLayer_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && _selectedFx>=0 && FxLayer.SelectedIndex>=0)
            Post(33,_selectedFx,14,FxLayer.SelectedIndex);
    }
    private void WeatherKind_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && _selectedWeather>=0 && WeatherKind.SelectedIndex>=0)
            Post(38,_selectedWeather,1,WeatherKind.SelectedIndex);
    }
    private void WeatherLayer_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(!_refreshing && _selectedWeather>=0 && WeatherLayer.SelectedIndex>=0)
            Post(38,_selectedWeather,10,WeatherLayer.SelectedIndex);
    }
    private void WeatherSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_refreshing || _selectedWeather<0 || sender is not Slider slider)return;
        if(int.TryParse(slider.Tag?.ToString(),out int property))
            Post(38,_selectedWeather,property,(int)Math.Round(slider.Value));
    }

    private void Action_Click(object sender,RoutedEventArgs e)
    {
        if(sender is not Button button)return;
        string tag=button.Tag?.ToString()??"";
        int kit=Field(KitSlot,0,11,_selectedKit<0?0:_selectedKit);
        int style=Field(StyleSlot,0,15,_selectedStyle<0?0:_selectedStyle);
        int weather=Field(WeatherSlot,0,7,_selectedWeather<0?0:_selectedWeather);
        switch(tag)
        {
            case "new-light":Post(5,128,120);break;
            case "duplicate":if(_selected>=0){Post(3,_selected);Post(6);}break;
            case "delete-light":if(_selected>=0){Post(3,_selected);Post(7);}break;
            case "copy":if(_selected>=0){Post(3,_selected);Post(42);}break;
            case "paste":Post(43);break;
            case "identity":
                if(_selected>=0)
                {
                    Post(3,_selected);
                    TextCommand(19,0,NameBox.Text,48);
                    TextCommand(20,0,GroupBox.Text.Length==0?"Ungrouped":GroupBox.Text,32);
                }
                break;
            case "move":
                if(_selected>=0)
                {
                    int x=Field(WorldX,0,65535,-1),y=Field(WorldY,0,479,-1);
                    if(x<0 || y<0){WorkStatus.Text="World X must be 0–65535 and Y 0–479.";break;}
                    Post(3,_selected);Post(4,13,x);Post(4,14,y);
                }
                break;
            case "warm":Color(255,167,74);break;
            case "cool":Color(150,196,255);break;
            case "white":Color(255,255,255);break;
            case "neutral-ambient":PostSet((21,1,255,0),(21,2,255,0),(21,3,255,0));break;
            case "daylight":Sky(32,204,224,255);break;
            case "moonlight":Sky(20,123,157,245);break;
            case "no-sky":Post(22,0,0);break;
            case "neutral-grade":PostSet((23,0,0,0),(23,1,0,0),(23,2,100,0));break;
            case "builtin":Post(13,Math.Max(0,Builtins.SelectedIndex),128,120);break;
            case "capture-kit":TextCommand(24,kit,KitName.Text,48);break;
            case "apply-kit":Post(25,kit);break;
            case "rename-kit":
                if(GoodName(KitName.Text,48))Post(39,1,kit,0,KitName.Text);
                else WorkStatus.Text="Kit name requires printable ASCII (1–47 characters).";
                break;
            case "clone-kit":
                {
                    int empty=Enumerable.Range(0,12)
                        .FirstOrDefault(i=>_scene?.Lighting.Kits.All(k=>k.Slot!=i)==true,-1);
                    if(empty<0){WorkStatus.Text="All 12 saved kit slots are occupied.";break;}
                    Post(39,2,kit,empty);
                    break;
                }
            case "delete-kit":Post(39,3,kit);break;
            case "capture-style":TextCommand(26,style,StyleName.Text,48);break;
            case "link-style":if(_selected>=0){Post(3,_selected);Post(27,style,0);}break;
            case "link-group":if(_selected>=0){Post(3,_selected);Post(27,style,1);}break;
            case "unlink-style":if(_selected>=0){Post(3,_selected);Post(27,-1,0);}break;
            case "new-mask":Post(29);break;
            case "delete-mask":if(_selectedMask>=0)Post(30,_selectedMask,0,0);break;
            case "move-mask":
                if(_selectedMask>=0)
                {
                    int x=Field(MaskX,0,65535,-1),y=Field(MaskY,0,479,-1);
                    if(x<0 || y<0){WorkStatus.Text="Mask coordinates must be valid world X/Y.";break;}
                    Post(30,_selectedMask,1,x);Post(30,_selectedMask,2,y);
                }
                break;
            case "new-fx":Post(32,Math.Max(0,FxKind.SelectedIndex));break;
            case "move-fx":
                if(_selectedFx>=0)
                {
                    int x=Field(FxWorldX,0,65535,-1),y=Field(FxWorldY,0,479,-1);
                    if(x<0 || y<0){WorkStatus.Text="FX coordinates must be valid world X/Y.";break;}
                    Post(33,_selectedFx,2,x);Post(33,_selectedFx,3,y);
                }
                break;
            case "clone-fx":if(_selectedFx>=0)Post(34,_selectedFx);break;
            case "delete-fx":if(_selectedFx>=0)Post(33,_selectedFx,0,0);break;
            case "rename-fx":if(_selectedFx>=0)TextCommand(41,_selectedFx,FxName.Text,48);break;
            case "attach-fx":if(_selectedFx>=0 && _selected>=0)Post(35,_selectedFx,_selected);break;
            case "detach-fx":if(_selectedFx>=0)Post(35,_selectedFx,-1);break;
            case "create-weather":Post(36,weather,Math.Max(0,WeatherTemplate.SelectedIndex));break;
            case "apply-weather":Post(37,weather);break;
            case "unlink-weather":Post(37,-1);break;
            case "rename-weather":TextCommand(40,weather,WeatherName.Text,48);break;
            case "set-weather-seed":
                if(_selectedWeather>=0)
                {
                    int seed=Field(WeatherSeed,0,65535,-1);
                    if(seed<0){WorkStatus.Text="Seed must be 0–65535.";break;}
                    Post(38,_selectedWeather,9,seed);
                }
                break;
        }
    }
    public bool TryShortcut(Key key)
    {
        switch(key)
        {
            case Key.Z:Post(8);return true;
            case Key.Y:Post(9);return true;
            case Key.D:
                if(_selected>=0){Post(3,_selected);Post(6);}
                return true;
            case Key.C:
                if(_selected>=0){Post(3,_selected);Post(42);}
                return true;
            case Key.V:Post(43);return true;
            default:return false;
        }
    }
    private void Color(int r,int g,int b)
    {
        if(_selected<0)return;
        Post(3,_selected);
        Post(4,4,r);Post(4,5,g);Post(4,6,b);
    }
    private void Sky(int power,int r,int g,int b)
    {
        Post(22,0,power);Post(22,1,r);Post(22,2,g);
        Post(22,3,b);Post(22,4,-1);
    }
}
