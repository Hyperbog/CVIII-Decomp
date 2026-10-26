# CVIII native PC Alpha 0.2 — Original/Enhanced owner-only launcher.
[CmdletBinding()]
param(
 [string]$Rom='',
 [ValidateSet('Original','Enhanced')][string]$Edition='Enhanced',
 [switch]$UnlimitedSprites,
 [switch]$StableSprites,
 [string]$ControlsProfile='',
 [switch]$SpriteTrace,
 [switch]$AudioTrace,
 [ValidateRange(0,100)][int]$MasterVolume,
 [switch]$AudioUiPreview,
 [switch]$ChrAudit,
 [string]$AuditOutDir=''
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if (-not $Rom) {
 $nearby=Join-Path $PSScriptRoot 'Akumajou Densetsu (Japan).nes'
 if (Test-Path -LiteralPath $nearby) {$Rom=$nearby}
}
if (-not $Rom) {
 Add-Type -AssemblyName System.Windows.Forms
 $picker=New-Object System.Windows.Forms.OpenFileDialog
 $picker.Title='Select original Japanese Akumajou Densetsu ROM'
 $picker.Filter='NES cartridge (*.nes)|*.nes'
 if ($picker.ShowDialog() -ne 'OK') {throw 'No Japanese ROM selected.'}
 $Rom=$picker.FileName
}
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$expected='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$actual=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {throw 'Wrong ROM: original Japanese mapper24 required.'}
$game=Join-Path $PSScriptRoot 'jp_akumajou_densetsu.exe'
if (-not (Test-Path -LiteralPath $game)) {
 $game=Join-Path $PSScriptRoot 'CVIII_Alpha.exe'
}
$dll=Join-Path $PSScriptRoot 'SDL2.dll'
if (-not (Test-Path -LiteralPath $game) -or -not (Test-Path -LiteralPath $dll)) {
 throw ('The folder contains the ROM-free build kit, not the compiled private game. '+
        'Run Build-And-Play.bat from the extracted kit to compile with your original JP ROM. '+
        'The game EXE and SDL2.dll will be created together under '+
        (Join-Path $env:USERPROFILE 'CVIII-Alpha\AlphaCandidate')+
        '. Do not download an unrelated SDL2.dll.')
}
# JP0750: Only explicit launch switches override saved renderer preferences.
# Previous launcher always passed --stable-sprites 0 and --unlimited-sprites 0
# by default, undoing the persisted Enhanced sprite stabilization each launch.
# Keep the experimental compositor opt-in until the owner validates retail play.
function Get-CviiiSpriteLaunchOptions {
 param(
  [string]$Edition,
  [bool]$UnlimitedSprites,
  [bool]$StableSprites,
  [bool]$OverrideUnlimited,
  [bool]$OverrideStable
 )
 if ($OverrideUnlimited) {
  '--unlimited-sprites'
  if ($Edition -eq 'Enhanced' -and $UnlimitedSprites) {'1'} else {'0'}
 }
 if ($OverrideStable) {
  '--stable-sprites'
  if ($Edition -eq 'Enhanced' -and $StableSprites) {'1'} else {'0'}
 }
}
$extraSpriteArgs=@(Get-CviiiSpriteLaunchOptions -Edition $Edition `
    -UnlimitedSprites ([bool]$UnlimitedSprites) `
    -StableSprites ([bool]$StableSprites) `
    -OverrideUnlimited ($PSBoundParameters.ContainsKey('UnlimitedSprites')) `
    -OverrideStable ($PSBoundParameters.ContainsKey('StableSprites')))
if ($extraSpriteArgs.Count) {
 Write-Host ('Explicit host-only sprite presentation override: '+($extraSpriteArgs -join ' '))
} else {
 Write-Host 'Sprite options: using saved settings from config.ini (no launcher override).'
}
Write-Host 'Controls: arrows=D-pad, Z=A, X=B, Enter=Start, Backslash=Select.'
Write-Host 'Enhanced Pause: F4 opens Save State / Load State / Audio / Quit; arrows navigate, Enter selects, Esc closes.'
Write-Host 'Pause menu uses authenticated CHR. Save/Load opens slot 0..9: Left/Right chooses, Enter confirms, Esc returns.'
Write-Host 'Enhanced audio: F6 opens original-healthbar sliders; arrows change by 1%; Esc or F6 closes.'
Write-Host 'F8/F9 save/load; builds supporting slots use Ctrl+0..9.'
if ($AuditOutDir -and -not ($ChrAudit -or $SpriteTrace -or $AudioTrace)) { throw '-AuditOutDir requires -ChrAudit, -SpriteTrace or -AudioTrace' }
$auditBase=if ($AuditOutDir) { [IO.Path]::GetFullPath($AuditOutDir) } else { $PSScriptRoot }
if ($ChrAudit -or $SpriteTrace -or $AudioTrace) {
 [IO.Directory]::CreateDirectory($auditBase) | Out-Null
 $pythonResolver=Join-Path $PSScriptRoot 'Resolve-Python.ps1'
 if (-not (Test-Path -LiteralPath $pythonResolver)) {
  throw 'Private AlphaCandidate is missing Resolve-Python.ps1. Rebuild with the latest builder.'
 }
 . $pythonResolver
 (Resolve-CviiiPython) | Out-Null
}
# JP0661: opt-in persistent keyboard Player 1 profile, applied BEFORE
# NESRecomp reads config.ini. When absent, never change user controls.
if ($ControlsProfile) {
 $profileTool=Join-Path $PSScriptRoot 'Control-Profiles.py'
 $pythonResolver=Join-Path $PSScriptRoot 'Resolve-Python.ps1'
 if (!(Test-Path -LiteralPath $profileTool -PathType Leaf) -or
     !(Test-Path -LiteralPath $pythonResolver -PathType Leaf)) {
  throw 'Controls profile helper missing; rebuild the private AlphaCandidate.'
 }
 . $pythonResolver
 Invoke-CviiiPython -Script $profileTool -Arguments @('--root',$PSScriptRoot,'--apply',$ControlsProfile)
 Write-Host ('JP0661 native Player 1 keyboard profile: '+$ControlsProfile)
}
Push-Location $PSScriptRoot
try {
 $gameArgs=@($romPath,'--edition',$Edition.ToLowerInvariant()) + $extraSpriteArgs
 if ($PSBoundParameters.ContainsKey('MasterVolume')) {
  $gameArgs+=@('--master-volume',[string]$MasterVolume)
  Write-Host ('Enhanced master output gain override: '+$MasterVolume+'%')
 }
 if ($AudioTrace) {
  $audioLog=Join-Path $auditBase 'CVIII-Audio-Registers.csv'
  $gameArgs+=@('--audio-reg-trace',$audioLog)
  Write-Host ('JP0610 original 2A03/VRC6 audio register trace: '+$audioLog)
  $requestLog=Join-Path $auditBase 'CVIII-Sound-Requests.csv'
  $gameArgs+=@('--sound-request-trace',$requestLog)
  Write-Host ('JP0612 original $E249 sound requests: '+$requestLog)
  $sessionId=([guid]::NewGuid()).ToString('N').ToLowerInvariant()
  $epochLog=Join-Path $auditBase 'CVIII-Audio-Epochs.csv'
  $gameArgs+=@('--audio-session-id',$sessionId,'--audio-epoch-trace',$epochLog)
  Write-Host ('JP0614 private audio epoch boundaries: '+$epochLog)
 }
 if ($SpriteTrace) {
  $spriteLog=Join-Path $auditBase 'CVIII-Sprite-Objects.csv'
  $gameArgs+=@('--sprite-object-trace',$spriteLog)
  Write-Host ('JP0609 actual 28 objects / rotated hardware OAM trace: '+$spriteLog)
 }
 # Enhanced can opt into verified physical CHR asset metadata without ever
 # replacing the original cartridge's timing, mapper or game framebuffer.
 if ($Edition -eq 'Enhanced') {
  # JP0727: forward the ROM already selected and SHA256-authenticated by
  # this launcher. The game decodes its Stage 1 resources in memory; no
  # build-time ROM path or manual extraction is required for this renderer.
  $gameArgs+=@('--stage1-world-rom',$romPath)
  # Optional JP0729 private resource cache: a bad/missing cache is safely
  # regenerated by the game from this same authenticated original ROM.
  # Never store original assets in the source checkout or public build kit.
  $cacheHome=[Environment]::GetFolderPath('LocalApplicationData')
  if ($cacheHome) {
   $resourceDir=Join-Path $cacheHome 'CVIII-Decomp\\ResourceCache'
   try {
    [IO.Directory]::CreateDirectory($resourceDir) | Out-Null
    $resourceCache=Join-Path $resourceDir 'japanese-vrc6-stage1-chr-v1.dat'
    $gameArgs+=@('--stage1-resource-cache',$resourceCache)
   } catch {
    Write-Warning 'Private resource cache unavailable; extracting into memory on this run.'
   }
  }
  $assetIndex=Join-Path $PSScriptRoot 'CVIII-CHR-Index.dat'
  if (Test-Path -LiteralPath $assetIndex) {
   $gameArgs+=@('--asset-index',$assetIndex)
   Write-Host 'Loading authenticated read-only CHR asset index (no rendering changes).'
   if ($AudioUiPreview) {
    $gameArgs+=@('--audio-ui-preview','1')
    Write-Host 'JP0619 noninteractive original health-bar/font overlay preview enabled.'
   }
   if ($ChrAudit) {
    $chrAuditPath=Join-Path $auditBase 'CVIII-CHR-Audit.csv'
    $gameArgs+=@('--chr-audit',$chrAuditPath)
    $fetchAuditPath=Join-Path $auditBase 'CVIII-CHR-Fetch.csv'
    $gameArgs+=@('--chr-fetch-audit',$fetchAuditPath)
    $frameEvidencePath=Join-Path $auditBase 'CVIII-Frame-Evidence.csv'
    $gameArgs+=@('--frame-evidence',$frameEvidencePath)
    $ntAuditPath=Join-Path $auditBase 'CVIII-NT-Fetch.csv'
    $gameArgs+=@('--nt-fetch-audit',$ntAuditPath)
    Write-Host ('Recording actual PPU nametable/attribute values: '+$ntAuditPath)
    Write-Host ('Recording original PPU fingerprints: '+$frameEvidencePath)
    Write-Host ('Recording sampled VRC6 mappings: '+$chrAuditPath)
    Write-Host ('Recording physical PPU CHR reads: '+$fetchAuditPath)
   }
  } else {
   if ($ChrAudit -or $AudioUiPreview) { throw 'Audio UI/CHR audit requires private CVIII-CHR-Index.dat' }
   Write-Host 'No asset index found; Enhanced falls back to original ROM-driven graphics.'
  }
 } elseif ($ChrAudit -or $AudioUiPreview) { throw 'CHR UI preview and audit require Enhanced' }
 & $game @gameArgs
 if ($LASTEXITCODE -ne 0) {throw "Native game exited with $LASTEXITCODE"}
 if ($AudioTrace) {
  $audioVerifier=Join-Path $PSScriptRoot 'jp_audio_session_verify_0614.py'
  if (!(Test-Path -LiteralPath $audioVerifier)) { throw 'JP0614 session validator missing; rebuild latest private AlphaCandidate' }
  $fileSpecs=@{
   requests=@{ name='CVIII-Sound-Requests.csv'; path=$requestLog }
   registers=@{ name='CVIII-Audio-Registers.csv'; path=$audioLog }
   epochs=@{ name='CVIII-Audio-Epochs.csv'; path=$epochLog }
  }
  $boundFiles=@{}
  foreach ($key in @('requests','registers','epochs')) {
   $item=$fileSpecs[$key]
   if (!(Test-Path -LiteralPath $item.path)) {throw ('Missing private audio capture file: '+$item.path)}
   $boundFiles[$key]=@{ name=$item.name; sha256=(Get-FileHash -LiteralPath $item.path -Algorithm SHA256).Hash.ToLowerInvariant() }
  }
  $manifestFile=Join-Path $auditBase 'CVIII-Audio-Session.json'
  $manifestData=@{ schema='CVIII-JP-audio-session/v1'; session_id=$sessionId; files=$boundFiles }
  [IO.File]::WriteAllText($manifestFile,
    (($manifestData | ConvertTo-Json -Depth 6) + [Environment]::NewLine),
    [Text.UTF8Encoding]::new($false))
  $epochSummary=Join-Path $auditBase 'CVIII-Audio-Epoch-Verification.json'
  Invoke-CviiiPython -Script $audioVerifier -Arguments @('--dir',$auditBase,'--json',$epochSummary)
  if ($LASTEXITCODE -ne 0) {throw 'JP0614 sound trace session/epoch validation failed'}
  Write-Host ('JP0614 validated session epoch boundaries: '+$epochSummary)
  $epochInfo=Get-Content -LiteralPath $epochSummary -Raw | ConvertFrom-Json
  # The older JP0610 analyzer requires one monotonically increasing
  # cycle epoch. Never apply it blindly across reset or load-state.
  if ($epochInfo.epochs.Count -eq 1) {
   $audioTool=Join-Path $PSScriptRoot 'jp_audio_bus_report_0610.py'
   if (!(Test-Path -LiteralPath $audioTool)) { throw 'JP0610 audio trace analyzer missing from private build' }
   $audioSummary=Join-Path $auditBase 'CVIII-Audio-Registers.json'
   Invoke-CviiiPython -Script $audioTool -Arguments @('--csv',$audioLog,'--json',$audioSummary)
   if ($LASTEXITCODE -ne 0) { throw 'JP0610 hardware trace invalid' }
   Write-Host ('JP0610 2A03/VRC6 single-epoch report: '+$audioSummary)
  } else {
   Write-Host 'JP0610 whole-file report omitted: use validated JP0614 epochs after load/reset.'
  }
 }
 if ($SpriteTrace -and (Test-Path -LiteralPath $spriteLog)) {
  $oamTool=Join-Path $PSScriptRoot 'jp_object_oam_report_0609.py'
  if (!(Test-Path -LiteralPath $oamTool)) {
   throw 'JP0609 object/OAM trace analyzer missing from the private build'
  }
  $oamSummary=Join-Path $auditBase 'CVIII-Sprite-Objects.json'
  Invoke-CviiiPython -Script $oamTool -Arguments @('--csv',$spriteLog,'--json',$oamSummary)
  Write-Host ('Original 28-object/OAM trace report: '+$oamSummary)
 }
 if ($ChrAudit -and (Test-Path -LiteralPath $fetchAuditPath)) {
  $summaryTool=Join-Path $PSScriptRoot 'jp_chr_fetch_report_0600.py'
  $summaryJson=Join-Path $auditBase 'CVIII-CHR-Fetch.json'
  if (Test-Path -LiteralPath $summaryTool) {
   Invoke-CviiiPython -Script $summaryTool -Arguments @('--csv',$fetchAuditPath,'--json',$summaryJson)
   if ($LASTEXITCODE -ne 0) { throw 'Invalid JP0600 CHR fetch CSV' }
   $summary=Get-Content -LiteralPath $summaryJson -Raw | ConvertFrom-Json
   Write-Host ('Sampled physical PPU CHR reads: '+$summary.pattern_fetches)
   Write-Host ('Cache mismatches: '+$summary.cache_mismatches+'; invalid reads: '+$summary.invalid_fetches)
   if (-not $summary.cache_parity_pass) { Write-Warning 'Observed CHR bytes do not all match the asset cache' }
   Write-Host ('Local CHR analysis: '+$summaryJson)
  }
  $frameTool=Join-Path $PSScriptRoot 'jp_frame_evidence_report_0601.py'
  $frameJson=Join-Path $auditBase 'CVIII-Frame-Evidence.json'
  if ((Test-Path -LiteralPath $frameTool) -and
      (Test-Path -LiteralPath $frameEvidencePath)) {
   Invoke-CviiiPython -Script $frameTool -Arguments @('--fetch',$fetchAuditPath,'--evidence',$frameEvidencePath,'--json',$frameJson,'--require-parity')
   if ($LASTEXITCODE -ne 0) { throw 'JP0601 original PPU and CHR observations disagree' }
   $report=Get-Content -LiteralPath $frameJson -Raw | ConvertFrom-Json
   Write-Host ('Original PPU sampled frames: '+$report.sampled_original_ppu_frames)
   Write-Host ('Validated paired fetches: '+$report.pattern_fetches)
   Write-Host ('Local PPU frame-evidence report: '+$frameJson)
   $ntTool=Join-Path $PSScriptRoot 'jp_nt_trace_report_0606.py'
   if ((Test-Path -LiteralPath $ntTool) -and (Test-Path -LiteralPath $ntAuditPath)) {
    $ntJson=Join-Path $auditBase 'CVIII-NT-Fetch.json'
    Invoke-CviiiPython -Script $ntTool -Arguments @('--csv',$ntAuditPath,'--evidence',$frameEvidencePath,'--json',$ntJson)
    if ($LASTEXITCODE -ne 0) { throw 'JP0606 PPU nametable and frame evidence disagree' }
    $ntSummary=Get-Content -LiteralPath $ntJson -Raw | ConvertFrom-Json
    Write-Host ('JP0606 tile fetches: '+$ntSummary.tile_reads+', attribute fetches: '+$ntSummary.attribute_reads)
    Write-Host ('JP0606 CIRAM fetches: '+$ntSummary.ciram_reads+', CHR-ROM NT fetches: '+$ntSummary.chrrom_reads)
    if (-not $ntSummary.no_invalid_bus_records) { Write-Warning 'JP0606 reported invalid nametable bus records' }
    Write-Host ('Local nametable fetch report: '+$ntJson)
   }
  }
 }
} finally {Pop-Location}
