# JP0844: owner-private ROM-free seed source resolution and candidate freshness.
Set-StrictMode -Version Latest
function Resolve-CviiiSeedEvidence {
 [CmdletBinding()]
 param([string]$Directory='', [string]$UserProfile=$env:USERPROFILE)
 $explicit=-not [string]::IsNullOrWhiteSpace($Directory)
 if ($explicit) {
  $candidate=(Resolve-Path -LiteralPath $Directory -ErrorAction Stop).Path
 } else {
  if ([string]::IsNullOrWhiteSpace($UserProfile)) { return $null }
  $candidate=Join-Path $UserProfile 'Documents\jp0837-private'
 }
 $required=@('jp0837-report.json','native.misses','native.hashes',
             'interp.hashes','jp0837-bank-qualified-seeds.txt')
 $missing=@($required | Where-Object {
  -not (Test-Path -LiteralPath (Join-Path $candidate $_) -PathType Leaf)
 })
 if ($missing.Count -gt 0) {
  if ($explicit) { throw ('Incomplete JP0837 private coverage: '+($missing -join ', ')) }
  return $null
 }
 return [pscustomobject]@{
  Directory=$candidate
  MissSha256=(Get-FileHash -LiteralPath (Join-Path $candidate 'native.misses') -Algorithm SHA256).Hash.ToLowerInvariant()
 }
}
function Test-CviiiSeededCandidate {
 [CmdletBinding()]
 param([Parameter(Mandatory=$true)][string]$Directory,
       [Parameter(Mandatory=$true)][string]$MissSha256)
 $manifest=Join-Path $Directory 'ALPHA_BUILD.json'
 $exe=Join-Path $Directory 'jp_akumajou_densetsu.exe'
 if (-not (Test-Path -LiteralPath $manifest -PathType Leaf) -or
     -not (Test-Path -LiteralPath $exe -PathType Leaf)) { return $false }
 try {
  $meta=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
  if ($meta.jp0844_seeded_native_backend -ne $true -or
      $meta.jp0844_source_miss_sha256 -ne $MissSha256 -or
      [int]$meta.jp0844_seed_count -le 0) { return $false }
  $actual=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
  return $actual -eq [string]$meta.game_exe_sha256
 } catch { return $false }
}
