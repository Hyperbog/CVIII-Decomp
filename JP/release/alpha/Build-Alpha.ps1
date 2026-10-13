# Windows x64 0.2.0-alpha.1 PRIVATE Original/Enhanced compiler/packager.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Rom,
 [string]$OutDir=(Join-Path $env:USERPROFILE 'CVIII-Alpha'),
 [string]$ProjectRoot='',
 [switch]$PlayAfterBuild
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
function Invoke-Checked([string]$Program,[string[]]$Args) {
 & $Program @Args
 if ($LASTEXITCODE -ne 0) { throw "$Program failed (exit $LASTEXITCODE)" }
}
foreach ($command in @('git','cmake','python')) {
 if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
  throw "Missing dependency $command. See README_ALPHA.md."
 }
}
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$outPath=[IO.Path]::GetFullPath($OutDir)
[IO.Directory]::CreateDirectory($outPath) | Out-Null
if ($ProjectRoot) {
 $repoPath=(Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path
} else {
 $repoPath=Join-Path $outPath '_cviisource'
 if (-not (Test-Path -LiteralPath $repoPath)) {
  Invoke-Checked 'git' @('clone','--branch','decompilation','--single-branch',
      'https://github.com/Hyperbog/CVIII-Decomp.git',$repoPath)
 } else {
  # This directory is managed by this builder; do not silently compile
  # a stale branch when new asset/gameplay tooling has been committed.
  Invoke-Checked 'git' @('-C',$repoPath,'pull','--ff-only','origin','decompilation')
 }
}
$buildScript=Join-Path $repoPath 'JP/tools/build_retail_cycle_0575.py'
if (-not (Test-Path -LiteralPath $buildScript)) {
 throw 'CVIII repository missing original-JP C11 compiler entry point.'
}
$privateOut=Join-Path $outPath '_private_original_rom_build'
Write-Host 'Compiling the original Japanese game to native C11 with SDL2...'
Invoke-Checked 'python' @($buildScript,'--rom',$romPath,'--out',$privateOut,'--windowed','--build-only')
$reportPath=Join-Path $privateOut 'jp0575_build_report.json'
if (-not (Test-Path -LiteralPath $reportPath)) {throw 'No compiler build report was produced.'}
$report=Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if (-not $report.build_completed -or $report.frame_execution_attempted) {
 throw 'Native compilation failed or was incorrectly reported.'
}
$program=[IO.Path]::GetFullPath([string]$report.runner)
if (-not (Test-Path -LiteralPath $program) -or
    [IO.Path]::GetExtension($program).ToLowerInvariant() -ne '.exe') {
 throw "Windows game executable not found: $program"
}
$binDir=Split-Path -Parent $program
$sdl=Join-Path $binDir 'SDL2.dll'
if (-not (Test-Path -LiteralPath $sdl)) {
 throw 'SDL2.dll is missing. Refusing headless binary as a playable alpha.'
}
$stage=Join-Path $outPath 'AlphaCandidate'
[IO.Directory]::CreateDirectory($stage) | Out-Null
Copy-Item -LiteralPath $program -Destination (Join-Path $stage 'jp_akumajou_densetsu.exe') -Force
Copy-Item -LiteralPath $sdl -Destination $stage -Force
# JP0597: generate/cache an authenticated, local ROM-derived CHR asset
# archive once per private candidate. Neither public CI nor Git sees it.
$assetBuilder=Join-Path $repoPath 'JP/tools/jp_asset_pack_0597.py'
if (-not (Test-Path -LiteralPath $assetBuilder)) { throw "Missing JP0597 asset builder" }
$assetPack=Join-Path $stage 'CVIII-Assets.bin'
Write-Host 'Verifying or creating private CVIII-Assets.bin...'
Invoke-Checked 'python' @($assetBuilder,'--build','--rom',$romPath,'--out',$assetPack)
if (-not (Test-Path -LiteralPath $assetPack)) { throw 'Asset cache was not created' }
# JP0598: export verified 2bpp and indexed pixels into a fixed-size C11
# reader format; private native code imports it without touching NES state.
$assetIndexTool=Join-Path $repoPath 'JP/tools/jp_asset_runtime_0598.py'
if (-not (Test-Path -LiteralPath $assetIndexTool)) { throw "Missing JP0598 runtime index exporter" }
$assetIndex=Join-Path $stage 'CVIII-CHR-Index.dat'
Invoke-Checked 'python' @($assetIndexTool,'--export','--assets',$assetPack,'--out',$assetIndex)
if (-not (Test-Path -LiteralPath $assetIndex)) { throw 'CHR index export missing' }

$launch=Join-Path $PSScriptRoot 'Launch-Alpha.ps1'
if (-not (Test-Path -LiteralPath $launch)) {
 $launch=Join-Path $repoPath 'JP/release/alpha/Launch-Alpha.ps1'
}
Copy-Item -LiteralPath $launch -Destination $stage -Force
$notes=Join-Path $PSScriptRoot 'README_ALPHA.md'
if (-not (Test-Path -LiteralPath $notes)) {
 $notes=Join-Path $repoPath 'JP/release/alpha/README_ALPHA.md'
}
Copy-Item -LiteralPath $notes -Destination $stage -Force
foreach ($name in @('Play-Original.bat','Play-Enhanced.bat','Play-Alpha.bat','Debug-Stage-Companion.bat')) {
 $src=Join-Path $repoPath ('JP/release/alpha/'+$name)
 if (-not (Test-Path -LiteralPath $src)) {throw "Missing alpha launcher: $src"}
 Copy-Item -LiteralPath $src -Destination $stage -Force
}
foreach ($name in @('jp_password_stage_0593.py','jp_password_debug_menu_0593.py','jp_asset_pack_0597.py','jp_asset_runtime_0598.py')) {
 $src=Join-Path $repoPath ('JP/tools/'+$name)
 if (-not (Test-Path -LiteralPath $src)) {throw "Missing debug password helper: $src"}
 Copy-Item -LiteralPath $src -Destination $stage -Force
}
$engine=Join-Path $privateOut '_external/nesrecomp'
$licenses=Join-Path $stage 'licenses'
[IO.Directory]::CreateDirectory($licenses) | Out-Null
$upstreamLicense=Join-Path $engine 'LICENSE'
$sdlLicense=Join-Path $engine 'runner/external/SDL2/COPYING.txt'
if (-not (Test-Path -LiteralPath $upstreamLicense) -or -not (Test-Path -LiteralPath $sdlLicense)) {
 throw 'Required third-party licenses are unavailable.'
}
Copy-Item -LiteralPath $upstreamLicense -Destination (Join-Path $licenses 'NESRecomp-LICENSE.txt') -Force
Copy-Item -LiteralPath $sdlLicense -Destination (Join-Path $licenses 'SDL2-COPYING.txt') -Force
$manifest=[ordered]@{
 schema='CVIII-windows-alpha-candidate/v2'
 version='0.2.0-alpha.1'
 runtime='generated native C11 2A03/VRC6 cycle backend'
 original_rom_sha256='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
 game_exe_sha256=(Get-FileHash -LiteralPath (Join-Path $stage 'jp_akumajou_densetsu.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
 gameplay_verified=$false
 playable_alpha_qualified=$false
 original_enhanced_options=$true
 extra_sprite_compositor_experimental=$true
 shared_background_bug_fixed=$false
 widescreen_implemented=$false
 individual_audio_channels_implemented=$false
 original_rom_included=$false
 debug_stage_companion_password_picker=$true
 debug_automatic_warp_implemented=$false
 assets_schema='cviii.jp.assets/v1'
 assets_sha256=(Get-FileHash -LiteralPath $assetPack -Algorithm SHA256).Hash.ToLowerInvariant()
 asset_pack_contains_original_chr=$true
 asset_pack_loaded_by_runtime=$false
 asset_chr_index_schema='CVIII-JP-native-chr-index/v1'
 asset_chr_index_sha256=(Get-FileHash -LiteralPath $assetIndex -Algorithm SHA256).Hash.ToLowerInvariant()
 enhanced_can_read_chr_index=$true
 enhanced_uses_chr_index_for_rendering=$false
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage 'ALPHA_BUILD.json') -Encoding UTF8
# Local private ZIP includes game-derived compiled instructions. Do not upload to CI.
$zip=Join-Path $outPath 'CVIII-Alpha-0.2.0-Windows-x64-PRIVATE.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host ('Native C11 build successful: '+$program)
Write-Host ('Private alpha candidate ZIP: '+$zip)
Write-Host 'Original edition has owner playtest history. New Enhanced mode needs GUI QA.'
Write-Host ('Launch using Launch-Alpha.ps1 -Rom "'+$romPath+'"')
if ($PlayAfterBuild) {
 & (Join-Path $stage 'Launch-Alpha.ps1') -Rom $romPath -Edition Original
 if ($LASTEXITCODE -ne 0) { throw "Native game failed with exit $LASTEXITCODE" }
}
