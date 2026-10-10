#!/usr/bin/env bash
# JP native subsystem regression gate; no original ROM is committed.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
src="$root/JP/src"; tests="$root/JP/tests"
build="$(mktemp -d "${TMPDIR:-/tmp}/c3-jp-tests.XXXXXXXX")"
trap 'rm -rf "$build"' EXIT
cxx="${CXX:-g++}"
flags=(-std=c++20 -O2 -Wall -Wextra -Werror -pedantic -I "$src")
rom="${1:-}"
if [[ -n "$rom" ]]; then
    [[ -f "$rom" ]] || { echo "ROM not found: $rom" >&2; exit 2; }
    python3 - "$rom" <<'PY'
import hashlib,sys
data=open(sys.argv[1],'rb').read()
assert len(data)==393232 and hashlib.sha256(data).hexdigest()=='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28', 'wrong JP ROM'
print('JP ROM identity verified')
PY
fi
compile() {
    local t="$1"; shift
    "$cxx" "${flags[@]}" "$tests/${t}_test.cpp" "$@" -o "$build/$t"
    echo "COMPILE PASS $t"
}
compile ai_script_dispatch "$src/ai_script_dispatch.cpp"
compile collision_math "$src/collision_math.cpp"
compile fixed_tile_probe
compile oam_renderer "$src/oam_renderer.cpp"
compile room_state_dispatch
compile temporary_prg_bank_read
compile vrc6_irq "$src/vrc6_irq.cpp"
compile vrc6_mapper "$src/vrc6_mapper.cpp"
for t in collision_math oam_renderer vrc6_irq vrc6_mapper; do
    "$build/$t"
    echo "TEST PASS $t (ROM-free)"
done
if [[ -n "$rom" ]]; then
    for t in ai_script_dispatch fixed_tile_probe room_state_dispatch temporary_prg_bank_read; do
        "$build/$t" "$rom"
        echo "TEST PASS $t (ROM-backed)"
    done
    for t in vrc6_irq vrc6_mapper; do
        "$build/$t" "$rom"
        echo "TEST PASS $t (ROM-backed supplemental)"
    done
else
    echo "ROM-backed tests require locally supplied JP ROM; absent from GitHub Actions"
fi
"$cxx" "${flags[@]}" "$tests/vrc6_irq_trace_driver_0508.cpp" "$src/vrc6_irq.cpp" -o "$build/vrc6_irq_trace_driver"
python3 "$root/JP/tools/test_vrc6_irq_cross_language_0508.py" "$build/vrc6_irq_trace_driver"
python3 "$root/JP/tests/test_nes_reuse.py"
python3 "$root/JP/tests/test_nes_mapper_family.py"
python3 "$root/JP/tests/test_nes_certified_reuse.py"
python3 "$root/JP/tests/test_nes_cdl_bridge_0508.py"
python3 "$root/JP/tests/test_synthetic_crossedition_0508.py"
python3 "$root/JP/tests/test_nes_fds_catalog.py"
python3 "$root/JP/tests/test_nes_trace_compare.py"
python3 "$root/JP/tests/test_mesen_reference_0508.py"
python3 "$root/JP/tests/test_mesen_stage1_branch_0508.py"
python3 "$root/JP/tests/test_mesen_fixed_live_0508.py"
python3 "$root/JP/tests/test_native_mesen_pc_0509.py"
python3 -m py_compile "$root/JP/tools/audit_mesen_stage1_branch_0508.py" "$root/JP/tools/audit_mesen_stage1_crossedition_0508.py" "$root/JP/tools/audit_mesen_fixed_live_0508.py"
compile cpu_2a03 "$src/cpu_2a03.cpp"
compile native_machine_0509 "$src/cpu_2a03.cpp" "$src/native_machine_0509.cpp" "$src/vrc6_mapper.cpp" "$src/vrc6_irq.cpp"
"$build/cpu_2a03"
echo "TEST PASS cpu_2a03 (262144 exhaustive ADC/SBC and control-stack tests)"
"$build/native_machine_0509"
echo "TEST PASS native_machine_0509 (synthetic mapped CPU/VRC6/PPU/NMI)"
"$cxx" "${flags[@]}" "$root/JP/tools/native_probe_0509.cpp" "$src/cpu_2a03.cpp" "$src/native_machine_0509.cpp" "$src/vrc6_mapper.cpp" "$src/vrc6_irq.cpp" -o "$build/cviii-headless-0509"
echo "COMPILE PASS cviii-headless-0509 (requires original JP ROM to run)"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/tools/test_native_mesen_pc_0509.py" "$build/cviii-headless-0509" "$rom"
    echo "TEST PASS authenticated JP original-ROM 7828-PC golden Mesen2 prefix"
fi
python3 -m py_compile "$root/JP/tools/audit_actor_slot_0509.py" "$root/JP/tools/audit_actor_cpu_abi_0509.py" "$root/JP/tools/audit_actor_spawn_0509.py"
if [[ -n "$rom" ]]; then
  python3 "$root/JP/tools/audit_actor_slot_0509.py" "$rom" "$build/actor_lift_rom_hash_audit.json"
  python3 "$root/JP/tools/audit_actor_cpu_abi_0509.py" "$rom" --report "$build/actor_source_cpu_abi_audit.json"
  python3 "$root/JP/tools/audit_actor_spawn_0509.py" "$rom" --report "$build/actor_source_spawn_audit.json"
fi
echo "PASS: 10 native test binaries plus original-ROM headless CLI compiled; ROM-free suites executed"
