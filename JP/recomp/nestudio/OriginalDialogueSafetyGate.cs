namespace NEStudio;

/// <summary>
/// No runtime patch mechanism. An authored entry may be previewed only against
/// its own verified source event and exact original byte-buffer commitment.
/// </summary>
public static class OriginalDialogueSafetyGate
{
    public static ReplacementPreview Validate(
        StudioDialogue? entry,uint sceneRoom,StudioEc47Trace? trace,
        OriginalCommandPreview? captured,string authoredText)
    {
        if(entry is null || trace is null || captured is null)
            return ReplacementPreview.Block(
                "Missing dialogue, verified formatter trace or original command snapshot.");
        if(entry.Trigger!="original-ec47-formatter")
            return ReplacementPreview.Block("Entry is not bound to an original $EC47 formatter call.");
        if(!trace.Returned || trace.Sequence<=0 ||
           trace.SourceBank!=0x0A || trace.EntryPc!=0xEC47 ||
           trace.CallerPc!=0xB8FF)
            return ReplacementPreview.Block("Original formatter call ancestry/return is not verified.");
        if(entry.Room!=sceneRoom ||
           entry.SourceMessageStage!=trace.Stage ||
           entry.SourceMessageByte!=trace.Token)
            return ReplacementPreview.Block("Original source event does not match this authored entry.");
        if(trace.QueueEnd<trace.QueueStart ||
           trace.QueueEnd-trace.QueueStart!=captured.OriginalBytes.Length)
            return ReplacementPreview.Block("Original command extent changed or wrapped.");
        if(!OriginalGlyphCodec.TryParse(captured.OriginalBytes,
              out OriginalCommandPreview? proof,out _) ||
           proof is null || proof.SourceSha256!=captured.SourceSha256)
            return ReplacementPreview.Block("Original command snapshot digest mismatch.");
        if(entry.SourceCommandSha256.Length!=0 &&
           !string.Equals(entry.SourceCommandSha256,captured.SourceSha256,
                          StringComparison.Ordinal))
            return ReplacementPreview.Block("Source command has changed since the draft was bound.");
        return OriginalGlyphCodec.PreviewReplacement(captured,authoredText);
    }
}
