using System.IO;

namespace NEStudio;

/// <summary>
/// Resolve legacy game BAT paths without executing CMD or PowerShell.
/// The only runtime target is the ROM-authenticated owner-private native game.
/// Actual ROM SHA and session-bridge validation happen in NativeGameHost.
/// </summary>
public static class GameLaunchResolver
{
    public static string Resolve(string requested,string? ownerProfile=null)
    {
        if(!File.Exists(requested))
            throw new FileNotFoundException("The selected game file does not exist.",requested);
        string path=Path.GetFullPath(requested);
        string extension=Path.GetExtension(path).ToLowerInvariant();
        if(extension==".exe")return path;
        if(extension is not (".bat" or ".cmd"))
            throw new InvalidDataException("Select a native game EXE or legacy game launcher.");

        // Critically, NOTHING in this function launches or evaluates the BAT.
        // Even Build-And-Play.bat and Build-Private-Game.bat resolve to an
        // already-compiled private game (or produce an actionable failure).
        string folder=Path.GetDirectoryName(path)!;
        string profile=ownerProfile??Environment.GetFolderPath(
            Environment.SpecialFolder.UserProfile);
        string[] candidates=
        {
            Path.Combine(folder,"jp_akumajou_densetsu.exe"),
            Path.Combine(folder,"AlphaCandidate","jp_akumajou_densetsu.exe"),
            Path.Combine(profile,"NEStudio-Preview","AlphaCandidate","jp_akumajou_densetsu.exe")
        };
        foreach(string candidate in candidates)
            if(File.Exists(candidate) &&
               File.Exists(Path.Combine(Path.GetDirectoryName(candidate)!,
                                        "NEStudio-RomPath.txt")))
                return candidate;

        throw new FileNotFoundException(
            "The BAT is not a game viewport. Build the private NEStudio game " +
            "with Build-Private-Game.bat, then select " +
            @"%USERPROFILE%\NEStudio-Preview\AlphaCandidate\jp_akumajou_densetsu.exe" +
            ". No external console was opened.",path);
    }
}
