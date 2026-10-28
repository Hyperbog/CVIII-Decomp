using NEStudio;
using System.Text.Json;

static void Check(bool ok,string reason)
{
    if(!ok)throw new Exception("NEStudio contract failure: "+reason);
}
// Original message command geometry and source-coupled dry-run constraints.
byte[] sourceCommand={0x01,0x20,0x20,0xC0,0xC1,0x00,0xFF};
Check(OriginalGlyphCodec.TryParse(sourceCommand,out var original,out _)
      && original is not null && original.Rows.Count==1,
      "original bounded nametable tile command parsed");
var sourceTrace=new StudioEc47Trace(1,0x0A,0xEC47,0xB8FF,
    2,0x32,10,17,3,0,0,0,0,true,120);
var authored=new StudioDialogue{Trigger="original-ec47-formatter",
    Room=0x2601,SourceMessageStage=2,SourceMessageByte=0x32};
var draft=OriginalDialogueSafetyGate.Validate(authored,0x2601,
    sourceTrace,original,"AZ");
Check(draft.Allowed && draft.CandidateBytes==sourceCommand.Length,
      "source-attested exact-geometry A-Z offline candidate");
Check(!OriginalDialogueSafetyGate.Validate(authored,0x2602,
      sourceTrace,original,"AZ").Allowed,"wrong room blocked");
authored.SourceCommandSha256=new string('0',64);
Check(!OriginalDialogueSafetyGate.Validate(authored,0x2601,
      sourceTrace,original,"AZ").Allowed,"stale original source hash blocked");
authored.SourceCommandSha256=original!.SourceSha256;
Check(!OriginalDialogueSafetyGate.Validate(authored,0x2601,
      sourceTrace with { Returned=false },original,"AZ").Allowed,
      "unreturned EC47 invocation blocked");
Check(!OriginalDialogueSafetyGate.Validate(authored,0x2601,
      sourceTrace,original,"日本語").Allowed,"unverified glyphs blocked");
Check(!OriginalDialogueSafetyGate.Validate(authored,0x2601,
      sourceTrace with { QueueEnd=18 },original,"AZ").Allowed,
      "changed original command extent blocked");
byte[] unknownCommand={0x01,0x20,0x20,0xE2,0xFF};
Check(OriginalGlyphCodec.TryParse(unknownCommand,out var unknown,out _)
      && !OriginalDialogueSafetyGate.Validate(
           authored,0x2601,sourceTrace,unknown,"A").Allowed,
      "unmapped original tile or stale hash blocked");

var project=StudioProject.Create();
Check(project.SchemaVersion==1,"schema v1");
Check(project.SpriteGroups.Count>=3,"initial sprite groups");
project.SpriteGroups.Add(new StudioSpriteGroup{Name="Trevor Body",
    Layer="World",Room=0x2601});
project.SpriteGroups.Add(new StudioSpriteGroup{Name="Torch Flame",
    Layer="Above Game",Room=0x2601});
project.SpriteGroups.Add(new StudioSpriteGroup
{
    Name="Original Actor Lifetimes",Room=0x2601,
    OriginalObjects=new()
    {
        new StudioOriginalObjectRef{Room=0x2601,ObjectSlot=1,Generation=2},
        new StudioOriginalObjectRef{Room=0x2601,ObjectSlot=4,Generation=1}
    }
});
project.SpriteGroups.Add(new StudioSpriteGroup
{
    Name="Paused OAM Body Parts",Room=0x2601,Layer="World",
    CapturedFrame=120,
    Members=new()
    {
        new StudioSpriteMember{OamSlot=3,Tile=0x24,Attributes=0x01,CaptureX=64,CaptureY=100},
        new StudioSpriteMember{OamSlot=8,Tile=0x25,Attributes=0x01,CaptureX=72,CaptureY=100}
    }
});
project.Dialogues.Add(new StudioDialogue
{
    Id="jp.stage01.dracula.001",Room=0x2601,
    MaxCharactersPerLine=16,MaxLinesPerPage=3,
    HasViewportRegion=true,ViewX=24,ViewY=164,ViewWidth=160,ViewHeight=32,
    Trigger="observed-actor-script",SourceObjectSlot=4,
    SourceGeneration=1,SourceScriptId=0x1B,
    Languages=new()
    {
        ["ja"]="こんばんは",
        ["en"]="Welcome to the castle.\nSeek your destiny.\n[page]\nThe night is long.",
        ["fr"]="Bienvenue au château."
    }
});
project.Dialogues.Add(new StudioDialogue
{
    Id="jp.original.room.message",Room=0x2601,
    Trigger="original-room-message",SourceMessageStage=2,
    SourceMessageByte=0x34
});
project.Dialogues.Add(new StudioDialogue
{
    Id="jp.original.ec47.formatter",Room=0x2601,
    Trigger="original-ec47-formatter",SourceMessageStage=2,
    SourceMessageByte=0x32
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
    Check(returned.SpriteGroups.Count==7,"sprite grouping persistence");
    Check(returned.SpriteGroups[^2].OriginalObjects.Count==2 &&
          returned.SpriteGroups[^2].OriginalObjects[0].ObjectSlot==1 &&
          returned.SpriteGroups[^2].OriginalObjects[0].Generation==2,
          "original CPU object lifetime references persist separately from rotating OAM");
    Check(returned.SpriteGroups[^1].Members.Count==2 &&
          returned.SpriteGroups[^1].Members[0].OamSlot==3 &&
          returned.SpriteGroups[^1].Members[1].Tile==0x25 &&
          returned.SpriteGroups[^1].CapturedFrame==120,
          "snapshot group OAM membership roundtrip");
    Check(returned.Dialogues.Count==3 &&
          returned.Dialogues[0].Languages["ja"]=="こんばんは",
          "Unicode localization roundtrip");
    Check(returned.Dialogues[0].HasViewportRegion &&
          returned.Dialogues[0].ViewX==24 &&
          returned.Dialogues[0].ViewWidth==160,
          "authored dialogue viewport region roundtrip");
    Check(returned.Dialogues[0].Trigger=="observed-actor-script" &&
          returned.Dialogues[0].SourceObjectSlot==4 &&
          returned.Dialogues[0].SourceGeneration==1 &&
          returned.Dialogues[0].SourceScriptId==0x1B,
          "original actor script transition binding roundtrip");
    Check(returned.Dialogues[1].Trigger=="original-room-message" &&
          returned.Dialogues[1].SourceMessageStage==2 &&
          returned.Dialogues[1].SourceMessageByte==0x34,
          "authenticated original room-message source byte roundtrip");
    Check(returned.Dialogues[2].Trigger=="original-ec47-formatter" &&
          returned.Dialogues[2].SourceMessageStage==2 &&
          returned.Dialogues[2].SourceMessageByte==0x32,
          "authenticated EC47 original formatter binding roundtrip");
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
    File.WriteAllText(file,"""{"SchemaVersion":1,"SpriteGroups":[{"Members":[{"OamSlot":100}]}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"invalid OAM member index rejected");
    File.WriteAllText(file,"""{"SchemaVersion":1,"SpriteGroups":[{"OriginalObjects":[{"ObjectSlot":28,"Generation":1}]}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"source object slot limit enforced");
    File.WriteAllText(file,"""{"SchemaVersion":1,"Dialogues":[{"Trigger":"observed-actor-script","SourceObjectSlot":28,"SourceGeneration":1,"SourceScriptId":27}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"invalid source script trigger rejected");
    File.WriteAllText(file,"""{"SchemaVersion":1,"Dialogues":[{"Trigger":"original-room-message","SourceMessageStage":5,"SourceMessageByte":52}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"invalid source room-message selector rejected");
    File.WriteAllText(file,"""{"SchemaVersion":1,"Dialogues":[{"Trigger":"original-ec47-formatter","SourceMessageStage":-1,"SourceMessageByte":50}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"unbound EC47 source-stage rejected");
    File.WriteAllText(file,"""{"SchemaVersion":1,"Dialogues":[{"HasViewportRegion":true,"ViewX":999}]}""");
    rejected=false;
    try{_ = StudioProjectFile.Load(file);}
    catch(InvalidDataException){rejected=true;}
    Check(rejected,"out of bounds dialogue marker rejected");
}
finally {File.Delete(file);}
Console.WriteLine("PASS NEStudio v1 project, sprite layers, multilingual dialogue, text flow and timeline round-trip");
