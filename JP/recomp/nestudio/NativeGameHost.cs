using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using WinForms = System.Windows.Forms;

namespace NEStudio;

/// <summary>
/// Owns only the child game process it launches. Uses a native child HWND,
/// not screenshots or a stretched captured NES frame. SDL2 continues to
/// handle mouse mapping, audio, timing, keyboard and gamepad input.
/// </summary>
public sealed class NativeGameHost : IDisposable
{
    private Process? _process;
    private IntPtr _window;
    private int _nativeGamePid;
    private bool _batchLauncher;
    private DateTime _launchTimeUtc;
    private string _runtimeExecutable="";
    private WinForms.Panel? _panel;
    public string Session { get; private set; } = "";
    public bool IsRunning => (_process is { HasExited:false }) ||
        NativeProcessAlive(_nativeGamePid);
    // A valid HWND is not proof of embedding. SDL may detach/recreate a
    // top-level window after a mode or display change.
    public bool IsEmbedded => _window!=IntPtr.Zero && IsWindow(_window) &&
        _panel is not null && GetParent(_window)==_panel.Handle;
    public int? ProcessId =>
        NativeProcessAlive(_nativeGamePid)?_nativeGamePid:
        (_process is { HasExited: false }?_process.Id:null);
    public bool IsBatchLauncher => _batchLauncher;
    public string RuntimeExecutable => _runtimeExecutable;
    public TimeSpan StartupElapsed => string.IsNullOrEmpty(Session)?TimeSpan.Zero:DateTime.UtcNow-_launchTimeUtc;
    private static bool NativeProcessAlive(int pid)
    {
        if(pid<=0)return false;
        try
        {
            using Process process=Process.GetProcessById(pid);
            return !process.HasExited;
        }
        catch(ArgumentException){return false;}
        catch(InvalidOperationException){return false;}
    }
    public void SetNativeProcessId(int pid)
    {
        // The PID comes from the unique, per-launch native session map.
        // It is not supplied by a path, .bat command or a user text field.
        if(pid>0 && NativeProcessAlive(pid))_nativeGamePid=pid;
    }
    public void AttachPanel(WinForms.Panel panel)
    {
        _panel=panel;
        panel.BackColor=System.Drawing.Color.FromArgb(8,13,21);
        panel.Resize+=(sender,args)=>Resize();
    }
    private const string OriginalJpSha256=
        "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28";

    private static string ResolveNativeExe(string requested)
    {
        string path=Path.GetFullPath(requested);
        string extension=Path.GetExtension(path).ToLowerInvariant();
        if(extension==".exe")return path;
        if(extension is not (".bat" or ".cmd"))
            throw new InvalidDataException("Select a private Enhanced game EXE or its launcher.");
        // Run/Attach must NEVER execute a build/launcher BAT, cmd.exe,
        // Start-Process or another emulator. Instead resolve the actual
        // session-enabled native program built by our private builder.
        string folder=Path.GetDirectoryName(path)!;
        var candidates=new[]
        {
            Path.Combine(folder,"jp_akumajou_densetsu.exe"),
            Path.Combine(folder,"AlphaCandidate","jp_akumajou_densetsu.exe"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                "NEStudio-Preview","AlphaCandidate","jp_akumajou_densetsu.exe")
        };
        foreach(string candidate in candidates)
        {
            if(File.Exists(candidate) &&
               File.Exists(Path.Combine(Path.GetDirectoryName(candidate)!,"NEStudio-RomPath.txt")))
                return candidate;
        }
        throw new FileNotFoundException(
            "This BAT is not a game viewport. Build the owner-private NEStudio game first " +
            "with Build-Private-Game.bat, then choose " +
            @"%USERPROFILE%\NEStudio-Preview\AlphaCandidate\jp_akumajou_densetsu.exe" +
            " in Set Game / Launcher. No external console was opened.",path);
    }

    private static string ValidatePrivateGame(string executable)
    {
        string directory=Path.GetDirectoryName(executable)!;
        if(!File.Exists(Path.Combine(directory,"SDL2.dll")))
            throw new FileNotFoundException("Private native game needs SDL2.dll beside its executable.");
        string hint=Path.Combine(directory,"NEStudio-RomPath.txt");
        if(!File.Exists(hint))
            throw new FileNotFoundException(
                "No authenticated original JP ROM hint. Run Build-Private-Game.bat " +
                "before attaching the private game.",hint);
        string rom=File.ReadAllText(hint).Trim().Trim('"');
        if(!File.Exists(rom))
            throw new FileNotFoundException("Saved original Japanese ROM location does not exist.",rom);
        using(var stream=File.OpenRead(rom))
        {
            string hash=Convert.ToHexString(SHA256.HashData(stream));
            if(!hash.Equals(OriginalJpSha256,StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Saved ROM is not the authenticated original Japanese cartridge.");
        }
        // Prevent attaching a stale generic Alpha EXE that opens a separate
        // window without NEStudio IPC, even when it shares the same filename.
        string native=Encoding.ASCII.GetString(File.ReadAllBytes(executable));
        if(!native.Contains("CVIII_NESTUDIO_SESSION",StringComparison.Ordinal))
            throw new InvalidDataException(
                "The native game lacks the NEStudio bridge. Rebuild via " +
                "Build-Private-Game.bat; do not use an older CVIII Alpha executable.");
        return rom;
    }

    public void Start(string path)
    {
        if(IsRunning)return;
        if(_process is not null)Stop();
        if(!File.Exists(path))
            throw new FileNotFoundException("Game launcher does not exist.",path);
        string full=ResolveNativeExe(path);
        string rom=ValidatePrivateGame(full);
        string directory=Path.GetDirectoryName(full)!;
        Session=Guid.NewGuid().ToString("N");
        var start=new ProcessStartInfo
        {
            FileName=full,
            WorkingDirectory=directory,
            UseShellExecute=false,
            CreateNoWindow=true // never display a BAT/CMD build console
        };
        start.ArgumentList.Add(rom);
        start.ArgumentList.Add("--edition");
        start.ArgumentList.Add("enhanced");
        start.ArgumentList.Add("--unlimited-sprites");
        start.ArgumentList.Add("0");
        start.ArgumentList.Add("--stable-sprites");
        start.ArgumentList.Add("0");
        string assets=Path.Combine(directory,"CVIII-CHR-Index.dat");
        if(File.Exists(assets))
        {
            start.ArgumentList.Add("--asset-index");
            start.ArgumentList.Add(assets);
        }
        start.Environment["CVIII_NESTUDIO_SESSION"]=Session;
        _process=Process.Start(start) ??
            throw new IOException("Could not launch the private native game.");
        _nativeGamePid=_process.Id;
        _runtimeExecutable=full;
        _batchLauncher=false;
        _launchTimeUtc=DateTime.UtcNow;
        _window=IntPtr.Zero;
    }
    public bool TryEmbed()
    {
        if(!IsRunning || _panel is null)return false;
        if(IsEmbedded){Resize();return true;}
        // For .bat/.cmd launchers cmd.exe is NEVER the SDL window owner.
        // Wait for the game to publish its PID in the session handshake.
        int pid=_nativeGamePid;
        if(pid<=0 || !NativeProcessAlive(pid))return false;
        IntPtr found=IntPtr.Zero;
        EnumWindows((hwnd,param)=>
        {
            GetWindowThreadProcessId(hwnd,out uint process);
            if(process!=(uint)pid || !IsWindowVisible(hwnd))return true;
            var className=new System.Text.StringBuilder(128);
            GetClassName(hwnd,className,className.Capacity);
            if(!className.ToString().Contains("SDL",StringComparison.OrdinalIgnoreCase))
                return true;
            found=hwnd;return false;
        },IntPtr.Zero);
        if(found==IntPtr.Zero)return false;
        // The game is a genuine resizable Win32 CHILD window of our panel.
        // It owns its SDL input and graphics context. SetWindowPos resizes
        // the real SDL drawable, so its mouse mapping remains correct.
        IntPtr originalStyle=GetWindowLongPtr(found,-16);
        IntPtr originalExtended=GetWindowLongPtr(found,-20);
        long style=originalStyle.ToInt64();
        style&=~(WS_CAPTION|WS_THICKFRAME|WS_MINIMIZEBOX|
                 WS_MAXIMIZEBOX|WS_SYSMENU|WS_POPUP);
        style|=WS_CHILD|WS_VISIBLE;
        SetWindowLongPtr(found,-16,new IntPtr(style));
        SetWindowLongPtr(found,-20,
            new IntPtr(originalExtended.ToInt64() & ~WS_EX_APPWINDOW));
        SetParent(found,_panel.Handle);
        int parentError=Marshal.GetLastWin32Error();
        if(GetParent(found)!=_panel.Handle)
        {
            // Do not leave a detached floating SDL window styled as a child.
            SetWindowLongPtr(found,-16,originalStyle);
            SetWindowLongPtr(found,-20,originalExtended);
            throw new InvalidOperationException(
                $"Could not embed SDL2 window: Win32 {parentError}");
        }
        _window=found;
        Resize();
        return true;
    }
    public void Resize()
    {
        if(_panel is null || !IsEmbedded)return;
        int pw=Math.Max(1,_panel.ClientSize.Width);
        int ph=Math.Max(1,_panel.ClientSize.Height);
        // Keep NES presentation at the physical 256:240 aspect ratio;
        // NO stretch into widescreen, and SDL receives real window pixels.
        int w=Math.Min(pw,(int)Math.Floor(ph*256.0/240.0));
        int h=Math.Min(ph,(int)Math.Floor(pw*240.0/256.0));
        int x=(pw-w)/2,y=(ph-h)/2;
        SetWindowPos(_window,IntPtr.Zero,x,y,Math.Max(1,w),Math.Max(1,h),
                     SWP_NOZORDER|SWP_NOACTIVATE|SWP_FRAMECHANGED|SWP_SHOWWINDOW);
    }
    /// <summary>
    /// Give the genuine SDL child Win32 keyboard focus. SetFocus alone cannot
    /// cross the editor/game UI-thread input queue boundary after SetParent.
    /// Attach only long enough to change focus, then always detach.
    /// </summary>
    public bool FocusGame()
    {
        if(!IsEmbedded || _panel is null)return false;
        IntPtr root=GetAncestor(_panel.Handle,2); // GA_ROOT editor top level
        if(root!=IntPtr.Zero)SetForegroundWindow(root);
        uint gameThread=GetWindowThreadProcessId(_window,out _);
        uint uiThread=GetCurrentThreadId();
        if(gameThread==0)return false;
        bool attached=gameThread!=uiThread &&
            AttachThreadInput(uiThread,gameThread,true);
        if(gameThread!=uiThread && !attached)return false;
        try
        {
            SetFocus(_window);
            return GetFocus()==_window;
        }
        finally
        {
            if(attached)AttachThreadInput(uiThread,gameThread,false);
        }
    }
    public void Stop()
    {
        if(_process is null)
        {
            _nativeGamePid=0;_batchLauncher=false;
            _runtimeExecutable="";
            _window=IntPtr.Zero;Session="";
            return;
        }
        try
        {
            if(_nativeGamePid>0 && _nativeGamePid!=_process.Id)
            {
                // Only a PID learned through this launch's native session
                // mapping can be stopped independently of cmd.exe.
                try
                {
                    using Process native=Process.GetProcessById(_nativeGamePid);
                    if(!native.HasExited)
                    {
                        native.CloseMainWindow();
                        if(!native.WaitForExit(1200))
                            native.Kill(entireProcessTree:true);
                    }
                }
                catch(ArgumentException){}
                catch(InvalidOperationException){}
            }
            if(!_process.HasExited)
            {
                _process.CloseMainWindow();
                if(!_process.WaitForExit(1200))
                    _process.Kill(entireProcessTree:true);
            }
        }
        catch(InvalidOperationException){}
        finally
        {
            _process.Dispose();_process=null;
            _nativeGamePid=0;_batchLauncher=false;
            _runtimeExecutable="";
            _window=IntPtr.Zero;Session="";
        }
    }
    public void Dispose() => Stop();
    private const long WS_CAPTION=0x00C00000,WS_THICKFRAME=0x00040000,
       WS_MINIMIZEBOX=0x00020000,WS_MAXIMIZEBOX=0x00010000,
       WS_SYSMENU=0x00080000,WS_POPUP=unchecked((long)0x80000000),
       WS_CHILD=0x40000000,WS_VISIBLE=0x10000000,
       WS_EX_APPWINDOW=0x00040000;
    private const uint SWP_NOZORDER=4,SWP_NOACTIVATE=0x10,
                       SWP_FRAMECHANGED=0x20,SWP_SHOWWINDOW=0x40;
    private delegate bool EnumWindowsDelegate(IntPtr hwnd,IntPtr parameter);
    [DllImport("user32.dll")] private static extern bool EnumWindows(
        EnumWindowsDelegate callback,IntPtr data);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(
        IntPtr hwnd,out uint processId);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] private static extern bool IsWindow(IntPtr hwnd);
    [DllImport("user32.dll",CharSet=CharSet.Unicode)] private static extern int GetClassName(
        IntPtr hwnd,System.Text.StringBuilder name,int max);
    [DllImport("user32.dll",SetLastError=true)] private static extern IntPtr SetParent(
        IntPtr child,IntPtr parent);
    [DllImport("user32.dll")] private static extern IntPtr GetParent(IntPtr hwnd);
    [DllImport("user32.dll",EntryPoint="GetWindowLongPtrW",SetLastError=true)]
    private static extern IntPtr GetWindowLongPtr(IntPtr hwnd,int index);
    [DllImport("user32.dll",EntryPoint="SetWindowLongPtrW",SetLastError=true)]
    private static extern IntPtr SetWindowLongPtr(IntPtr hwnd,int index,IntPtr value);
    [DllImport("user32.dll",SetLastError=true)] private static extern bool SetWindowPos(
        IntPtr hwnd,IntPtr after,int x,int y,int w,int h,uint flags);
    [DllImport("user32.dll")] private static extern IntPtr SetFocus(IntPtr hwnd);
    [DllImport("user32.dll")] private static extern IntPtr GetFocus();
    [DllImport("kernel32.dll")] private static extern uint GetCurrentThreadId();
    [DllImport("user32.dll",SetLastError=true)] private static extern bool AttachThreadInput(
        uint sourceThread,uint targetThread,bool attach);
    [DllImport("user32.dll")] private static extern IntPtr GetAncestor(IntPtr hwnd,uint flags);
    [DllImport("user32.dll")] private static extern bool SetForegroundWindow(IntPtr hwnd);
}
