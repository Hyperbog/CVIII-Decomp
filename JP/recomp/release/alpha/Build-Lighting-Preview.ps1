# Private Windows Enhanced lighting preview. Does not touch the working CVIII-Alpha.
[CmdletBinding()]
param(
 [string]$Rom='',
 [string]$OutDir=(Join-Path $env:USERPROFILE 'CVIII-Lighting-Preview'),
 [switch]$BuildOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$branch='feature/enhanced-lighting-foundation'
$expected='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
if (-not $Rom) {
 $hint=Join-Path (Join-Path $env:USERPROFILE 'CVIII-Alpha') 'LastRomPath.txt'
 if (Test-Path -LiteralPath $hint) {
  $previous=(Get-Content -LiteralPath $hint -Raw).Trim()
  if ($previous -and (Test-Path -LiteralPath $previous -PathType Leaf)) { $Rom=$previous }
 }
}
if (-not $Rom) {
 Add-Type -AssemblyName System.Windows.Forms
 $dialog=New-Object System.Windows.Forms.OpenFileDialog
 $dialog.Filter='NES cartridge (*.nes)|*.nes'
 $dialog.Title='Choose your original Japanese Akumajou Densetsu ROM'
 if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
  throw 'The original Japanese ROM was not selected.'
 }
 $Rom=$dialog.FileName
}
$romPath=(Resolve-Path -LiteralPath $Rom -ErrorAction Stop).Path
$actual=(Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) {
 throw 'The private lighting build needs the authenticated original Japanese mapper24 ROM.'
}
$target=[IO.Path]::GetFullPath($OutDir)
[IO.Directory]::CreateDirectory($target) | Out-Null
$repo=Join-Path $target '_cviisource'
$uri='https://github.com/Hyperbog/CVIII-Decomp.git'
function Invoke-Git([string[]]$Arguments) {
 & git @Arguments
 if ($LASTEXITCODE -ne 0) { throw ('Git operation failed: '+($Arguments -join ' ')) }
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
 throw 'Git for Windows is required.'
}
if (-not (Test-Path -LiteralPath $repo)) {
 Invoke-Git -Arguments @('clone','--branch',$branch,'--single-branch',$uri,$repo)
} else {
 # This is a feature-only checkout; never switch or reset another branch.
 $current=(& git -C $repo branch --show-current)
 if ($LASTEXITCODE -ne 0 -or $current.Trim() -ne $branch) {
  throw 'The preview source folder contains a different branch. Refusing to overwrite it.'
 }
 Invoke-Git -Arguments @('-C',$repo,'pull','--ff-only','origin',$branch)
}
$commit=(& git -C $repo rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Could not identify the preview source commit.' }
Write-Host ('Lighting preview source: '+$commit)
Write-Host ('Dedicated private preview folder: '+$target)
$build=Join-Path $repo 'JP/recomp/release/alpha/Build-Alpha.ps1'
if (-not (Test-Path -LiteralPath $build)) { throw 'Feature branch build tool missing.' }
if ($BuildOnly) {
 & $build -Rom $romPath -OutDir $target -ProjectRoot $repo
} else {
 & $build -Rom $romPath -OutDir $target -ProjectRoot $repo -PlayAfterBuild
}
Write-Host 'Preview build complete. The normal CVIII-Alpha game remains unchanged.'
