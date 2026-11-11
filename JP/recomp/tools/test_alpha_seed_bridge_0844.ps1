# JP0844: synthetic private evidence; no Japanese ROM or Mesen required.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$alpha=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\release\alpha')).Path
. (Join-Path $alpha 'Resolve-Seed-0844.ps1')
foreach ($name in @('Build-Alpha.ps1','Build-And-Play.ps1','Resolve-Seed-0844.ps1')) {
 $tokens=$null;$errors=$null
 [System.Management.Automation.Language.Parser]::ParseFile(
  (Join-Path $alpha $name),[ref]$tokens,[ref]$errors) | Out-Null
 if ($errors.Count -gt 0) { throw ($name+': '+($errors | Out-String)) }
}
$builder=Get-Content -LiteralPath (Join-Path $alpha 'Build-Alpha.ps1') -Raw
$launcher=Get-Content -LiteralPath (Join-Path $alpha 'Build-And-Play.ps1') -Raw
if ($builder -notmatch "'--jp0837-dir'" -or
    $builder -notmatch 'bank_qualified_seed_provenance' -or
    $launcher -notmatch 'Test-CviiiSeededCandidate') {
 throw 'JP0844 builder or cached-candidate integration absent'
}
$root=Join-Path $env:RUNNER_TEMP ('JP0844 seed path '+[guid]::NewGuid().ToString('N'))
$evidence=Join-Path $root 'Documents\jp0837-private'
$candidate=Join-Path $root 'Candidate With Spaces'
[IO.Directory]::CreateDirectory($evidence) | Out-Null
[IO.Directory]::CreateDirectory($candidate) | Out-Null
try {
 if (Resolve-CviiiSeedEvidence -UserProfile $root) {
  throw 'Incomplete default evidence accepted'
 }
 foreach ($name in @('jp0837-report.json','native.misses','native.hashes',
                      'interp.hashes','jp0837-bank-qualified-seeds.txt')) {
  Set-Content -LiteralPath (Join-Path $evidence $name) -Encoding Ascii -Value 'synthetic'
 }
 $source=Resolve-CviiiSeedEvidence -UserProfile $root
 $explicit=Resolve-CviiiSeedEvidence -Directory $evidence
 if (-not $source -or $source.MissSha256 -ne $explicit.MissSha256 -or
     $source.Directory -ne $explicit.Directory) {
  throw 'Default and explicit evidence selection differ'
 }
 $exe=Join-Path $candidate 'jp_akumajou_densetsu.exe'
 Set-Content -LiteralPath $exe -Encoding Ascii -Value 'synthetic executable'
 $hash=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
 @{
  jp0844_seeded_native_backend=$true
  jp0844_seed_count=6716
  jp0844_source_miss_sha256=$source.MissSha256
  game_exe_sha256=$hash
 } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $candidate 'ALPHA_BUILD.json') -Encoding UTF8
 if (-not (Test-CviiiSeededCandidate -Directory $candidate -MissSha256 $source.MissSha256)) {
  throw 'Matching seeded candidate rejected'
 }
 if (Test-CviiiSeededCandidate -Directory $candidate -MissSha256 ('0'*64)) {
  throw 'Outdated source accepted'
 }
 Add-Content -LiteralPath $exe -Value 'tampered'
 if (Test-CviiiSeededCandidate -Directory $candidate -MissSha256 $source.MissSha256) {
  throw 'Tampered executable accepted'
 }
 Remove-Item -LiteralPath (Join-Path $evidence 'native.hashes')
 if (Resolve-CviiiSeedEvidence -UserProfile $root) {
  throw 'Incomplete default profile was not ignored'
 }
 $rejected=$false
 try { Resolve-CviiiSeedEvidence -Directory $evidence | Out-Null }
 catch { $rejected=$true }
 if (-not $rejected) { throw 'Incomplete explicit evidence not rejected' }
 Write-Host 'PASS JP0844 private coverage discovery, cache freshness and tamper rejection'
} finally {
 Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
