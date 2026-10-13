# CVIII native PC Alpha 0.2 — Original/Enhanced owner-only launcher.
[CmdletBinding()]
param(
 [string]$Rom='',
 [ValidateSet('Original','Enhanced')][string]$Edition='Original',
 [switch]$UnlimitedSprites,
 [switch]$ChrAudit
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
if (-not (Test-Path -LiteralPath $game) -or
    -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'SDL2.dll'))) {
 throw 'Missing native Windows game executable or SDL2.dll.'
}
$sprites=if ($Edition -eq 'Enhanced' -and $UnlimitedSprites) {'1'} else {'0'}
Write-Host "CVIII Alpha 0.2 $Edition (experimental extra-OAM sprites: $sprites)"
Write-Host 'Controls: arrows=D-pad, Z=A, X=B, Enter=Start, Backslash=Select.'
Write-Host 'F8/F9 save/load; builds supporting slots use Ctrl+0..9.'
Push-Location $PSScriptRoot
try {
 $gameArgs=@($romPath,'--edition',$Edition.ToLowerInvariant(),'--unlimited-sprites',$sprites)
 # Enhanced can opt into verified physical CHR asset metadata without ever
 # replacing the original cartridge's timing, mapper or game framebuffer.
 if ($Edition -eq 'Enhanced') {
  $assetIndex=Join-Path $PSScriptRoot 'CVIII-CHR-Index.dat'
  if (Test-Path -LiteralPath $assetIndex) {
   $gameArgs+=@('--asset-index',$assetIndex)
   Write-Host 'Loading authenticated read-only CHR asset index (no rendering changes).'
   if ($ChrAudit) {
    $chrAuditPath=Join-Path $PSScriptRoot 'CVIII-CHR-Audit.csv'
    $gameArgs+=@('--chr-audit',$chrAuditPath)
    $fetchAuditPath=Join-Path $PSScriptRoot 'CVIII-CHR-Fetch.csv'
    $gameArgs+=@('--chr-fetch-audit',$fetchAuditPath)
    $frameEvidencePath=Join-Path $PSScriptRoot 'CVIII-Frame-Evidence.csv'
    $gameArgs+=@('--frame-evidence',$frameEvidencePath)
    Write-Host ('Recording original PPU fingerprints: '+$frameEvidencePath)
    Write-Host ('Recording sampled VRC6 mappings: '+$chrAuditPath)
    Write-Host ('Recording physical PPU CHR reads: '+$fetchAuditPath)
   }
  } else {
   if ($ChrAudit) { throw 'CHR mapping audit requires private CVIII-CHR-Index.dat' }
   Write-Host 'No asset index found; Enhanced falls back to original ROM-driven graphics.'
  }
 } elseif ($ChrAudit) { throw 'CHR mapping audit is developer-only for Enhanced' }
 & $game @gameArgs
 if ($LASTEXITCODE -ne 0) {throw "Native game exited with $LASTEXITCODE"}
 if ($ChrAudit -and (Test-Path -LiteralPath $fetchAuditPath)) {
  $summaryTool=Join-Path $PSScriptRoot 'jp_chr_fetch_report_0600.py'
  $summaryJson=Join-Path $PSScriptRoot 'CVIII-CHR-Fetch.json'
  if (Test-Path -LiteralPath $summaryTool) {
   & python $summaryTool --csv $fetchAuditPath --json $summaryJson
   if ($LASTEXITCODE -ne 0) { throw 'Invalid JP0600 CHR fetch CSV' }
   $summary=Get-Content -LiteralPath $summaryJson -Raw | ConvertFrom-Json
   Write-Host ('Sampled physical PPU CHR reads: '+$summary.pattern_fetches)
   Write-Host ('Cache mismatches: '+$summary.cache_mismatches+'; invalid reads: '+$summary.invalid_fetches)
   if (-not $summary.cache_parity_pass) { Write-Warning 'Observed CHR bytes do not all match the asset cache' }
   Write-Host ('Local CHR analysis: '+$summaryJson)
  }
  $frameTool=Join-Path $PSScriptRoot 'jp_frame_evidence_report_0601.py'
  $frameJson=Join-Path $PSScriptRoot 'CVIII-Frame-Evidence.json'
  if ((Test-Path -LiteralPath $frameTool) -and
      (Test-Path -LiteralPath $frameEvidencePath)) {
   & python $frameTool --fetch $fetchAuditPath --evidence $frameEvidencePath --json $frameJson --require-parity
   if ($LASTEXITCODE -ne 0) { throw 'JP0601 original PPU and CHR observations disagree' }
   $report=Get-Content -LiteralPath $frameJson -Raw | ConvertFrom-Json
   Write-Host ('Original PPU sampled frames: '+$report.sampled_original_ppu_frames)
   Write-Host ('Validated paired fetches: '+$report.pattern_fetches)
   Write-Host ('Local PPU frame-evidence report: '+$frameJson)
  }
 }
} finally {Pop-Location}
