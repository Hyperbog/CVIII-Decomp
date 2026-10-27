using NEStudio;
using System.Text.Json;

static void Check(bool ok,string reason)
{
    if(!ok)throw new Exception("NEStudio contract failure: "+reason);
}
var project=StudioProject.Create();
Check(project.SchemaVersion==1,"schema v1");
Check(project.SpriteGroups.Count>=3,"initial sprite groups");
project.SpriteGroups.Add(new StudioSpriteGroup{Name="Trevor Body",
    Layer="World",Room=0x2601});
project.SpriteGroups.Add(new StudioSpriteGroup{Name="Torch Flame",
    Layer="Above Game",Room=0x2601});
project.Dialogues.Add(new StudioDialogue
{
    Id="jp.stage01.dracula.001",Room=0x2601,
    MaxCharactersPerLine=16,MaxLinesPerPage=3,
    Languages=new()
    {
        ["ja"]="こんばんは",
        ["en"]="Welcome to the castle.\nSeek your destiny.\n[page]\nThe night is long.",
        ["fr"]="Bienvenue au château."
    }
});
project.Events.Add(new StudioEvent
{
    Room=0x2601,Frame=120,Kind="dialogue",
    TargetId="jp.stage01.dracula.001"
});
project.Assets.Add(new StudioAsset
{
    RelativePath="assets/sprite-overrides/trevor.png",Kind="png"
});
var pages=DialogueLayout.Paginate(project.Dialogues[0].Languages["en"],16,3);
Check(pages.Count>=2,"explicit page delimiter and wrapping");
Check(pages[0].Contains("Welcome") && pages[^1].Contains("night"),
    "page text retained");
Check(DialogueLayout.Paginate("123456789012345678901",8,2).Count>=2,
    "long unbroken words still wrap");
string file=Path.Combine(Path.GetTempPath(),
    "nestudio-rom-free-"+Guid.NewGuid().ToString("N")+".nestudio");
try
{
    StudioProjectFile.Save(project,file);
    StudioProject returned=StudioProjectFile.Load(file);
    Check(returned.SpriteGroups.Count==5,"sprite grouping persistence");
    Check(returned.Dialogues.Count==1 &&
          returned.Dialogues[0].Languages["ja"]=="こんばんは",
          "Unicode localization roundtrip");
    Check(returned.Events[0].Frame==120,"timeline preservation");
    Check(returned.Assets[0].RelativePath.EndsWith("trevor.png"),
          "external image reference");
    var json=File.ReadAllText(file);
    Check(!json.Contains("ROM bytes"),"ROM-free project data");
    File.WriteAllText(file,@"{""SchemaVersion"":50}");
    bool rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"unknown project schema fails closed");
}
finally {File.Delete(file);}
Console.WriteLine("PASS NEStudio v1 project, sprite layers, multilingual dialogue, text flow and timeline round-trip");
