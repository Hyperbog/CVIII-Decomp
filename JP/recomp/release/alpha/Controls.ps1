# JP0661 — owner-only keyboard profile selector for the existing native game.
# Acts only on the local NESRecomp config.ini; no guest memory/ROM changes.
[CmdletBinding()]
param(
 [ValidateSet('Menu','List','Show','Apply','Save','Remap')][string]$Action='Menu',
 [string]$Profile='',
 [string]$Button='',
 [string]$Key='',
 [string]$GameDir=''
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

if (-not $GameDir) {
 if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'config.ini') -PathType Leaf) {
  $GameDir=$PSScriptRoot
 } else {
  $GameDir=Join-Path $env:USERPROFILE 'CVIII-Alpha\AlphaCandidate'
 }
}
$GameDir=[IO.Path]::GetFullPath($GameDir)
$config=Join-Path $GameDir 'config.ini'
if (-not (Test-Path -LiteralPath $config -PathType Leaf)) {
 throw ('No native config.ini found at '+$config+'. Run Play-CVIII.bat once, close the game, then retry.')
}
$profileTool=Join-Path $GameDir 'Control-Profiles.py'
if (-not (Test-Path -LiteralPath $profileTool -PathType Leaf)) {
 $profileTool=Join-Path $PSScriptRoot 'Control-Profiles.py'
}
$resolver=Join-Path $GameDir 'Resolve-Python.ps1'
if (-not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
 $resolver=Join-Path $PSScriptRoot 'Resolve-Python.ps1'
}
if (-not (Test-Path -LiteralPath $profileTool -PathType Leaf) -or
    -not (Test-Path -LiteralPath $resolver -PathType Leaf)) {
 throw 'Controls manager not installed in this private AlphaCandidate; rebuild with the current ROM-free kit.'
}
. $resolver
function Invoke-ControlProfile {
 param([Parameter(Mandatory=$true)][string[]]$ControlArguments)
 Invoke-CviiiPython -Script $profileTool -Arguments (@('--root',$GameDir) + $ControlArguments)
}
switch ($Action) {
 'List'  { Invoke-ControlProfile -ControlArguments @('--list'); return }
 'Show'  { Invoke-ControlProfile -ControlArguments @('--show'); return }
 'Save'  {
  if (-not $Profile) { throw 'Specify -Profile with -Action Save.' }
  Invoke-ControlProfile -ControlArguments @('--save',$Profile)
  return
 }
 'Apply' {
  if (-not $Profile) { throw 'Specify -Profile with -Action Apply.' }
  Invoke-ControlProfile -ControlArguments @('--apply',$Profile)
  return
 }
 'Remap' {
  if (-not $Button -or -not $Key) {
   throw 'Specify -Button (a,b,select,start,up,down,left,right) and -Key.'
  }
  Invoke-ControlProfile -ControlArguments @('--remap',$Button.ToLowerInvariant(),$Key)
  return
 }
}
Write-Host 'CVIII native keyboard controls — close the running game before changing config.ini.'
while ($true) {
 Write-Host ''
 Invoke-ControlProfile -ControlArguments @('--show')
 Invoke-ControlProfile -ControlArguments @('--list')
 Write-Host '1) Original keyboard defaults (arrows / Z / X)'
 Write-Host '2) WASD keyboard layout (WASD / J / K)'
 Write-Host '3) Save the currently active keyboard bindings as a named profile'
 Write-Host '4) Apply a previously saved named profile'
 Write-Host '5) Remap a single button (swaps any conflicting existing key)'
 Write-Host '6) Exit without changes'
 $selection=(Read-Host 'Choose 1–6').Trim()
 switch ($selection) {
  '1' { Invoke-ControlProfile -ControlArguments @('--apply','default') }
  '2' { Invoke-ControlProfile -ControlArguments @('--apply','wasd') }
  '3' {
   $selected=(Read-Host 'Profile name (lowercase letters/digits/_/-)').Trim()
   Invoke-ControlProfile -ControlArguments @('--save',$selected)
  }
  '4' {
   $selected=(Read-Host 'Saved profile name').Trim()
   Invoke-ControlProfile -ControlArguments @('--apply',$selected)
  }
  '5' {
   $b=(Read-Host 'Button: a, b, select, start, up, down, left or right').Trim().ToLowerInvariant()
   $k=(Read-Host 'Keyboard scancode (e.g. C, Space, W, Left Shift)').Trim()
   Invoke-ControlProfile -ControlArguments @('--remap',$b,$k)
  }
  '6' { return }
  default { Write-Host 'Invalid choice; enter 1, 2, 3, 4, 5 or 6.' }
 }
}
