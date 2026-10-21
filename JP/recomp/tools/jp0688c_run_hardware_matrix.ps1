# JP0688c: public Blargg test ROMs; no CVIII ROM, no NESRecomp modifications.
# Creates private iNES header-only copies with 8 KiB PRG RAM for $6000 output.
$ErrorActionPreference = 'Stop'

$root = 'C:\Tools\Mesen2\Private\JP0688-Hardware-Validation'
$work = 'C:\Tools\Mesen2\JP0684-Native-Clock-Logging-Fix'
$src = Join-Path $root 'nesrecomp'
$roms = Join-Path $root 'nes-test-roms'
$build = Join-Path $root 'build'
$private = Join-Path $root 'JP0688c'
$sourcePin = '2b4fcdb98c9e702be3fb365cfc645003c50b5fc1'
$testPin = '95d8f621ae55cee0d09b91519a8989ae0e64753b'

if (!(Test-Path $work)) { throw "Missing working directory: $work" }
New-Item -ItemType Directory -Force $private | Out-Null
foreach ($pair in @(@($src, $sourcePin), @($roms, $testPin))) {
    $actual = (& git -C $pair[0] rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $actual -ne $pair[1]) {
        throw "Revision mismatch for $($pair[0]); expected $($pair[1])"
    }
}

# Rebuild the host from the specified source; a stale executable is not evidence.
& cmake -S (Join-Path $src 'runner\cyc') -B $build `
    -DNESRECOMP_HEADLESS=ON -DNESRECOMP_RECOMP_UI=OFF
if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed' }
& cmake --build $build --config Release --target cyc_interp --parallel 4
if ($LASTEXITCODE -ne 0) { throw 'cyc_interp build failed' }
$releaseExe = Join-Path $build 'Release\cyc_interp.exe'
if (Test-Path $releaseExe) {
    $exePath = $releaseExe
} else {
    $found = @(Get-ChildItem $build -Recurse -File -Filter 'cyc_interp.exe')
    if ($found.Count -ne 1) { throw 'Ambiguous or missing cyc_interp.exe' }
    $exePath = $found[0].FullName
}

$tests = @(
    @{ Id='vbl_set_time'; File='ppu_vbl_nmi/rom_singles/02-vbl_set_time.nes' },
    @{ Id='nmi_control'; File='ppu_vbl_nmi/rom_singles/04-nmi_control.nes' },
    @{ Id='nmi_timing'; File='ppu_vbl_nmi/rom_singles/05-nmi_timing.nes' },
    @{ Id='branch_delays_irq'; File='cpu_interrupts_v2/rom_singles/5-branch_delays_irq.nes' }
)

$rows = [System.Collections.Generic.List[object]]::new()
$evidence = [System.Collections.Generic.List[string]]::new()
$romMetadata = [System.Collections.Generic.List[object]]::new()

foreach ($test in $tests) {
    $original = Join-Path $roms $test.File
    if (!(Test-Path $original)) { throw "Missing test ROM: $original" }
    $bytes = [System.IO.File]::ReadAllBytes($original)
    # All four pinned single-ROM images: NROM, 32 KiB PRG, 8 KiB CHR,
    # vertical mirroring, iNES byte 8 = 0 (no PRG-RAM declared).
    if ($bytes.Length -ne 40976 -or
        $bytes[0] -ne 0x4E -or $bytes[1] -ne 0x45 -or
        $bytes[2] -ne 0x53 -or $bytes[3] -ne 0x1A -or
        $bytes[4] -ne 2 -or $bytes[5] -ne 1 -or
        $bytes[6] -ne 1 -or $bytes[7] -ne 0 -or
        $bytes[8] -ne 0) {
        throw "Unexpected public ROM header/length: $($test.Id)"
    }
    $copy = [byte[]]$bytes.Clone()
    $copy[8] = 1
    $patched = Join-Path $private "$($test.Id)-prgram8k.nes"
    [System.IO.File]::WriteAllBytes($patched, $copy)
    $originalHash = (Get-FileHash $original -Algorithm SHA256).Hash
    if ($test.Id -eq 'nmi_control' -and $originalHash -ne
        '84722C75B896C47C8642F83220230FE14F0A31E55E26ECB83C400E6A26D91B32') {
        throw 'nmi_control original SHA differs from JP0688b control gate'
    }
    $patchedHash = (Get-FileHash $patched -Algorithm SHA256).Hash
    $romMetadata.Add([pscustomobject]@{
        Test=$test.Id; OriginalSHA256=$originalHash;
        HeaderOnlyCopySHA256=$patchedHash; HeaderPRGRAMBytes=8192
    })

    foreach ($align in 0..3) {
        $id = "$($test.Id)-align$align"
        $dump = Join-Path $private "$id.mem.txt"
        $log = Join-Path $private "$id.log"
        Remove-Item $dump, $log -ErrorAction SilentlyContinue
        $watch = [System.Diagnostics.Stopwatch]::StartNew()
        & $exePath $patched --headless --align $align `
            --frames 900 --mem-frame 899 --mem-out $dump *> $log
        $code = $LASTEXITCODE
        $watch.Stop()

        $dumpExists = Test-Path $dump
        $wramLines = [System.Collections.Generic.List[string]]::new()
        if ($dumpExists) {
            foreach ($line in [System.IO.File]::ReadLines($dump)) {
                if ($line -match '^wram [0-9A-Fa-f]{4}:') {
                    $wramLines.Add($line)
                    if ($wramLines.Count -ge 3) { break }
                }
            }
        }
        $resultByte = $null
        $signatureValid = $false
        $head = @()
        if ($wramLines.Count -ge 1 -and
            $wramLines[0] -match '^wram 0000:\s*(.+)$') {
            $head = @($Matches[1].Trim() -split '\s+')
            if ($head.Count -ge 4 -and
                (@($head[0..3] | Where-Object { $_ -notmatch '^[0-9a-fA-F]{2}$' }).Count -eq 0)) {
                $resultByte = $head[0].ToUpperInvariant()
                $signatureValid = (
                    $head[1].ToUpperInvariant() -eq 'DE' -and
                    $head[2].ToUpperInvariant() -eq 'B0' -and
                    $head[3].ToUpperInvariant() -eq '61'
                )
            }
        }
        $verdict = if ($code -ne 0) { 'RUNTIME_ERROR' }
            elseif (!$dumpExists) { 'NO_DUMP' }
            elseif ($null -eq $resultByte) { 'NO_WRAM_RESULT' }
            elseif (!$signatureValid) { 'INVALID_TEST_SIGNATURE' }
            elseif ($resultByte -eq '00') { 'PASS' }
            elseif ($resultByte -eq '80') { 'STILL_RUNNING' }
            elseif ($resultByte -eq '81') { 'RESET_REQUIRED' }
            elseif ([Convert]::ToInt32($resultByte,16) -le 127) { 'TEST_FAILURE_CODE' }
            else { 'INVALID_RESULT_CODE' }

        $rows.Add([pscustomobject]@{
            Test=$test.Id; Alignment=$align; Frames=900;
            ResultCode=$resultByte; SignatureValid=$signatureValid;
            Verdict=$verdict; ExitCode=$code;
            DumpExists=$dumpExists; ElapsedSeconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
        })
        $evidence.Add("=== $id ===")
        foreach ($line in $wramLines) { $evidence.Add($line) }
        $evidence.Add('')
        Write-Host ("{0,-29} status={1,-3} {2}" -f $id, $resultByte, $verdict)
    }
}

$report = [ordered]@{
    Protocol='JP0688c-v1'; SourcePin=$sourcePin; TestPin=$testPin;
    Host='cyc_interp'; PRGRAMHeaderCopiesOnly=$true;
    FrameCount=900; SampleFrame=899;
    RomMetadata=@($romMetadata.ToArray()); Results=@($rows.ToArray())
}
$jsonPath = Join-Path $work 'JP0688c-hardware-matrix.json'
$evidencePath = Join-Path $work 'JP0688c-wram-evidence.txt'
$report | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 $jsonPath
$evidence | Set-Content -Encoding ASCII $evidencePath
$rows | Format-Table Test,Alignment,ResultCode,Verdict,ExitCode -AutoSize
Write-Host "JSON:     $jsonPath"
Write-Host "Evidence: $evidencePath"
Write-Host "Private dumps, patched public ROMs and logs: $private"
