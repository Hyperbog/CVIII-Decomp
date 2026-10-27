using System.IO;
using System.IO.MemoryMappedFiles;
using System.Text;
using System.Threading;

namespace NEStudio;

public sealed record StudioLight(int Slot,uint Room,int X,int Y,int Radius,
    int Power,int Red,int Green,int Blue,int Shape,int Muted,int Flicker,
    string Name)
{
    public string Label => $"{Slot+1:00}  {(string.IsNullOrWhiteSpace(Name)?"Light":Name)}  ({X},{Y})";
}
public sealed record StudioSprite(int Slot,int X,int Y,int Tile,int Attribute)
{
    public string Label => $"OAM {Slot:00}   XY({X},{Y})   Tile ${Tile:X2}  Attr ${Attribute:X2}";
}
public sealed record StudioScene(uint Room,int Selected,bool Editing,int Renderer,
    bool Enabled,IReadOnlyList<StudioLight> Lights,
    IReadOnlyList<StudioSprite> Sprites,int Revision);
/// <summary>
/// Fixed-layout in-process companion to cviii_nestudio_host_bridge.h.
/// The native recomp creates a session-isolated pagefile mapping. Only the
/// game's SDL thread executes commands. NEStudio never reads game RAM.
/// </summary>
public sealed class StudioBridge : IDisposable
{
    public const int Magic=unchecked((int)0x5453454E);
    private const int Capacity=128+128*80+64*24;
    private readonly MemoryMappedFile _file;
    private readonly MemoryMappedViewAccessor _view;
    private int _pendingSequence;
    private int _completedSequence;
    public int LastResult { get; private set; }
    private StudioBridge(MemoryMappedFile map)
    {
        _file=map;
        _view=map.CreateViewAccessor(0,Capacity,MemoryMappedFileAccess.ReadWrite);
    }
    public static StudioBridge? TryOpen(string session)
    {
        try
        {
            MemoryMappedFile map=MemoryMappedFile.OpenExisting(
                @"Local\NEStudio-"+session,MemoryMappedFileRights.ReadWrite);
            var bridge=new StudioBridge(map);
            if(bridge._view.ReadInt32(0)!=Magic ||
               bridge._view.ReadInt32(4)!=1)
            {
                bridge.Dispose();return null;
            }
            return bridge;
        }
        catch(FileNotFoundException){return null;}
        catch(UnauthorizedAccessException){return null;}
        catch(IOException){return null;}
    }
    public bool TryCommand(int operation,int arg0=0,int arg1=0,int arg2=0)
    {
        if(_view.ReadInt32(0)!=Magic)return false;
        int request=_view.ReadInt32(8);
        int ack=_view.ReadInt32(12);
        if(request!=ack)return false;
        int seq=request+1;
        if(seq==0)seq=1;
        _view.Write(16,operation);
        _view.Write(20,arg0);
        _view.Write(24,arg1);
        _view.Write(28,arg2);
        Thread.MemoryBarrier();
        _view.Write(8,seq);
        _pendingSequence=seq;
        return true;
    }
    public StudioScene? Poll()
    {
        if(_view.ReadInt32(0)!=Magic)return null;
        int ack=_view.ReadInt32(12);
        if(ack!=_completedSequence && ack==_pendingSequence)
        {
            LastResult=_view.ReadInt32(32);
            _completedSequence=ack;
        }
        for(int attempt=0;attempt<3;++attempt)
        {
            int before=_view.ReadInt32(36);
            if((before&1)!=0)continue;
            uint room=unchecked((uint)_view.ReadInt32(40));
            int selected=_view.ReadInt32(44);
            bool editing=_view.ReadInt32(48)!=0;
            int renderer=_view.ReadInt32(52);
            bool enabled=_view.ReadInt32(68)!=0;
            var lights=new List<StudioLight>();
            for(int i=0;i<128;++i)
            {
                long o=128L+80L*i;
                if(_view.ReadInt32(o)==0)continue;
                uint lightRoom=unchecked((uint)_view.ReadInt32(o+4));
                if(lightRoom!=room)continue;
                byte[] bytes=new byte[32];
                _view.ReadArray(o+48,bytes,0,32);
                int zero=Array.IndexOf(bytes,(byte)0);
                string name=Encoding.ASCII.GetString(bytes,0,zero<0?32:zero);
                lights.Add(new StudioLight(i,lightRoom,
                    _view.ReadInt32(o+8),_view.ReadInt32(o+12),
                    _view.ReadInt32(o+16),_view.ReadInt32(o+20),
                    _view.ReadInt32(o+24),_view.ReadInt32(o+28),
                    _view.ReadInt32(o+32),_view.ReadInt32(o+36),
                    _view.ReadInt32(o+40),_view.ReadInt32(o+44),name));
            }
            var sprites=new List<StudioSprite>();
            for(int i=0;i<64;++i)
            {
                long o=128L+128L*80L+i*24L;
                if(_view.ReadInt32(o)==0)continue;
                sprites.Add(new StudioSprite(
                    _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                    _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                    _view.ReadInt32(o+20)));
            }
            Thread.MemoryBarrier();
            int after=_view.ReadInt32(36);
            if(before==after && (after&1)==0)
                return new StudioScene(room,selected,editing,renderer,
                                       enabled,lights,sprites,after);
        }
        return null;
    }
    public void Dispose()
    {
        _view.Dispose();
        _file.Dispose();
    }
}
