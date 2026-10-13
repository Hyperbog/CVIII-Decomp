# JP0602 owner-only labelled retail-JP PPU/CHR evidence session.
# No ROM, binary, or copyrighted extracted data leave the private machine.
[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Rom,
 [Parameter(Mandatory=$true)][ValidatePattern('^[a-z][a-z0-9-]{2,47}$')][string]$Scene,
 [Parameter(Mandatory=$true)]
 [ValidateSet('title','village','clock_tower','forest','ship','castle','boss','companion')]
 [string]$Area,
 [ValidateSet('Trevor','Sypha','Grant','Alucard','None')][string]$Character='Trevor',
 [ValidateSet('title','gameplay','boss','cutscene','recruitment')][string]$Kind='gameplay',
 [string]$Checkpoint='',
 [string]$Notes='',
 [string]$OutRoot=(Join-Path $PSScriptRoot 'QA')
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$jpSha='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
if ((Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $jpSha) {
 throw 'Owner-local JP0602 capture needs the authenticated Japanese retail ROM.'
}
$launcher=Join-Path $PSScriptRoot 'Launch-Alpha.ps1'
$exe=Join-Path $PSScriptRoot 'jp_akumajou_densetsu.exe'
if (!(Test-Path -LiteralPath $exe)) { $exe=Join-Path $PSScriptRoot 'CVIII_Alpha.exe' }
$asset=Join-Path $PSScriptRoot 'CVIII-CHR-Index.dat'
foreach ($f in @($launcher,$exe,$asset)) {
 if (!(Test-Path -LiteralPath $f)) { throw "Missing private Alpha file: $f" }
}
$start=[DateTime]::UtcNow
$id=$start.ToString('yyyyMMddTHHmmssZ')+'-'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$root=[IO.Path]::GetFullPath($OutRoot)
[IO.Directory]::CreateDirectory($root) | Out-Null
$folder=Join-Path $root ($Scene+'-'+$id)
if (Test-Path -LiteralPath $folder) { throw 'Refusing to overwrite prior QA capture.' }
[IO.Directory]::CreateDirectory($folder) | Out-Null
Write-Host ('Capturing owner-private retail session: '+$folder)
Write-Host 'Play the chosen scene, then close the game to save/validate this sample.'
try {
 & $launcher -Rom $romPath -Edition Enhanced -ChrAudit -AuditOutDir $folder
} catch {
 Write-Warning ('Session failed; raw diagnostic files preserved at '+$folder)
 throw
}
$files=[ordered]@{}
foreach ($name in @('CVIII-CHR-Audit.csv','CVIII-CHR-Fetch.csv',
 'CVIII-Frame-Evidence.csv','CVIII-CHR-Fetch.json','CVIII-Frame-Evidence.json')) {
 $path=Join-Path $folder $name
 if (!(Test-Path -LiteralPath $path)) { throw "Missing local QA evidence: $path" }
 $bytes=(Get-Item -LiteralPath $path).Length
 if ($bytes -lt 1 -or $bytes -gt 32MB) { throw "Empty/oversized QA evidence: $path" }
 $files[$name]=[ordered]@{
  bytes=[long]$bytes
  sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
 }
}
$record=[ordered]@{
 schema='CVIII-JP-QA-capture/v1'
 capture_id=$id
 scene=$Scene
 area=$Area
 kind=$Kind
 character=$Character
 checkpoint=$Checkpoint
 notes=$Notes
 started_utc=$start.ToString('o')
 ended_utc=[DateTime]::UtcNow.ToString('o')
 rom_sha256=$jpSha
 game_exe_sha256=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
 asset_index_sha256=(Get-FileHash -LiteralPath $asset -Algorithm SHA256).Hash.ToLowerInvariant()
 files=$files
}
$manifest=Join-Path $folder 'capture.json'
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifest -Encoding UTF8
$tool=Join-Path $PSScriptRoot 'jp_qa_matrix_0602.py'
if (Test-Path -LiteralPath $tool) {
 $report=Join-Path $root 'CVIII-QA-Matrix.json'
 & python $tool --root $root --json $report --min-frames 10
 if ($LASTEXITCODE -ne 0) { Write-Warning 'QA matrix still has insufficient/corrupt evidence.' }
 else { Write-Host ('Private QA scene matrix: '+$report) }
}
Write-Host ('Captured private scene manifest: '+$manifest)
