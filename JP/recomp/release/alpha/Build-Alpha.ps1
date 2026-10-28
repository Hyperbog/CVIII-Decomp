# Windows x64 0.2.0-alpha.1 PRIVATE Original/Enhanced compiler/packager.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Rom,
 [string]$OutDir=(Join-Path $env:USERPROFILE 'CVIII-Widescreen-Alpha'),
 [string]$ProjectRoot='',
 [string]$CycleSeedFile='',
 [switch]$PlayAfterBuild
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
# JP0604: Avoid PowerShell's automatic $Args variable. Always pass
# a named array of command arguments, including Git clone subcommands.
function Invoke-Checked {
 param(
  [Parameter(Mandatory=$true)][string]$Program,
  [Parameter(Mandatory=$true)][string[]]$CommandArguments
 )
 if ($CommandArguments.Count -eq 0) { throw "No arguments supplied to $Program" }
 & $Program @CommandArguments
 if ($LASTEXITCODE -ne 0) {
  throw "$Program failed (exit $LASTEXITCODE); args: $($CommandArguments -join ' ')"
 }
}
# The private AlphaCandidate consumes files from three distinct directories.
# Keep the manifest in one function: packager and ROM-free Windows CI
# inspect the SAME source list before any commercial-ROM C11 compile.
function Get-CviiiAlphaCompanionSources {
 param([Parameter(Mandatory=$true)][string]$RepoPath)
 $bundles=@(
  @{ Directory='JP/recomp/release/alpha'; Names=@('Play-CVIII.bat','Debug-Stage-Companion.bat','Capture-QA-0602.ps1','Build-And-Play.ps1','Build-And-Play.bat','Resolve-Python.ps1','Control-Profiles.py','Controls.ps1','Controls.bat') }
  @{ Directory='JP/decomp/tools'; Names=@('jp_password_stage_0593.py','jp_password_debug_menu_0593.py','jp_qa_matrix_0602.py','jp_mapper_audit_0602.py','jp_mesen_sound_requests_0615.py','mesen_jp_sound_requests_0615.lua','jp_sound_priority_paths_0616.py','jp_mesen_gate_report_0616.py','mesen_jp_sound_gates_0616.lua','jp_sound_decision_reference_0617.py','mesen_jp_sound_decisions_0617.lua','jp_audio_ui_chr_0619.py') }
  @{ Directory='JP/recomp/tools'; Names=@('jp_asset_pack_0597.py','jp_asset_runtime_0598.py','jp_chr_fetch_report_0600.py','jp_frame_evidence_report_0601.py','jp_nt_trace_report_0606.py','jp_object_oam_report_0609.py','jp_audio_bus_report_0610.py','jp_audio_session_verify_0614.py') }
 )
 foreach ($bundle in $bundles) {
  foreach ($name in $bundle.Names) {
   [pscustomobject]@{
    Name=$name
    Source=(Join-Path $RepoPath ($bundle.Directory+'/'+$name))
   }
  }
 }
}
foreach ($command in @('git','cmake')) {
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
  Invoke-Checked -Program 'git' -CommandArguments @('clone','--branch','jp0723-ppu-queue-decoder','--single-branch',
      'https://github.com/Hyperbog/CVIII-Decomp.git',$repoPath)
 } else {
  # This directory is managed by this builder; do not silently compile
  # a stale branch when new asset/gameplay tooling has been committed.
  Invoke-Checked -Program 'git' -CommandArguments @('-C',$repoPath,'pull','--ff-only','origin','jp0723-ppu-queue-decoder')
 }
}
# The private widescreen kit must never silently compile the older baseline.
$worldHost=Join-Path $repoPath 'JP/recomp/native/enhanced/cviii_stage1_host_0725.c'
if (-not (Test-Path -LiteralPath $worldHost -PathType Leaf)) {
 throw 'Wrong source checkout: the Stage 1 widescreen host is missing.'
}
if (-not $ProjectRoot) {
 $sourceBranch=(& git -C $repoPath branch --show-current).Trim()
 if ($LASTEXITCODE -ne 0 -or $sourceBranch -ne 'jp0723-ppu-queue-decoder') {
  throw ('Wrong native source branch: '+$sourceBranch+'. Expected jp0723-ppu-queue-decoder.')
 }
}
$sourceRevision=(& git -C $repoPath rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $sourceRevision -notmatch '^[0-9a-f]{40}$') {
 throw 'Cannot verify native widescreen source revision.'
}
Write-Host ('Widescreen Enhanced native source revision: '+$sourceRevision)
# Fail before compiling if the kit would be impossible to stage.
$companionSources=@(Get-CviiiAlphaCompanionSources -RepoPath $repoPath)
if ($companionSources.Count -ne 29) {
 throw 'Private AlphaCandidate companion source manifest is incomplete.'
}
foreach ($item in $companionSources) {
 if (-not (Test-Path -LiteralPath $item.Source -PathType Leaf)) {
  throw ('Private AlphaCandidate source missing before build: '+$item.Source)
 }
}
# Resolve AFTER refreshing Git; an older kit can use the current resolver.
$pythonResolver=Join-Path $repoPath 'JP/recomp/release/alpha/Resolve-Python.ps1'
if (-not (Test-Path -LiteralPath $pythonResolver)) {
 throw "Python resolver missing from synchronized repository: $pythonResolver"
}
. $pythonResolver
$pyCmd=Resolve-CviiiPython
Write-Host ('Using verified Python interpreter: '+$pyCmd.Executable+' '+($pyCmd.Prefix -join ' '))
$buildScript=Join-Path $repoPath 'JP/recomp/tools/build_retail_cycle_0575.py'
if (-not (Test-Path -LiteralPath $buildScript)) {
 throw 'CVIII repository missing original-JP C11 compiler entry point.'
}
$privateOut=Join-Path $outPath '_private_original_rom_build'
Write-Host 'Compiling the original Japanese game to native C11 with SDL2...'
$nativeArgs=@($buildScript,'--rom',$romPath,'--out',$privateOut,'--windowed','--build-only')
if ($CycleSeedFile) {
 $seedPath=(Resolve-Path -LiteralPath $CycleSeedFile -ErrorAction Stop).Path
 $nativeArgs+=@('--seed-file',$seedPath)
 Write-Host 'Compiling additional original-JP PRG instruction entries from owner-private bank-qualified seeds.'
}
Invoke-Checked -Program $pyCmd.Executable -CommandArguments (@($pyCmd.Prefix) + $nativeArgs)
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
# Only package the optional acceptance command when both files exist in
# the synchronized source checkout. The baseline decompilation branch does
# not yet contain the draft feature; it must remain independently buildable.
$coverageTool=Join-Path $repoPath 'JP/recomp/tools/verify_compiled_product.py'
$coverageLauncher=Join-Path $repoPath 'JP/recomp/release/alpha/Verify-Compiled.ps1'
$hasVerifier=Test-Path -LiteralPath $coverageTool -PathType Leaf
$hasLauncher=Test-Path -LiteralPath $coverageLauncher -PathType Leaf
if ($hasVerifier -and $hasLauncher) {
 Copy-Item -LiteralPath $coverageTool -Destination (Join-Path $stage 'Verify-Compiled.py') -Force
 Copy-Item -LiteralPath $coverageLauncher -Destination (Join-Path $stage 'Verify-Compiled.ps1') -Force
 $roundtripTool=Join-Path $repoPath 'JP/recomp/tools/verify_enhanced_save_roundtrip.py'
 if (Test-Path -LiteralPath $roundtripTool -PathType Leaf) {
  Copy-Item -LiteralPath $roundtripTool -Destination (Join-Path $stage 'Verify-SaveRoundtrip.py') -Force
 }
} elseif ($hasVerifier -or $hasLauncher) {
 throw 'Incomplete compiled-product verifier source; refusing partial private package.'
} else {
 Write-Host 'Optional compiled PRG acceptance unavailable in this source revision; gameplay build unchanged.'
}
# JP0597: generate/cache an authenticated, local ROM-derived CHR asset
# archive once per private candidate. Neither public CI nor Git sees it.
$assetBuilder=Join-Path $repoPath 'JP/recomp/tools/jp_asset_pack_0597.py'
if (-not (Test-Path -LiteralPath $assetBuilder)) { throw "Missing JP0597 asset builder" }
$assetPack=Join-Path $stage 'CVIII-Assets.bin'
Write-Host 'Verifying or creating private CVIII-Assets.bin...'
Invoke-Checked -Program $pyCmd.Executable -CommandArguments (@($pyCmd.Prefix) + @($assetBuilder,'--build','--rom',$romPath,'--out',$assetPack))
if (-not (Test-Path -LiteralPath $assetPack)) { throw 'Asset cache was not created' }
# JP0598: export verified 2bpp and indexed pixels into a fixed-size C11
# reader format; private native code imports it without touching NES state.
$assetIndexTool=Join-Path $repoPath 'JP/recomp/tools/jp_asset_runtime_0598.py'
if (-not (Test-Path -LiteralPath $assetIndexTool)) { throw "Missing JP0598 runtime index exporter" }
$assetIndex=Join-Path $stage 'CVIII-CHR-Index.dat'
Invoke-Checked -Program $pyCmd.Executable -CommandArguments (@($pyCmd.Prefix) + @($assetIndexTool,'--export','--assets',$assetPack,'--out',$assetIndex))
if (-not (Test-Path -LiteralPath $assetIndex)) { throw 'CHR index export missing' }

# Always package the just-synchronized repo launcher; older kits must not
# overwrite the current build's CLI with an obsolete copy.
$launch=Join-Path $repoPath 'JP/recomp/release/alpha/Launch-Alpha.ps1'
if (-not (Test-Path -LiteralPath $launch)) { throw 'Current repo launcher missing' }
Copy-Item -LiteralPath $launch -Destination $stage -Force
$notes=Join-Path $repoPath 'JP/recomp/release/alpha/README_ALPHA.md'
if (-not (Test-Path -LiteralPath $notes)) { throw 'Current repo README missing' }
Copy-Item -LiteralPath $notes -Destination $stage -Force
# The source manifest was validated before native compilation.
foreach ($item in $companionSources) {
 Copy-Item -LiteralPath $item.Source -Destination (Join-Path $stage $item.Name) -Force
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
 native_source_revision=$sourceRevision
 native_source_branch='jp0723-ppu-queue-decoder'
 enhanced_stage1_widescreen_available=$true
 enhanced_widescreen_scope='Stage 1 authenticated atlas; other stages retain original viewport'
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
 jp0602_owner_local_scene_qa=$true
 jp0602_renderer_parity_certified=$false
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $stage 'ALPHA_BUILD.json') -Encoding UTF8
# Previous private candidates could retain obsolete public Original/Enhanced
# shortcut files from earlier builds. Remove shortcuts only, never save states.
foreach ($legacy in @('Play-Original.bat','Play-Enhanced.bat','Play-Alpha.bat')) {
 $obsolete=Join-Path $stage $legacy
 if (Test-Path -LiteralPath $obsolete) { Remove-Item -LiteralPath $obsolete -Force }
}
# Local private ZIP includes game-derived compiled instructions. Do not upload to CI.
$zip=Join-Path $outPath 'CVIII-Alpha-0.2.0-Windows-x64-PRIVATE.zip'
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
Write-Host ('Native C11 build successful: '+$program)
Write-Host ('Private alpha candidate ZIP: '+$zip)
Write-Host 'Enhanced is the public edition; reference-only original PPU comparisons remain internal.'
Write-Host ('Launch using Launch-Alpha.ps1 -Rom "'+$romPath+'"')
if ($PlayAfterBuild) {
 & (Join-Path $stage 'Launch-Alpha.ps1') -Rom $romPath -Edition Enhanced
 if ($LASTEXITCODE -ne 0) { throw "Native game failed with exit $LASTEXITCODE" }
}
