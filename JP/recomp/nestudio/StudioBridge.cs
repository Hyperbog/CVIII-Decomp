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
public sealed record StudioSprite(int Slot,int X,int Y,int Tile,int Attribute,
    int EmissionIndex=-1,int SourceOwner=-1)
{
    public string Label => $"OAM {Slot:00}  {(
        EmissionIndex>=0?$"Emission {EmissionIndex:00}":"Unknown emission")}  {(
        SourceOwner>=0?$"Object {SourceOwner:00}":"Unattributed")}  XY({X},{Y})  Tile ${Tile:X2}";
}
/* Game-observed source object slot, not an inferred sprite identity. */
public sealed record StudioOriginalObject(int Slot,int Generation,uint Room,
    int X,int Y,int Frame,int Selector,int Mirror,int Flags,int Script)
{
    public string Label => $"Object {Slot:00} · life {Generation}  XY({X},{Y})  selector ${Selector:X2} script ${Script:X2}";
}
public sealed record StudioEc47Trace(int Sequence,int SourceBank,int EntryPc,
    int CallerPc,int Stage,int Token,int QueueStart,int QueueEnd,
    int CursorReads,int PpuWrites,int FirstPpuAddress,int LastPpuAddress,
    int LastPpuPc,bool Returned,int SourceFrame);
public sealed record StudioPpuSourceWrite(int ProgramCounter,int PpuAddress,
    int TileValue,int ObservedWrites);
public sealed record StudioOriginalDialogueEvent(int Sequence,int Bank,
    int ProgramCounter,int ScriptId,int EventId,uint Room,int Frame,int Kind);
public sealed record StudioScene(uint Room,int Selected,bool Editing,int Renderer,
    bool Enabled,IReadOnlyList<StudioLight> Lights,
    IReadOnlyList<StudioSprite> Sprites,int Revision,
    IReadOnlyList<StudioOriginalObject> OriginalObjects,int OamPhase,
    StudioOriginalDialogueEvent? OriginalDialogue,
    int AttributionCount,int SourceCallCount,int AttributionErrors,
    StudioPpuSourceWrite? PpuSourceWrite,StudioEc47Trace? FormatterTrace,
    OriginalCommandPreview? FormatterCommand,string FormatterDecodeStatus);
/// <summary>
/// Fixed-layout in-process companion to cviii_nestudio_host_bridge.h.
/// The native recomp creates a session-isolated pagefile mapping. Only the
/// game's SDL thread executes commands. NEStudio never reads game RAM.
/// </summary>
public sealed class StudioBridge : IDisposable
{
    public const int Magic=unchecked((int)0x5453454E);
    private const int Capacity=13792; // v5 appends read-only $0300 command bytes
    private readonly MemoryMappedFile _file;
    private readonly MemoryMappedViewAccessor _view;
    private int _pendingSequence;
    private int _completedSequence;
    public int LastResult { get; private set; }
    // v1 reserved header slot, written before the session magic.
    // Used to locate SDL HWND when cmd.exe launches the native game.
    public int GameProcessId => _view.ReadInt32(72);
    public int GameFrame => _view.ReadInt32(64);
    public int AcknowledgedSequence => _view.ReadInt32(12);
    // Reserved v1 header mode=84, OAM selection masks=88/92.
    // These indicate visible 8x8 PPU OAM slots, NOT stable actor identities.
    public IReadOnlySet<int> SelectedOriginalObjectSlots
    {
        get
        {
            var selected=new HashSet<int>();
            if(_view.ReadInt32(0)!=Magic || _view.ReadInt32(84)!=1)return selected;
            uint mask=unchecked((uint)_view.ReadInt32(13448));
            for(int i=0;i<28;++i)if(((mask>>i)&1u)!=0)selected.Add(i);
            return selected;
        }
    }
    public bool SetOriginalObjectSelection(IEnumerable<int> slots)
    {
        if(_view.ReadInt32(0)!=Magic || _view.ReadInt32(84)!=1)return false;
        uint mask=0;
        foreach(int slot in slots)
            if(slot is >=0 and <28)mask|=1u<<slot;
        _view.Write(13448,unchecked((int)mask));
        return true;
    }
    public IReadOnlySet<int> SelectedSpriteSlots
    {
        get
        {
            if(_view.ReadInt32(0)!=Magic || _view.ReadInt32(84)!=1)
                return new HashSet<int>();
            uint lo=unchecked((uint)_view.ReadInt32(88));
            uint hi=unchecked((uint)_view.ReadInt32(92));
            var selected=new HashSet<int>();
            for(int i=0;i<32;i++)
            {
                if(((lo>>i)&1u)!=0)selected.Add(i);
                if(((hi>>i)&1u)!=0)selected.Add(i+32);
            }
            return selected;
        }
    }
    // v1 reserved[8] doubles as a group shortcut sequence in OAM mode;
    // it is the dialogue-click Y coordinate only in Dialogue mode.
    public int SpriteGroupRequestSequence =>
        _view.ReadInt32(0)==Magic && _view.ReadInt32(84)==1 ?
            _view.ReadInt32(104):0;
    public bool TryReadDialogueClick(out int sequence,out int x,out int y)
    {
        sequence=0;x=0;y=0;
        if(_view.ReadInt32(0)!=Magic || _view.ReadInt32(84)!=2)return false;
        int first=_view.ReadInt32(96); // reserved[6], native click sequence
        if(first==0)return false;
        int px=_view.ReadInt32(100),py=_view.ReadInt32(104);
        if(first!=_view.ReadInt32(96))return false;
        sequence=first;x=px;y=py;
        return px is >=0 and <256 && py is >=0 and <240;
    }
    public void SetDialogueHighlight(StudioDialogue? entry,uint room)
    {
        if(_view.ReadInt32(0)!=Magic)return;
        bool show=entry is not null && entry.HasViewportRegion &&
                  entry.Room==room;
        _view.Write(108,show?entry!.ViewX:0);
        _view.Write(112,show?entry!.ViewY:0);
        _view.Write(116,show?entry!.ViewWidth:0);
        _view.Write(120,show?entry!.ViewHeight:0);
        Thread.MemoryBarrier();
        _view.Write(124,show?1:0);
    }
    public bool SetSpriteSelection(IEnumerable<int> slots)
    {
        if(_view.ReadInt32(0)!=Magic || _view.ReadInt32(84)!=1)return false;
        uint lo=0,hi=0;
        foreach(int slot in slots)
        {
            if(slot is <0 or >=64)continue;
            if(slot<32)lo|=1u<<slot;
            else hi|=1u<<(slot-32);
        }
        _view.Write(88,unchecked((int)lo));
        _view.Write(92,unchecked((int)hi));
        return true;
    }
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
               bridge._view.ReadInt32(4)!=5)
            {
                bridge.Dispose();return null;
            }
            return bridge;
        }
        catch(FileNotFoundException){return null;}
        catch(UnauthorizedAccessException){return null;}
        catch(IOException){return null;}
    }
    // Session-scoped input capture: bitmask of 8 NES keyboard bindings.
    // Writes touch only reserved v1 presentation header fields (76,80).
    // The native SDL host merges them with physical keyboard/gamepads.
    public bool SetInputState(int bits,bool capture)
    {
        if(_view.ReadInt32(0)!=Magic)return false;
        _view.Write(76,bits&255);
        Thread.MemoryBarrier();
        _view.Write(80,capture?1:0);
        return true;
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
            int phase=_view.ReadInt32(11904);
            int objectCount=_view.ReadInt32(11908);
            if(objectCount is <0 or >28)return null;
            var originalObjects=new List<StudioOriginalObject>(objectCount);
            for(int i=0;i<28;++i)
            {
                long offset=11912L+44L*i;
                if(_view.ReadInt32(offset)==0)continue;
                int slot=_view.ReadInt32(offset+4);
                if(slot!=i)continue;
                originalObjects.Add(new StudioOriginalObject(
                    slot,_view.ReadInt32(offset+8),
                    unchecked((uint)_view.ReadInt32(offset+12)),
                    _view.ReadInt32(offset+16),_view.ReadInt32(offset+20),
                    _view.ReadInt32(offset+24),_view.ReadInt32(offset+28),
                    _view.ReadInt32(offset+32),_view.ReadInt32(offset+36),
                    _view.ReadInt32(offset+40)));
            }
            StudioOriginalDialogueEvent? originalDialogue=null;
            if(_view.ReadInt32(13144)>0)
            {
                originalDialogue=new StudioOriginalDialogueEvent(
                    _view.ReadInt32(13144),_view.ReadInt32(13148),
                    _view.ReadInt32(13152),_view.ReadInt32(13156),
                    _view.ReadInt32(13160),
                    unchecked((uint)_view.ReadInt32(13164)),
                    _view.ReadInt32(13168),_view.ReadInt32(13172));
            }
            int sourceValid=_view.ReadInt32(13432);
            int attributed=_view.ReadInt32(13436);
            int sourceCalls=_view.ReadInt32(13440);
            int sourceErrors=_view.ReadInt32(13444);
            StudioPpuSourceWrite? ppuWrite=null;
            int ppuWrites=_view.ReadInt32(13464);
            if(ppuWrites>0)
                ppuWrite=new StudioPpuSourceWrite(
                    _view.ReadInt32(13452),_view.ReadInt32(13456),
                    _view.ReadInt32(13460),ppuWrites);
            StudioEc47Trace? formatter=null;
            if(_view.ReadInt32(13468)>0)
                formatter=new StudioEc47Trace(
                    _view.ReadInt32(13468),_view.ReadInt32(13472),
                    _view.ReadInt32(13476),_view.ReadInt32(13480),
                    _view.ReadInt32(13484),_view.ReadInt32(13488),
                    _view.ReadInt32(13492),_view.ReadInt32(13496),
                    _view.ReadInt32(13500),_view.ReadInt32(13504),
                    _view.ReadInt32(13508),_view.ReadInt32(13512),
                    _view.ReadInt32(13516),_view.ReadInt32(13520)!=0,
                    _view.ReadInt32(13524));
            OriginalCommandPreview? formatterCommand=null;
            string decodeStatus="No completed original command-buffer capture.";
            int commandLength=_view.ReadInt32(13528);
            int commandSequence=_view.ReadInt32(13532);
            if(commandLength is >0 and <=256 && formatter is { Returned:true } &&
               formatter.Sequence==commandSequence)
            {
                var commands=new byte[commandLength];
                _view.ReadArray(13536L,commands,0,commandLength);
                OriginalGlyphCodec.TryParse(commands,
                    out formatterCommand,out decodeStatus);
            }
            var sprites=new List<StudioSprite>();
            for(int i=0;i<64;++i)
            {
                long o=128L+128L*80L+i*24L;
                if(_view.ReadInt32(o)==0)continue;
                sprites.Add(new StudioSprite(
                    _view.ReadInt32(o+4),_view.ReadInt32(o+8),
                    _view.ReadInt32(o+12),_view.ReadInt32(o+16),
                    _view.ReadInt32(o+20),
                    (phase>=0 && (phase&3)==0)
                       ? (((i-(phase>>2))&63)*17)&63 : -1,
                    sourceValid!=0 &&
                    _view.ReadInt32(13176L+4L*i) is >=0 and <28
                       ? _view.ReadInt32(13176L+4L*i) : -1));
            }
            Thread.MemoryBarrier();
            int after=_view.ReadInt32(36);
            if(before==after && (after&1)==0)
                return new StudioScene(room,selected,editing,renderer,
                                       enabled,lights,sprites,after,
                                       originalObjects,phase,originalDialogue,
                                       attributed,sourceCalls,sourceErrors,
                                       ppuWrite,formatter,formatterCommand,decodeStatus);
        }
        return null;
    }
    public void Dispose()
    {
        try {SetInputState(0,false);} catch(IOException){}
        _view.Dispose();
        _file.Dispose();
    }
}
