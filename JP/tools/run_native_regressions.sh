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
compile actor_event_row32_0510 "$src/actor_event_row32_0510.cpp" "$src/actor_slot_0509.cpp"
compile actor_motion_prg0b_0511 "$src/actor_motion_prg0b_0511.cpp"
compile actor_displacement_prg0b_0512 "$src/actor_displacement_prg0b_0512.cpp"
compile actor_displacement_vertical_prg0b_0513 "$src/actor_displacement_vertical_prg0b_0513.cpp"
compile actor_post8843_0513 "$src/actor_displacement_vertical_prg0b_0513.cpp"
compile actor_preflight_0514 "$src/actor_preflight_0514.cpp"
compile actor_collision_precheck_0515 "$src/actor_collision_precheck_0515.cpp" "$src/actor_preflight_0514.cpp"
compile actor_collision_measure_0516 "$src/actor_collision_measure_0516.cpp" "$src/actor_collision_precheck_0515.cpp" "$src/actor_preflight_0514.cpp"
"$build/actor_collision_measure_0516"
echo "TEST PASS original JP raw0B B339/80B3/80C1 collision distance (139343 source-bounded cases)"
python3 -m py_compile "$root/JP/tools/audit_b217_original_mesen_0515.py"
"$build/actor_collision_precheck_0515"
echo "TEST PASS JP original B217 collision admission and B1F8 composition (82947 cases)"
python3 -m py_compile "$root/JP/tools/audit_actor_preflight_0514.py"
"$build/actor_preflight_0514"
echo "TEST PASS original JP 0514 delta producer / actor preflight (100357 cases)"
python3 -m py_compile "$root/JP/tools/audit_vertical_synthetic_0513.py"
"$build/actor_displacement_vertical_prg0b_0513"
"$build/actor_post8843_0513"
echo "TEST PASS original JP 0513 vertical prefix and 8843 continuation (270351 cases)"
"$build/actor_displacement_prg0b_0512"
python3 -m py_compile "$root/JP/tools/audit_mesen_displacement_0512.py"
echo 'TEST PASS faithful original JP $80E3 horizontal displacement (73742 cases)'
python3 -m py_compile "$root/JP/tools/audit_mesen_actor_motion_0511.py"
"$build/actor_motion_prg0b_0511"
echo "TEST PASS original JP raw0B two-axis native actor motion (69646 source-bounded cases)"
python3 -m py_compile "$root/JP/tools/audit_native_row32_live_0510.py"
"$build/actor_event_row32_0510"
echo "TEST PASS source-lift original JP row32 (4111 ROM-free boundary cases)"
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
python3 -m py_compile "$root/JP/tools/audit_actor_slot_0509.py" "$root/JP/tools/audit_actor_cpu_abi_0509.py" "$root/JP/tools/audit_actor_spawn_0509.py" "$root/JP/tools/audit_actor_precheck_0509.py" "$root/JP/tools/audit_actor_guard_producers_0509.py" "$root/JP/tools/audit_actor_dispatch_chain_0509.py" "$root/JP/tools/audit_mesen_actor_live_0509.py" "$root/JP/tools/audit_mesen_actor_feedback_0509.py"
if [[ -n "$rom" ]]; then
  python3 "$root/JP/tools/audit_actor_slot_0509.py" "$rom" "$build/actor_lift_rom_hash_audit.json"
  python3 "$root/JP/tools/audit_actor_cpu_abi_0509.py" "$rom" --report "$build/actor_source_cpu_abi_audit.json"
  python3 "$root/JP/tools/audit_actor_spawn_0509.py" "$rom" --report "$build/actor_source_spawn_audit.json"
  python3 "$root/JP/tools/audit_actor_precheck_0509.py" "$rom" --report "$build/actor_source_precheck_audit.json"
  python3 "$root/JP/tools/audit_actor_guard_producers_0509.py" "$rom" --report "$build/actor_source_guard_producer_audit.json"
  python3 "$root/JP/tools/audit_actor_dispatch_chain_0509.py" "$rom" --report "$build/actor_source_indirect_dispatch_audit.json"
fi
# Native title -> intro -> Stage-1 prototype executes real host C++, but
# source assets/physics are provisional. Never fetch commercial art in CI.
if command -v cmake >/dev/null 2>&1 && command -v pkg-config >/dev/null 2>&1 && pkg-config --exists x11; then
  cmake -S "$root/JP/native_demo0510" -B "$build/native_demo0510" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$build/native_demo0510" --parallel
  ctest --test-dir "$build/native_demo0510" --output-on-failure
  echo "TEST PASS ROM-free native title/intro/stage state machine"
else
  echo "SKIP native title/intro/stage demo: X11 development dependency not available"
fi
echo "PASS: 10 native test binaries plus original-ROM headless CLI compiled; ROM-free suites executed"
