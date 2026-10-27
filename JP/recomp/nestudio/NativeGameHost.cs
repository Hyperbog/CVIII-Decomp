using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
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
    private WinForms.Panel? _panel;
    public string Session { get; private set; } = "";
    public bool IsRunning => _process is { HasExited: false };
    public bool IsEmbedded => _window!=IntPtr.Zero && IsWindow(_window);
    public int? ProcessId => IsRunning?_process!.Id:null;
    public void AttachPanel(WinForms.Panel panel)
    {
        _panel=panel;
        panel.BackColor=System.Drawing.Color.FromArgb(8,13,21);
        panel.Resize+=(sender,args)=>Resize();
    }
    public void Start(string path)
    {
        if(IsRunning)return;
        if(!File.Exists(path))
            throw new FileNotFoundException("Build the verified Japanese Enhanced game first.",path);
        string directory=Path.GetDirectoryName(Path.GetFullPath(path))!;
        if(!File.Exists(Path.Combine(directory,"SDL2.dll")))
            throw new FileNotFoundException("Game directory must contain SDL2.dll.");
        Session=Guid.NewGuid().ToString("N");
        var start=new ProcessStartInfo
        {
            FileName=Path.GetFullPath(path),
            WorkingDirectory=directory,
            Arguments="--edition Enhanced",
            UseShellExecute=false,
            CreateNoWindow=false
        };
        start.Environment["CVIII_NESTUDIO_SESSION"]=Session;
        _process=Process.Start(start) ??
            throw new IOException("Could not launch the Enhanced game.");
        _window=IntPtr.Zero;
    }
    public bool TryEmbed()
    {
        if(!IsRunning || _panel is null)return false;
        if(IsEmbedded){Resize();return true;}
        int pid=_process!.Id;
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
        long style=GetWindowLongPtr(found,-16).ToInt64();
        style&=~(WS_CAPTION|WS_THICKFRAME|WS_MINIMIZEBOX|
                 WS_MAXIMIZEBOX|WS_SYSMENU|WS_POPUP);
        style|=WS_CHILD|WS_VISIBLE;
        SetWindowLongPtr(found,-16,new IntPtr(style));
        if(SetParent(found,_panel.Handle)==IntPtr.Zero &&
           Marshal.GetLastWin32Error()!=0)
            throw new InvalidOperationException(
                $"Could not embed SDL2 window: Win32 {Marshal.GetLastWin32Error()}");
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
    public void FocusGame()
    {
        if(IsEmbedded)SetFocus(_window);
    }
    public void Stop()
    {
        if(_process is null)return;
        try
        {
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
            _window=IntPtr.Zero;Session="";
        }
    }
    public void Dispose() => Stop();
    private const long WS_CAPTION=0x00C00000,WS_THICKFRAME=0x00040000,
       WS_MINIMIZEBOX=0x00020000,WS_MAXIMIZEBOX=0x00010000,
       WS_SYSMENU=0x00080000,WS_POPUP=unchecked((long)0x80000000),
       WS_CHILD=0x40000000,WS_VISIBLE=0x10000000;
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
    [DllImport("user32.dll",EntryPoint="GetWindowLongPtrW",SetLastError=true)]
    private static extern IntPtr GetWindowLongPtr(IntPtr hwnd,int index);
    [DllImport("user32.dll",EntryPoint="SetWindowLongPtrW",SetLastError=true)]
    private static extern IntPtr SetWindowLongPtr(IntPtr hwnd,int index,IntPtr value);
    [DllImport("user32.dll",SetLastError=true)] private static extern bool SetWindowPos(
        IntPtr hwnd,IntPtr after,int x,int y,int w,int h,uint flags);
    [DllImport("user32.dll")] private static extern IntPtr SetFocus(IntPtr hwnd);
}
