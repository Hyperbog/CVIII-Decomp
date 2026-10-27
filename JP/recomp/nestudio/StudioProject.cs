using System.Text.Json;
using System.Text.Json.Serialization;

namespace NEStudio;

/// <summary>
/// Canonical editable NEStudio content. Never embeds ROM bytes or native
/// machine/save-state memory. Existing game-side lighting stays in config.ini
/// until the v2 content-pack runtime importer is ready.
/// </summary>
public sealed class StudioProject
{
    public int SchemaVersion { get; set; } = 1;
    public string Name { get; set; } = "Untitled Enhanced Project";
    public string GameExecutable { get; set; } = "";
    public List<StudioSpriteGroup> SpriteGroups { get; set; } = new();
    public List<StudioDialogue> Dialogues { get; set; } = new();
    public List<StudioEvent> Events { get; set; } = new();
    public List<StudioAsset> Assets { get; set; } = new();
    public static StudioProject Create() => new()
    {
        SpriteGroups = new()
        {
            new() { Name="Background", Layer="Behind Game" },
            new() { Name="World Sprites", Layer="World" },
            new() { Name="Foreground", Layer="Above Game" }
        }
    };
}
public sealed class StudioSpriteGroup
{
    public string Id { get; set; } = "sprite.group." + Guid.NewGuid().ToString("N");
    public string Name { get; set; } = "New Sprite Group";
    public string Layer { get; set; } = "World";
    public uint Room { get; set; } = 0;
    public bool Visible { get; set; } = true;
    public string? ReplacementAssetId { get; set; }
    public override string ToString() => $"{Name}  [{Layer}]";
}
public sealed class StudioDialogue
{
    public string Id { get; set; } = "dialogue." + Guid.NewGuid().ToString("N");
    public uint Room { get; set; }
    public string Trigger { get; set; } = "manual";
    public int MaxCharactersPerLine { get; set; } = 28;
    public int MaxLinesPerPage { get; set; } = 4;
    public Dictionary<string, string> Languages { get; set; } = new()
    {
        ["en"]="Enter dialogue here."
    };
    public override string ToString() => Id;
}
public sealed class StudioEvent
{
    public string Id { get; set; } = "timeline." + Guid.NewGuid().ToString("N");
    public uint Room { get; set; }
    public int Frame { get; set; }
    public string Kind { get; set; } = "dialogue";
    public string TargetId { get; set; } = "";
    public override string ToString() => $"Frame {Frame,5}  |  {Kind,-10}  {TargetId}";
}
public sealed class StudioAsset
{
    public string Id { get; set; } = "asset." + Guid.NewGuid().ToString("N");
    public string RelativePath { get; set; } = "";
    public string Kind { get; set; } = "image";
    public override string ToString() => $"{Kind}: {RelativePath}";
}
public static class StudioProjectFile
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true,
        Converters = { new JsonStringEnumConverter() }
    };
    public static StudioProject Load(string path)
    {
        if(new FileInfo(path).Length>16*1024*1024)
            throw new InvalidDataException("NEStudio project exceeds the 16 MB editor-content limit.");
        StudioProject? project=JsonSerializer.Deserialize<StudioProject>(
            File.ReadAllText(path),Options);
        if(project is null || project.SchemaVersion!=1)
            throw new InvalidDataException("Unsupported NEStudio project schema; expected version 1.");
        project.SpriteGroups ??=new();
        project.Dialogues ??=new();
        project.Events ??=new();
        project.Assets ??=new();
        if(project.SpriteGroups.Count>4096 || project.Dialogues.Count>8192 ||
           project.Events.Count>32768 || project.Assets.Count>8192)
            throw new InvalidDataException("Project exceeds bounded editor content limits.");
        foreach(var entry in project.Dialogues)
        {
            if(entry.Languages is null)entry.Languages=new();
            entry.MaxCharactersPerLine=Math.Clamp(entry.MaxCharactersPerLine,8,80);
            entry.MaxLinesPerPage=Math.Clamp(entry.MaxLinesPerPage,1,16);
        }
        return project;
    }
    public static void Save(StudioProject project,string path)
    {
        ArgumentNullException.ThrowIfNull(project);
        string full=Path.GetFullPath(path);
        Directory.CreateDirectory(Path.GetDirectoryName(full)!);
        string temp=full+".tmp";
        File.WriteAllText(temp,JsonSerializer.Serialize(project,Options));
        File.Move(temp,full,true); // atomic replacement on the same volume
    }
}
public static class DialogueLayout
{
    /// <summary>
    /// Deterministic editor preview: manual newlines and "[page]" page
    /// delimiters are preserved; wraps on words and splits long words.
    /// This is data authoring, NOT a claim that original NES dialogue
    /// dispatch or VRC6/font renderer has been replaced.
    /// </summary>
    public static List<string> Paginate(string text,int width,int lines)
    {
        width=Math.Clamp(width,8,80);
        lines=Math.Clamp(lines,1,16);
        var pages=new List<string>();
        var page=new List<string>();
        void PushLine(string line)
        {
            page.Add(line);
            if(page.Count>=lines)
            {
                pages.Add(string.Join("\n",page));
                page.Clear();
            }
        }
        void PushPage()
        {
            pages.Add(string.Join("\n",page));
            page.Clear();
        }
        foreach(string raw in (text??"").Replace("\r\n","\n").Split('\n'))
        {
            if(raw.Trim().Equals("[page]",StringComparison.OrdinalIgnoreCase))
            {
                PushPage();continue;
            }
            if(raw.Length==0){PushLine("");continue;}
            var words=raw.Split(' ');
            string row="";
            foreach(string word in words)
            {
                string remaining=word;
                while(remaining.Length>0)
                {
                    int space=row.Length>0?1:0;
                    int capacity=width-row.Length-space;
                    if(capacity==0){PushLine(row);row="";continue;}
                    if(remaining.Length<=capacity)
                    {
                        row=row.Length>0?row+" "+remaining:remaining;
                        remaining="";break;
                    }
                    if(row.Length>0){PushLine(row);row="";continue;}
                    PushLine(remaining[..capacity]);
                    remaining=remaining[capacity..];
                }
            }
            PushLine(row);
        }
        if(page.Count>0 || pages.Count==0)PushPage();
        return pages;
    }
}
