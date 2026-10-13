# JP0603: private first-run native Windows build and launch.
# The public build kit contains no game EXE, DLL or commercial ROM.
[CmdletBinding()]
param(
 [ValidateSet('Original','Enhanced')][string]$Edition='Original',
 [string]$Rom='',
 [switch]$UnlimitedSprites,
 [switch]$Rebuild
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

function Select-OwnerRom {
 Add-Type -AssemblyName System.Windows.Forms
 $picker=New-Object System.Windows.Forms.OpenFileDialog
 $picker.Title='Select original Japanese Akumajou Densetsu (.nes)'
 $picker.Filter='NES cartridge (*.nes)|*.nes'
 $picker.CheckFileExists=$true
 if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
  throw 'No original Japanese cartridge selected. No build was started.'
 }
 return $picker.FileName
}
function Test-PrivateGame([string]$Directory) {
 $main=Join-Path $Directory 'jp_akumajou_densetsu.exe'
 $legacy=Join-Path $Directory 'CVIII_Alpha.exe'
 return ((Test-Path -LiteralPath $main -PathType Leaf) -or
         (Test-Path -LiteralPath $legacy -PathType Leaf)) -and
         (Test-Path -LiteralPath (Join-Path $Directory 'SDL2.dll') -PathType Leaf) -and
         (Test-Path -LiteralPath (Join-Path $Directory 'Launch-Alpha.ps1') -PathType Leaf)
}

Write-Host 'CVIII — private Windows build and play'
$homeBuild=Join-Path $env:USERPROFILE 'CVIII-Alpha'
$romLocationFile=Join-Path $homeBuild 'LastRomPath.txt'
if (-not $Rom -and (Test-Path -LiteralPath $romLocationFile -PathType Leaf)) {
 $candidate=(Get-Content -LiteralPath $romLocationFile -Raw).Trim()
 if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
  $Rom=$candidate
  Write-Host 'Using previous original-JP cartridge location.'
 }
}
if (-not $Rom) { $Rom=Select-OwnerRom }
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$expected='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
$actual=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
 throw 'Wrong cartridge. The native JP build requires the original Japanese VRC6 ROM.'
}

[IO.Directory]::CreateDirectory($homeBuild) | Out-Null
# Store only the user's local ROM path, never any ROM or asset bytes.
Set-Content -LiteralPath $romLocationFile -Value $romPath -Encoding UTF8
$privateCandidate=Join-Path $homeBuild 'AlphaCandidate'
$localCandidate=$PSScriptRoot
if ((Test-PrivateGame $localCandidate) -and -not $Rebuild) {
 $runDir=$localCandidate
} elseif ((Test-PrivateGame $privateCandidate) -and -not $Rebuild) {
 $runDir=$privateCandidate
} else {
 $missing=@()
 foreach ($command in @('git','cmake','python')) {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) { $missing+= $command }
 }
 if ($missing.Count -gt 0) {
  throw ('Missing required tools: '+($missing -join ', ')+
   '. Install Git for Windows, Python 3, CMake, and Visual Studio 2022 Desktop development with C++; then retry.')
 }
 $programFilesX86=[Environment]::GetFolderPath('ProgramFilesX86')
 $vswhere=Join-Path $programFilesX86 'Microsoft Visual Studio\Installer\vswhere.exe'
 if (-not (Test-Path -LiteralPath $vswhere)) {
  throw 'Visual Studio 2022 with Desktop development with C++ is required. Install it, then retry.'
 }
 $vs=& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
 if ($LASTEXITCODE -ne 0 -or -not $vs) {
  throw 'MSVC x64 C++ tools are missing. Enable Desktop development with C++ in Visual Studio Installer.'
 }
 $builder=Join-Path $PSScriptRoot 'Build-Alpha.ps1'
 if (-not (Test-Path -LiteralPath $builder)) {
  $builder=Join-Path $homeBuild '_cviisource\JP\release\alpha\Build-Alpha.ps1'
 }
 if (-not (Test-Path -LiteralPath $builder)) {
  throw ('Missing Build-Alpha.ps1. Extract the complete ROM-free Builder Kit, then retry.')
 }
 [IO.Directory]::CreateDirectory($homeBuild) | Out-Null
 $logs=Join-Path $homeBuild 'logs'
 [IO.Directory]::CreateDirectory($logs) | Out-Null
 $log=Join-Path $logs ('Build-'+[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')+'.log')
 Write-Host ('Private game not found. Compiling once from the original cartridge.')
 Write-Host ('Build log: '+$log)
 Write-Host 'Compilation may take several minutes; do not close this window.'
 $started=$false
 try {
  Start-Transcript -Path $log -ErrorAction Stop | Out-Null
  $started=$true
  & $builder -Rom $romPath -OutDir $homeBuild
 } finally {
  if ($started) { Stop-Transcript | Out-Null }
 }
 if (-not (Test-PrivateGame $privateCandidate)) {
  throw ('Private build did not produce an EXE and SDL2.dll in '+$privateCandidate+
   '. Inspect the first error in '+$log)
 }
 $runDir=$privateCandidate
}
Write-Host ('Launching '+$Edition+' from '+$runDir)
$launcher=Join-Path $runDir 'Launch-Alpha.ps1'
$options=@{Rom=$romPath;Edition=$Edition}
if ($UnlimitedSprites -and $Edition -eq 'Enhanced') { $options.UnlimitedSprites=$true }
& $launcher @options
if ($LASTEXITCODE -ne 0) { throw ('Native game exited with status '+$LASTEXITCODE) }
