# Builds a standalone Windows NEStudio application without touching
# the owner's existing CVIII-Alpha or CVIII-Lighting-Preview installation.
[CmdletBinding()]
param(
    [string]$OutDir=(Join-Path $env:USERPROFILE 'NEStudio-Preview'),
    [string]$GameFolder='',
    [switch]$Launch
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw 'NEStudio requires the .NET 8 SDK. Install .NET 8, then rerun Build-NEStudio.ps1.'
}
$target=[IO.Path]::GetFullPath($OutDir)
[IO.Directory]::CreateDirectory($target) | Out-Null
Write-Host "Building ROM-free NEStudio desktop at $target"
& dotnet publish (Join-Path $PSScriptRoot 'NEStudio.csproj') -c Release -r win-x64 --self-contained false -o $target
if ($LASTEXITCODE -ne 0) {throw 'NEStudio Windows publish failed.'}
$exe=Join-Path $target 'NEStudio.exe'
if (-not (Test-Path -LiteralPath $exe)) {throw 'NEStudio.exe was not generated.'}
$starter=''
if ($GameFolder) {
    $folder=(Resolve-Path -LiteralPath $GameFolder).Path
    $game=Join-Path $folder 'jp_akumajou_densetsu.exe'
    $sdl=Join-Path $folder 'SDL2.dll'
    if (-not (Test-Path $game) -or -not (Test-Path $sdl)) {
        throw 'GameFolder must contain the privately built game EXE and SDL2.dll.'
    }
    $nativeLauncher=Join-Path $folder 'Launch-NEStudio-Game.bat'
    if (-not (Test-Path -LiteralPath $nativeLauncher -PathType Leaf)) {
        throw 'GameFolder needs Launch-NEStudio-Game.bat from the bridge-compatible private preview build. Run Preview-NEStudio.bat first.'
    }
    # Store the actual game EXE in the project. Run / Attach launches
    # this binary directly using NEStudio-RomPath.txt and its private
    # CHR index: it must never execute a .bat/cmd launcher.
    $game=Join-Path $folder 'jp_akumajou_densetsu.exe'
    $hint=Join-Path $folder 'NEStudio-RomPath.txt'
    if (-not (Test-Path -LiteralPath $hint -PathType Leaf)) {
        throw 'Private game is missing NEStudio-RomPath.txt. Re-run Build-Private-Game.bat.'
    }
    $starter=Join-Path $target 'EnhancedProject.nestudio'
    $payload=[ordered]@{
       SchemaVersion=1
       Name='Castlevania III Enhanced'
       GameExecutable=$game
       SpriteGroups=@(
         @{Id='scene.background';Name='Background';Layer='Behind Game';Room=0;Visible=$true},
         @{Id='scene.sprites';Name='World Sprites';Layer='World';Room=0;Visible=$true},
         @{Id='scene.foreground';Name='Foreground';Layer='Above Game';Room=0;Visible=$true}
       )
       Dialogues=@()
       Events=@()
       Assets=@()
    }
    $payload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $starter -Encoding utf8
    Write-Host ('Linked private Enhanced executable for direct embedded viewport: '+$game)
}
Write-Host ('NEStudio ready: '+$exe)
if ($Launch) {
    if ($starter) { Start-Process -FilePath $exe -ArgumentList ('"'+$starter+'"') }
    else { Start-Process -FilePath $exe }
}
