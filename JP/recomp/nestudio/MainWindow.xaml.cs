using Microsoft.Win32;
using System.IO;
using System.ComponentModel;
using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Threading;
using WinForms = System.Windows.Forms;

namespace NEStudio;

public partial class MainWindow : Window
{
    private StudioProject _project=StudioProject.Create();
    private string? _path;
    private readonly NativeGameHost _game=new();
    private StudioBridge? _bridge;
    private StudioScene? _scene;
    private readonly DispatcherTimer _poll=new(){ Interval=TimeSpan.FromMilliseconds(33) };
    private readonly Queue<(int Op,int A,int B,int C)> _commands=new();
    private bool _changing;
    private bool _dirty;
    private int _selectedLight=-1;
    private string _fingerprint="";
    private string _spriteFingerprint="";
    private StudioSpriteGroup? _sprite;
    private StudioDialogue? _dialogue;
    private string _language="en";
    // User-local acceptance evidence; no ROM bytes or project assets are logged.
    private readonly string _acceptanceLogPath=Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "NEStudio","Acceptance",
        $"session-{DateTime.Now:yyyyMMdd-HHmmss}-{Guid.NewGuid():N}.log");
    private int _lastNativePid;
    private int _lastNativeFrame=-1;
    private int _lastAck;
    private int _lastSentOperation;
    private DateTime _lastFrameAdvanceUtc;
    private bool _frameProgressLogged;
    private bool _frameDelayLogged;
    private bool _snapshotLogged;
    private bool _lightEditLogged;
    private bool _bridgeWaitLogged;
    private bool _captureGameKeys;
    private int _gameKeyBits;
    // Matches SDL SCANCODE_UP/DOWN/LEFT/RIGHT/Z/X/RETURN/BACKSLASH
    // in the owner-private v1 session input header.
    private static int GameBit(Key key) => key switch
    {
        Key.Up=>1,Key.Down=>2,Key.Left=>4,Key.Right=>8,
        Key.Z=>16,Key.X=>32,Key.Enter=>64,Key.Oem5=>128,
        _=>0
    };
    public MainWindow()
    {
        InitializeComponent();
        _poll.Tick+=Poll_Tick;
        PreviewKeyDown+=Hotkeys;
        PreviewKeyUp+=GameKeyUp;
        Deactivated+=(sender,args)=>ReleaseGameKeys();
    }
    private void Window_Loaded(object sender,RoutedEventArgs e)
    {
        var panel=new WinForms.Panel{Dock=WinForms.DockStyle.Fill};
        ViewportHost.Child=panel;
        _game.AttachPanel(panel);
        _project.GameExecutable=FindGame();
        _changing=true;
        LanguageCombo.SelectedIndex=0;
        SpriteLayerCombo.SelectedIndex=1;
        RendererCombo.SelectedIndex=0;
        FlickerCombo.SelectedIndex=0;
        _changing=false;
        string[] args=Environment.GetCommandLineArgs();
        if(args.Length>1 && File.Exists(args[1]))
        {
            try { Load(args[1]); }
            catch(Exception ex){Error("Opening project",ex);}
        }
        else RefreshProject();
        _poll.Start();
        Log("Editor initialized. Open a .nestudio project or create one.");
        Log("Runtime is a separate native recomp process; no ROM assets enter project files.");
        Log("Acceptance log: "+_acceptanceLogPath);
    }
    private static string FindGame()
    {
        string basePath=AppContext.BaseDirectory;
        string[] guesses={
            Path.Combine(basePath,"jp_akumajou_densetsu.exe"),
            Path.GetFullPath(Path.Combine(basePath,"..","jp_akumajou_densetsu.exe")),
            Path.GetFullPath(Path.Combine(basePath,"..","AlphaCandidate","jp_akumajou_densetsu.exe"))
        };
        return guesses.FirstOrDefault(File.Exists)??"";
    }
    private void Window_Closing(object? sender,CancelEventArgs e)
    {
        if(!ConfirmDiscard()){e.Cancel=true;return;}
        _poll.Stop();
        ReleaseGameKeys();
        _bridge?.Dispose();_bridge=null;
        _game.Dispose();
    }
    private void Poll_Tick(object? sender,EventArgs args)
    {
        try
        {
            if(_game.IsRunning)
            {
                // The executable launched by a .bat is a CHILD of cmd.exe.
                // The unique game-session bridge publishes its actual PID.
                if(_bridge is null)
                {
                    _bridge=StudioBridge.TryOpen(_game.Session);
                    if(_bridge is not null)
                    {
                        _lastFrameAdvanceUtc=DateTime.UtcNow;
                        Log("Connected to live C11 Enhanced scene bridge.");
                    }
                }
                if(_bridge is not null)
                {
                    int nativePid=_bridge.GameProcessId;
                    _game.SetNativeProcessId(nativePid);
                    if(nativePid>0 && nativePid!=_lastNativePid)
                    {
                        _lastNativePid=nativePid;
                        Log($"Native game PID confirmed by session bridge: {nativePid}.");
                    }
                    int frame=_bridge.GameFrame;
                    if(_lastNativeFrame<0)
                    {
                        _lastNativeFrame=frame;
                        _lastFrameAdvanceUtc=DateTime.UtcNow;
                    }
                    else if(frame!=_lastNativeFrame)
                    {
                        _lastNativeFrame=frame;
                        _lastFrameAdvanceUtc=DateTime.UtcNow;
                        _frameDelayLogged=false;
                        if(!_frameProgressLogged)
                        {
                            _frameProgressLogged=true;
                            Log("Native SDL host frame counter is advancing.");
                        }
                    }
                    else if(!_frameDelayLogged &&
                            _scene?.Editing!=true &&
                            DateTime.UtcNow-_lastFrameAdvanceUtc>TimeSpan.FromSeconds(5))
                    {
                        _frameDelayLogged=true;
                        Log("Native frame counter unchanged for 5 seconds; game may be paused or stalled.");
                    }
                    if(!_game.IsEmbedded && _game.TryEmbed())
                    {
                        ViewportHint.Visibility=Visibility.Collapsed;
                        Log($"Embedded native SDL2 viewport (PID {_game.ProcessId}, Win32 parent verified; panel {ViewportHost.ActualWidth:0}x{ViewportHost.ActualHeight:0}).");
                    }
                }
                if(!_game.IsEmbedded && !_game.IsBatchLauncher &&
                   _game.TryEmbed())
                {
                    ViewportHint.Visibility=Visibility.Collapsed;
                    Log("Embedded native SDL2 game viewport.");
                }
                if(_bridge is not null)
                {
                    // Read the previous acknowledgement before dispatching the
                    // next command, so acceptance logs name the correct action.
                    StudioScene? snapshot=_bridge.Poll();
                    int ack=_bridge.AcknowledgedSequence;
                    if(ack!=_lastAck)
                    {
                        _lastAck=ack;
                        if(_bridge.LastResult==0)
                            Log($"Native editor command rejected (op {_lastSentOperation}).");
                        else if(_lastSentOperation is 1 or 2 or 13 or 14)
                            Log($"Native editor command acknowledged (op {_lastSentOperation}).");
                        else if(_lastSentOperation==4 && !_lightEditLogged)
                        {
                            _lightEditLogged=true;
                            Log("Native lighting property edit acknowledged.");
                        }
                    }
                    if(snapshot is not null)
                    {
                        if(!_snapshotLogged)
                        {
                            _snapshotLogged=true;
                            Log($"Live scene snapshot received (room 0x{snapshot.Room:X8}, {snapshot.Lights.Count} lights, {snapshot.Sprites.Count} OAM slots).");
                        }
                        UpdateScene(snapshot);
                    }
                    if(_commands.Count>0)
                    {
                        var cmd=_commands.Peek();
                        if(_bridge.TryCommand(cmd.Op,cmd.A,cmd.B,cmd.C))
                        {
                            _lastSentOperation=cmd.Op;
                            _commands.Dequeue();
                        }
                    }
                }
                if(_bridge is null && _game.StartupElapsed>TimeSpan.FromSeconds(20))
                {
                    ConnectionLabel.Text="BRIDGE WAITING · Check game launcher";
                    if(!_bridgeWaitLogged)
                    {
                        _bridgeWaitLogged=true;
                        Log("No NEStudio native bridge after 20 seconds. If the game window is already open separately, an older Alpha build may have been reused. Run the private NEStudio builder, then select NEStudio-Preview\\AlphaCandidate\\Launch-NEStudio-Game.bat.");
                    }
                }
                else ConnectionLabel.Text=_bridge is null?
                    "GAME RUNNING · Bridge connecting":
                    _scene?.Editing==true?"LIVE · EDIT MODE / PAUSED":"LIVE · PLAYING";
                return;
            }
            // Session is the definitive launch marker, including an EXE
            // that exits before its native bridge or SDL window appears.
            if(!string.IsNullOrEmpty(_game.Session))
            {
                bool wasBatchLauncher=_game.IsBatchLauncher;
                ReleaseGameKeys();
                _bridge?.Dispose();_bridge=null;_scene=null;
                _commands.Clear();_fingerprint="";
                ViewportHint.Visibility=Visibility.Visible;
                ConnectionLabel.Text="OFFLINE · Game stopped";
                Log(wasBatchLauncher?
                    "Launcher exited without a connected native SDL game. A BAT that only builds or starts another emulator does not provide NEStudio's C11 bridge.":
                    "Game stopped; saved NEStudio project content remains available.");
                // Release the launcher handle and reset the session once;
                // otherwise the same failure is logged every polling tick.
                _game.Stop();
            }
        }
        catch(Exception ex)
        {
            ConnectionLabel.Text="RUNTIME ERROR";
            Log(ex.Message);
        }
    }
    private void UpdateScene(StudioScene scene)
    {
        _scene=scene;
        // A native viewport handle click changes the authoritative game
        // selection. Follow it unless the editor has already queued a new
        // scene-tree selection that has not yet reached the native thread.
        if(!_commands.Any(cmd=>cmd.Op==3))
            _selectedLight=scene.Selected;
        var spriteFingerprint=string.Join("|",scene.Sprites.Select(sp=>
            $"{sp.Slot}:{sp.X}:{sp.Y}:{sp.Tile}:{sp.Attribute}"));
        if(spriteFingerprint!=_spriteFingerprint)
        {
            _spriteFingerprint=spriteFingerprint;
            LiveSpritesList.ItemsSource=scene.Sprites.Select(sp=>sp.Label).ToList();
        }
        RoomLabel.Text=$"Room 0x{scene.Room:X8} · {scene.Lights.Count} live light(s)";
        var fingerprint=scene.Room+"|"+_selectedLight+"|"+
            string.Join("|",scene.Lights.Select(l=>
                $"{l.Slot}:{l.Name}:{l.X}:{l.Y}"));
        if(fingerprint!=_fingerprint)
        {
            _fingerprint=fingerprint;
            RebuildSceneTree();
        }
        StudioLight? selected=scene.Lights.FirstOrDefault(l=>l.Slot==_selectedLight);
        _changing=true;
        if(selected is not null)
        {
            LightName.Text=$"{selected.Name} · world ({selected.X},{selected.Y})";
            LightRadius.Value=selected.Radius;
            LightPower.Value=selected.Power;
            LightRed.Value=selected.Red;
            LightGreen.Value=selected.Green;
            LightBlue.Value=selected.Blue;
            FlickerCombo.SelectedIndex=Math.Clamp(selected.Flicker,0,4);
            SelectionLabel.Text=selected.Label;
        }
        else
        {
            LightName.Text="Select or drag a light in the game viewport";
            SelectionLabel.Text="No light selected";
        }
        RendererCombo.SelectedIndex=Math.Clamp(scene.Renderer,0,2);
        _changing=false;
    }
    private void RebuildSceneTree()
    {
        _changing=true;
        SceneTree.Items.Clear();
        var root=new TreeViewItem
        {
            Header=_scene is null?"Project Scene":$"Live Room 0x{_scene.Room:X8}",
            IsExpanded=true
        };
        var lights=new TreeViewItem{Header="Lighting",IsExpanded=true};
        if(_scene is not null)
            foreach(StudioLight light in _scene.Lights)
                lights.Items.Add(new TreeViewItem{
                    Header=light.Label,Tag=light,
                    IsSelected=light.Slot==_selectedLight
                });
        root.Items.Add(lights);
        var sprites=new TreeViewItem{Header="Sprite Groups",IsExpanded=false};
        foreach(StudioSpriteGroup group in _project.SpriteGroups)
            sprites.Items.Add(new TreeViewItem{Header=group.Name,Tag=group});
        root.Items.Add(sprites);
        var dialogue=new TreeViewItem{Header="Dialogue / Localization",IsExpanded=false};
        foreach(StudioDialogue entry in _project.Dialogues)
            dialogue.Items.Add(new TreeViewItem{Header=entry.Id,Tag=entry});
        root.Items.Add(dialogue);
        root.Items.Add(new TreeViewItem{Header="Particle FX / Weather (native Lighting Studio)"});
        root.Items.Add(new TreeViewItem{Header="Scene Events / Timeline"});
        SceneTree.Items.Add(root);
        _changing=false;
    }
    private void SceneTree_SelectedItemChanged(object sender,
                                               RoutedPropertyChangedEventArgs<object> e)
    {
        if(_changing || e.NewValue is not TreeViewItem item)return;
        switch(item.Tag)
        {
            case StudioLight light:
                _selectedLight=light.Slot;
                Queue(3,light.Slot);
                SelectionLabel.Text=light.Label;
                break;
            case StudioSpriteGroup sprite:
                SpriteList.SelectedItem=sprite;
                SelectionLabel.Text=sprite.Name;
                break;
            case StudioDialogue dialogue:
                DialogueList.SelectedItem=dialogue;
                SelectionLabel.Text=dialogue.Id;
                break;
        }
    }
    private void Queue(int op,int a=0,int b=0,int c=0)
    {
        if(!_game.IsRunning)
        {
            Status("Start the game to use live editor controls.");
            return;
        }
        /* Continuous editor sliders must stay live, not accumulate hundreds
         * of stale property commands during a drag. Preserve non-property
         * operations in order and collapse superseded values. */
        if(op==1 && (_scene?.Editing==true || _commands.Any(x=>x.Op==1)))
            return;
        if(op==3 && _scene?.Selected==a &&
           !_commands.Any(x=>x.Op==3 && x.A!=a))
            return;
        if(op==4)
        {
            var pending=_commands.Where(x=>!(x.Op==4 && x.A==a)).ToArray();
            _commands.Clear();
            foreach(var item in pending)_commands.Enqueue(item);
        }
        if(_commands.Count>=128)
        {
            Status("Editor command queue is full; retry the change.");
            return;
        }
        _commands.Enqueue((op,a,b,c));
    }
    private void Run_Click(object sender,RoutedEventArgs e)
    {
        try
        {
            if(_game.IsRunning){Status("Game is already running.");return;}
            string path=ResolveGame();
            if(!File.Exists(path))
            {
                ChooseGame_Click(sender,e);
                path=ResolveGame();
            }
            if(!File.Exists(path))return;
            ReleaseGameKeys();
            _game.Start(path);
            _lastNativePid=0;_lastNativeFrame=-1;_lastAck=0;
            _lastSentOperation=0;_frameProgressLogged=false;
            _frameDelayLogged=false;_snapshotLogged=false;_lightEditLogged=false;
            _bridgeWaitLogged=false;
            _lastFrameAdvanceUtc=DateTime.UtcNow;
            _fingerprint="";
            Status("Launching game in embedded viewport.");
            Log($"Launched {Path.GetFileName(path)} (owner-local {(_game.IsBatchLauncher?"BAT/CMD launcher":"native executable")}).");
        }
        catch(Exception ex){Error("Starting game",ex);}
    }
    private string ResolveGame()
    {
        if(Path.IsPathRooted(_project.GameExecutable))
            return _project.GameExecutable;
        string root=_path is null?
            AppContext.BaseDirectory:Path.GetDirectoryName(_path)!;
        return Path.GetFullPath(Path.Combine(root,_project.GameExecutable));
    }
    private void Stop_Click(object sender,RoutedEventArgs e)
    {
        ReleaseGameKeys();
        _bridge?.Dispose();_bridge=null;
        _game.Stop();
        _scene=null;_commands.Clear();
        _fingerprint="";
        ViewportHint.Visibility=Visibility.Visible;
        ConnectionLabel.Text="OFFLINE · Game stopped";
        Status("Stopped editor-owned game process.");
    }
    private void Pause_Click(object sender,RoutedEventArgs e)
    {
        ReleaseGameKeys();
        Queue(1);Status("Entering live editing: original game simulation pauses.");
    }
    private void Play_Click(object sender,RoutedEventArgs e)
    {
        Queue(2);
        CaptureGameKeys();
    }
    private void FocusGame_Click(object sender,RoutedEventArgs e)
    {
        if(_captureGameKeys)ReleaseGameKeys();
        else CaptureGameKeys();
    }
    private void CaptureGameKeys()
    {
        if(_bridge is null || !_game.IsEmbedded)
        {
            Status("Attach a bridge-enabled native game before capturing controls.");
            return;
        }
        _gameKeyBits=0;
        _captureGameKeys=_bridge.SetInputState(0,true);
        GameInputButton.Content=_captureGameKeys?"Release Keys":"Capture Keys";
        if(_captureGameKeys)
        {
            Focus();
            Keyboard.Focus(this);
            Status("GAME CONTROLS CAPTURED — arrows / Z / X / Enter / Backslash. Esc releases.");
            Log("NEStudio keyboard input capture enabled (native SDL frame mapping).");
        }
        else Status("Unable to enable keyboard capture on native session.");
    }
    private void ReleaseGameKeys()
    {
        bool hadCapture=_captureGameKeys;
        _captureGameKeys=false;
        _gameKeyBits=0;
        _bridge?.SetInputState(0,false);
        GameInputButton.Content="Capture Keys";
        if(hadCapture)Status("Game keys released. Click Capture Keys or Play to control the game.");
    }
    private void GameKeyUp(object sender,System.Windows.Input.KeyEventArgs e)
    {
        if(!_captureGameKeys)return;
        int bit=GameBit(e.Key);
        if(bit==0)return;
        _gameKeyBits&=~bit;
        _bridge?.SetInputState(_gameKeyBits,true);
        e.Handled=true;
    }
    private void Candle_Click(object sender,RoutedEventArgs e)
    {
        Queue(1);Queue(13,0,128,120);Status("Placing Candle in live view center.");
    }
    private void Torch_Click(object sender,RoutedEventArgs e)
    {
        Queue(1);Queue(13,1,128,120);Status("Placing Torch in live view center.");
    }
    private void Duplicate_Click(object sender,RoutedEventArgs e)
    {
        Queue(1);if(_selectedLight>=0)Queue(3,_selectedLight);
        Queue(6);
    }
    private void DeleteLight_Click(object sender,RoutedEventArgs e)
    {
        if(_selectedLight<0)return;
        Queue(1);Queue(3,_selectedLight);Queue(7);
        _selectedLight=-1;
    }
    private void Undo_Click(object sender,RoutedEventArgs e){Queue(8);}
    private void Redo_Click(object sender,RoutedEventArgs e){Queue(9);}
    private void LightSlider_Changed(object sender,RoutedPropertyChangedEventArgs<double> e)
    {
        if(_changing || sender is not Slider slider || _selectedLight<0 ||
           slider.Tag is not string field || !int.TryParse(field,out int property))
            return;
        Queue(1);Queue(3,_selectedLight);
        Queue(4,property,(int)Math.Round(slider.Value));
    }
    private void FlickerCombo_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_changing || _selectedLight<0 || FlickerCombo.SelectedIndex<0)return;
        Queue(1);Queue(3,_selectedLight);Queue(4,12,FlickerCombo.SelectedIndex);
    }
    private void RendererCombo_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_changing || RendererCombo.SelectedIndex<0)return;
        Queue(10,RendererCombo.SelectedIndex);
    }
    private void NewProject_Click(object sender,RoutedEventArgs e)
    {
        if(!ConfirmDiscard())return;
        _project=StudioProject.Create();
        _project.GameExecutable=_game.IsRunning?_project.GameExecutable:FindGame();
        _path=null;_dirty=false;
        RefreshProject();
        Status("New NEStudio project.");
    }
    private bool ConfirmDiscard()
    {
        if(!_dirty)return true;
        return System.Windows.MessageBox.Show("Discard unsaved NEStudio project changes?",
                "Unsaved project",MessageBoxButton.YesNo,MessageBoxImage.Warning)
               ==MessageBoxResult.Yes;
    }
    private void OpenProject_Click(object sender,RoutedEventArgs e)
    {
        if(!ConfirmDiscard())return;
        var dlg=new Microsoft.Win32.OpenFileDialog
        {
            Filter="NEStudio Project (*.nestudio)|*.nestudio",
            CheckFileExists=true
        };
        if(dlg.ShowDialog()==true)
        {
            try{Load(dlg.FileName);}
            catch(Exception ex){Error("Opening project",ex);}
        }
    }
    private void Load(string path)
    {
        _project=StudioProjectFile.Load(path);
        _path=Path.GetFullPath(path);
        _dirty=false;
        RefreshProject();
        Log("Opened "+_path);
        Status("Project loaded.");
    }
    private void SaveProject_Click(object sender,RoutedEventArgs e)=>Save(false);
    private void SaveAs_Click(object sender,RoutedEventArgs e)=>Save(true);
    private void Save(bool choose)
    {
        try
        {
            if(_path is null || choose)
            {
                var dlg=new Microsoft.Win32.SaveFileDialog
                {
                    Filter="NEStudio Project (*.nestudio)|*.nestudio",
                    DefaultExt=".nestudio",
                    AddExtension=true,
                    FileName=_path is null?"EnhancedProject.nestudio":Path.GetFileName(_path)
                };
                if(dlg.ShowDialog()!=true)return;
                _path=dlg.FileName;
            }
            StudioProjectFile.Save(_project,_path);
            _dirty=false;
            ProjectLabel.Text=_project.Name;
            Title=$"NEStudio — {_project.Name}";
            Queue(14); // flush game's current lighting config independently
            Status("Saved project and requested native lighting config save.");
            Log("Saved "+_path);
        }
        catch(Exception ex){Error("Saving project",ex);}
    }
    private void ChooseGame_Click(object sender,RoutedEventArgs e)
    {
        var dlg=new Microsoft.Win32.OpenFileDialog
        {
            Filter="Game executable or launcher (*.exe;*.bat;*.cmd)|*.exe;*.bat;*.cmd|Native game (*.exe)|*.exe|Windows launcher (*.bat;*.cmd)|*.bat;*.cmd",
            CheckFileExists=true,
            Title="Select the native Enhanced game .exe or the .bat/.cmd that launches it"
        };
        if(dlg.ShowDialog()==true)
        {
            string ext=Path.GetExtension(dlg.FileName).ToLowerInvariant();
            if(ext is not (".exe" or ".bat" or ".cmd"))
            {
                System.Windows.MessageBox.Show("Select a game executable or a Windows game launcher.",
                                "NEStudio",MessageBoxButton.OK,MessageBoxImage.Warning);
                return;
            }
            _project.GameExecutable=dlg.FileName;
            Dirty();Status("Game executable linked to this NEStudio project.");
        }
    }
    private void RefreshProject()
    {
        ProjectLabel.Text=_project.Name+(_dirty?" *":"");
        SpriteList.ItemsSource=null;SpriteList.ItemsSource=_project.SpriteGroups;
        DialogueList.ItemsSource=null;DialogueList.ItemsSource=_project.Dialogues;
        TimelineList.ItemsSource=null;TimelineList.ItemsSource=_project.Events;
        AssetList.ItemsSource=null;AssetList.ItemsSource=_project.Assets;
        RebuildSceneTree();
    }
    private void Dirty()
    {
        if(_changing)return;
        _dirty=true;
        ProjectLabel.Text=_project.Name+" *";
    }
    private void AddSpriteGroup_Click(object sender,RoutedEventArgs e)
    {
        var group=new StudioSpriteGroup{Name="Layer "+(_project.SpriteGroups.Count+1)};
        _project.SpriteGroups.Add(group);Dirty();RefreshProject();
        SpriteList.SelectedItem=group;
    }
    private void RemoveSpriteGroup_Click(object sender,RoutedEventArgs e)
    {
        if(_sprite is null)return;
        _project.SpriteGroups.Remove(_sprite);_sprite=null;
        Dirty();RefreshProject();
    }
    private void SpriteList_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(SpriteList.SelectedItem is not StudioSpriteGroup group)return;
        _sprite=group;_changing=true;
        SpriteName.Text=group.Name;
        SpriteLayerCombo.SelectedIndex=group.Layer switch
        {
            "Behind Game"=>0,"World"=>1,"Above Game"=>2,"UI"=>3,_=>1
        };
        SelectionLabel.Text=group.Name;
        _changing=false;
    }
    private void SpriteName_Changed(object sender,TextChangedEventArgs e)
    {
        if(_changing || _sprite is null)return;
        _sprite.Name=SpriteName.Text;Dirty();SpriteList.Items.Refresh();
    }
    private void SpriteLayer_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(_changing || _sprite is null || SpriteLayerCombo.SelectedIndex<0)return;
        _sprite.Layer=new[]{"Behind Game","World","Above Game","UI"}[
            SpriteLayerCombo.SelectedIndex];
        Dirty();SpriteList.Items.Refresh();
    }
    private void AddDialogue_Click(object sender,RoutedEventArgs e)
    {
        var dialog=new StudioDialogue
        {
            Id=$"scene.dialogue.{_project.Dialogues.Count+1:000}",
            Room=_scene?.Room??0
        };
        _project.Dialogues.Add(dialog);
        Dirty();RefreshProject();DialogueList.SelectedItem=dialog;
    }
    private void RemoveDialogue_Click(object sender,RoutedEventArgs e)
    {
        if(_dialogue is null)return;
        _project.Dialogues.Remove(_dialogue);_dialogue=null;
        Dirty();RefreshProject();
    }
    private void DialogueList_SelectionChanged(object sender,SelectionChangedEventArgs e)
    {
        if(DialogueList.SelectedItem is not StudioDialogue entry)return;
        _dialogue=entry;_changing=true;
        DialogueId.Text=entry.Id;
        DialogueWrap.Text=entry.MaxCharactersPerLine.ToString();
        DialogueText.Text=entry.Languages.GetValueOrDefault(_language,"");
        SelectionLabel.Text=entry.Id;
        _changing=false;
        UpdateDialoguePreview();
    }
    private void Language_Changed(object sender,SelectionChangedEventArgs e)
    {
        if(LanguageCombo.SelectedItem is not ComboBoxItem selected)return;
        _language=selected.Tag as string??"en";
        if(_dialogue is null)return;
        _changing=true;
        DialogueText.Text=_dialogue.Languages.GetValueOrDefault(_language,"");
        _changing=false;
        UpdateDialoguePreview();
    }
    private void Dialogue_Changed(object sender,TextChangedEventArgs e)
    {
        if(_changing || _dialogue is null)return;
        _dialogue.Id=DialogueId.Text.Trim();
        _dialogue.Languages[_language]=DialogueText.Text;
        if(int.TryParse(DialogueWrap.Text,out int width))
            _dialogue.MaxCharactersPerLine=Math.Clamp(width,8,80);
        Dirty();UpdateDialoguePreview();
    }
    private void UpdateDialoguePreview()
    {
        if(_dialogue is null){DialoguePreview.Text="";return;}
        List<string> pages=DialogueLayout.Paginate(
            DialogueText.Text,_dialogue.MaxCharactersPerLine,
            _dialogue.MaxLinesPerPage);
        DialoguePreview.Text=$"PAGE 1/{pages.Count}\n\n{pages[0]}";
    }
    private void NewEvent_Click(object sender,RoutedEventArgs e)
    {
        var item=new StudioEvent
        {
            Room=_scene?.Room??0,Frame=_scene?.Revision??0,
            TargetId=_dialogue?.Id??""
        };
        _project.Events.Add(item);Dirty();RefreshProject();
        Status("Added timeline event (project authoring only).");
    }
    private void AddAsset_Click(object sender,RoutedEventArgs e)
    {
        var dlg=new Microsoft.Win32.OpenFileDialog
        {
            Filter="Images, data, fonts|*.png;*.bmp;*.json;*.txt;*.ttf;*.otf|All Files|*.*",
            CheckFileExists=true
        };
        if(dlg.ShowDialog()!=true)
            return;
        string root=_path is null?AppContext.BaseDirectory:Path.GetDirectoryName(_path)!;
        _project.Assets.Add(new StudioAsset
        {
            RelativePath=Path.GetRelativePath(root,dlg.FileName),
            Kind=Path.GetExtension(dlg.FileName).Trim('.').ToLowerInvariant()
        });
        Dirty();RefreshProject();
    }
    private void Hotkeys(object sender,System.Windows.Input.KeyEventArgs e)
    {
        if(_captureGameKeys)
        {
            if(e.Key==Key.Escape)
            {
                ReleaseGameKeys();
                e.Handled=true;
                return;
            }
            int bit=GameBit(e.Key);
            if(bit!=0)
            {
                _gameKeyBits|=bit;
                _bridge?.SetInputState(_gameKeyBits,true);
                e.Handled=true;
                return;
            }
        }
        if((Keyboard.Modifiers&ModifierKeys.Control)==0)return;
        if(e.Key==Key.S){Save(false);e.Handled=true;}
        else if(e.Key==Key.O){OpenProject_Click(sender,new RoutedEventArgs());e.Handled=true;}
    }
    private void OpenAcceptanceLog_Click(object sender,RoutedEventArgs e)
    {
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName=_acceptanceLogPath,UseShellExecute=true
            });
        }
        catch(Exception ex){Error("Opening acceptance log",ex);}
    }
    private void Status(string message){StatusText.Text=message;}
    private void Log(string line)
    {
        string entry=$"[{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff}] {line}";
        ConsoleText.AppendText(entry+"\n");
        ConsoleText.ScrollToEnd();
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(_acceptanceLogPath)!);
            File.AppendAllText(_acceptanceLogPath,entry+Environment.NewLine);
        }
        catch(IOException){} // Never interrupt game input for diagnostic I/O.
        catch(UnauthorizedAccessException){}
    }
    private void Error(string operation,Exception ex)
    {
        Log($"{operation}: {ex.Message}");
        Status($"{operation} failed.");
        System.Windows.MessageBox.Show(this,ex.Message,operation,MessageBoxButton.OK,
                        MessageBoxImage.Error);
    }
}
