using System.Security.Cryptography;
using System.Text;

namespace NEStudio;

/// <summary>
/// Interprets the verified original bank00:$966A formatter command output:
/// each row is $01, VRAM low, VRAM high, tile bytes, $FF separator.
/// $FE is a SOURCE-stream row separator consumed by the formatter; it
/// must not appear in this output. These are presentation tile IDs,
/// not Unicode/Japanese glyph IDs. No native memory mutation occurs.
/// </summary>
public sealed record OriginalTileRow(int VramAddress,byte[] Tiles)
{
    public string Label => $"VRAM ${VramAddress:X4}: "+
        string.Concat(Tiles.Select(OriginalGlyphCodec.DescribeTile));
}
public sealed record OriginalCommandPreview(IReadOnlyList<OriginalTileRow> Rows,
    string SourceSha256,byte[] OriginalBytes);

public sealed record ReplacementPreview(bool Allowed,string Explanation,
    string SourceSha256,string CandidateHex,int OriginalBytes,int CandidateBytes)
{
    public static ReplacementPreview Block(string reason) =>
        new(false,reason,"","",0,0);
}

public static class OriginalGlyphCodec
{
    // The original JP ending credits at source indices $32..$66 demonstrate
    // sequential tile IDs $C0..$D9 spelling English uppercase A..Z.
    // Punctuation $F6-$FA and other tiles retain raw identities until
    // CHR/font evidence proves their exact visual/glyph meaning.
    public static string DescribeTile(byte tile) =>
        tile==0?" ":tile is >=0xC0 and <=0xD9?
            ((char)('A'+tile-0xC0)).ToString():$"<{tile:X2}>";

    public static bool TryParse(ReadOnlySpan<byte> command,
        out OriginalCommandPreview? preview,out string reason)
    {
        preview=null;
        if(command.Length<5 || command.Length>256)
        {
            reason="Command snapshot must contain 5..256 bytes.";return false;
        }
        var rows=new List<OriginalTileRow>();
        int pos=0;
        while(pos<command.Length && rows.Count<16)
        {
            if(command[pos++]!=0x01 || command.Length-pos<3)
            {
                reason="Unknown original formatter command marker or truncated row.";
                return false;
            }
            int address=command[pos]|command[pos+1]<<8;
            pos+=2;
            // The original formatter may also feed CHR/palette commands.
            // A text-only replacement must not touch such destinations.
            if(address<0x2000 || address>=0x3000)
            {
                reason=$"Destination ${address:X4} is outside nametable VRAM.";return false;
            }
            int from=pos;
            while(pos<command.Length && command[pos]!=0xFF)
            {
                if(command[pos]==0xFE)
                {
                    reason="Unconsumed source $FE control in output command.";
                    return false;
                }
                ++pos;
            }
            int length=pos-from;
            if(pos==command.Length || length==0 ||
                length>64 || (address&0x3FF)+length>0x3C0)
            {
                reason="Missing row terminator, empty/oversized text, or attribute-table overflow.";
                return false;
            }
            rows.Add(new OriginalTileRow(address,command.Slice(from,length).ToArray()));
            ++pos; // original queued $FF row terminator
        }
        if(rows.Count==0 || pos!=command.Length)
        {
            reason="Empty command or unsupported number of original rows.";
            return false;
        }
        byte[] original=command.ToArray();
        preview=new OriginalCommandPreview(rows,
            Convert.ToHexString(SHA256.HashData(original)).ToLowerInvariant(),
            original);
        reason="Source-backed command rows decoded; unknown tile IDs remain raw.";
        return true;
    }

    /// <summary>
    /// Strict original-geometry, no guest writes. The target rows and byte
    /// counts remain identical, unused cells fill with the established
    /// original $00 blank tile. Supports ASCII A-Z, a-z and spaces only.
    /// </summary>
    public static ReplacementPreview PreviewReplacement(
        OriginalCommandPreview? source,string authoredText)
    {
        if(source is null)return ReplacementPreview.Block(
            "No completed, authenticated original formatter command snapshot.");
        string normalized=(authoredText??"").Replace("\r\n","\n").Replace('\r','\n');
        string[] lines=normalized.Split('\n');
        if(lines.Length!=source.Rows.Count)
            return ReplacementPreview.Block(
                $"Replacement requires exactly {source.Rows.Count} original text rows.");
        var result=new List<byte>(source.OriginalBytes.Length);
        for(int i=0;i<lines.Length;++i)
        {
            OriginalTileRow row=source.Rows[i];
            if(lines[i].Length>row.Tiles.Length)
                return ReplacementPreview.Block(
                    $"Row {i+1}: {lines[i].Length} characters exceed original {row.Tiles.Length} cells.");
            result.Add(0x01);
            result.Add((byte)row.VramAddress);
            result.Add((byte)(row.VramAddress>>8));
            foreach(char c in lines[i])
            {
                if(c==' ')result.Add(0);
                else if(c is >= 'A' and <= 'Z')result.Add((byte)(0xC0+c-'A'));
                else if(c is >= 'a' and <= 'z')result.Add((byte)(0xC0+c-'a'));
                else return ReplacementPreview.Block(
                    $"Unsupported character U+{(int)c:X4} in row {i+1}; no verified original glyph mapping.");
            }
            while(result.Count < RowEndOffset(source.Rows,i))
                result.Add(0); // exact original row capacity
            result.Add(0xFF);
        }
        byte[] candidate=result.ToArray();
        if(candidate.Length!=source.OriginalBytes.Length)
            return ReplacementPreview.Block("Candidate changed original command geometry.");
        if(!TryParse(candidate,out var check,out _) ||
           check!.Rows.Count!=source.Rows.Count ||
           check.Rows.Where((r,i)=>r.VramAddress!=source.Rows[i].VramAddress ||
               r.Tiles.Length!=source.Rows[i].Tiles.Length).Any())
            return ReplacementPreview.Block("Candidate failed exact VRAM and tile geometry parity.");
        return new ReplacementPreview(true,
            "DRY RUN ONLY. Original nametable destinations and tile counts preserved; no guest writes permitted.",
            source.SourceSha256,Convert.ToHexString(candidate),
            source.OriginalBytes.Length,candidate.Length);
    }

    // Expected byte offset just before this row's original $FF.
    private static int RowEndOffset(IReadOnlyList<OriginalTileRow> rows,int target)
    {
        int length=0;
        for(int i=0;i<=target;++i)
            length+=3+rows[i].Tiles.Length+(i==target?0:1);
        return length;
    }
}
