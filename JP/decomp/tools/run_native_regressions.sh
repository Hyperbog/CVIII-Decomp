#!/usr/bin/env bash
# JP native subsystem regression gate; no original ROM is committed.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
src="$root/JP/decomp/src"; tests="$root/JP/decomp/tests"
build="$(mktemp -d "${TMPDIR:-/tmp}/c3-jp-tests.XXXXXXXX")"
trap 'rm -rf "$build"' EXIT
cxx="${CXX:-g++}"
flags=(-std=c++20 -O2 -Wall -Wextra -Werror -pedantic -I "$src")
rom="${1:-}"
python3 "$root/JP/decomp/tools/audit_folder_consolidation_0662.py"
# Shared AI decomp/recomp semantic-evidence and native-source gates (ROM free).
python3 -m unittest discover -s "$root/SharedDecomp" -p 'test_*.py' -v
python3 "$root/SharedDecomp/workflow.py" bank "$root/JP/decomp/analysis/0539_RAW0A_BANK_MAP.json"
python3 -m unittest discover -s "$root/JP/decomp/tools" -p 'test_0538_bank_workflow.py' -v
python3 "$root/JP/decomp/tools/export_0538_bank_workflow.py" --smoke
python3 -m unittest discover -s "$root/JP/decomp/tools/native" -p 'test_native_lookup_smoke.py' -v
# Durable per-checkpoint research evidence gate. This catches provenance
# regressions quickly, before slower native C++ compilation and CTest.
python3 -m py_compile "$root/JP/decomp/tools/audit_native_evidence_ledger.py"
python3 "$root/JP/decomp/tools/audit_native_evidence_ledger.py"
# Reconstruct the recoverable historical 0500-0508 physical PRG union.
# No globally new byte claims: the 43,475-byte earlier baseline is unmapped.
python3 -m py_compile "$root/JP/decomp/tools/test_recomp_6502_0525.py"
python3 -m py_compile "$root/JP/decomp/tools/audit_historical_prg_0526.py" "$root/JP/decomp/tools/test_recomp_6502_0526.py"
# Source reproducibility: ROM-free assembler smoke, original-ROM full 25-bank rebuild.
python3 -m py_compile "$root/JP/decomp/tools/lift_bank05_scripts_0531.py"
PYTHONPATH="$root/JP/decomp/tools" python3 -c 'import lift_bank05_scripts_0531 as s; assert sum(b-a for _,a,b,_ in s.WINDOWS)==14168 and len(s.WINDOWS)==3'
python3 -m py_compile "$root/JP/decomp/tools/lift_fixed_dispatch_0530.py"
PYTHONPATH="$root/JP/decomp/tools" python3 -c 'import lift_fixed_dispatch_0530 as s; assert (sum(b-a for a,b,_ in s.HIST04FE),sum(b-a for a,b,_ in s.HIST04FF),sum(b-a for a,b,_ in s.HIST0500))==(957,931,982)'
# JP 0532: verify original sound parser and bank04 source-lift invariants.
# JP 0533 original sound interpreter and metadata proof (source-only CI).
python3 -m py_compile "$root/JP/decomp/tools/lift_bank0c_sound_0533.py" "$root/JP/decomp/tools/test_bank0c_sound_0533.py"
# 0535: ROM-free state-pointer/6502 source smoke and optional authenticated JP-ROM
# Whole raw0A bank hierarchical reconstruction: ROM-free checks in CI;
# private original-JP ROM source / CPU traversal and full 25-bank tests locally.
python3 -m py_compile "$root/JP/decomp/tools/recover_raw0a_hierarchy.py" "$root/JP/decomp/tools/test_raw0a_lookup_cpu.py" "$root/JP/decomp/tools/build_fullbank_0a_source.py" "$root/JP/decomp/tools/test_fullbank_raw0a_0538.py"
python3 "$root/JP/decomp/tools/build_fullbank_0a_source.py" --smoke
python3 "$root/JP/decomp/tools/test_fullbank_raw0a_0538.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_fullbank_raw0a_0538.py" --rom "$rom"
fi
if [[ -n "$rom" ]]; then
  # Authenticated local-ROM only: 16KiB partition hashes and real original-6502 vs host-C++ lookup.
  python3 "$root/JP/decomp/tools/build_fullbank_0a_source.py" --rom "$rom" --out "$build/0539_fullbank"
  python3 "$root/JP/decomp/tools/export_0538_bank_workflow.py" --atlas "$build/0539_fullbank/raw0a_hierarchy_atlas.json" --rom "$rom" --out "$build/0539_evidence"
  python3 "$root/JP/decomp/tools/native/replay_raw0a_native.py" --rom "$rom" --cases "$build/0539_fullbank/raw0a_bounded_selector_cases.json" --out "$build/0539_native"
fi
# 0542: both bank0A B873 descriptor gate branches are covered by original
# 6502-vs-native parity. Non-sentinel 9x256 synthetic cases run without ROM.
python3 -m py_compile "$root/JP/decomp/tools/replay_room_gate_0542.py" "$root/JP/decomp/tools/test_room_gate_0542.py"
python3 "$root/JP/decomp/tools/test_room_gate_0542.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_room_gate_0542.py" --rom "$rom" --out "$build/0542_gate"
fi
# 0541: original fixed E526 -> two bank0A inline-tail dispatches ->
# B873 sentinel -> E785 22-slot clear -> bank0E object stream loader.
# ROM-free synthetic state replay runs in public CI. Authenticated retail
# CPU-vs-C++ 1280-case comparisons run only if supplied original JP ROM.
python3 -m py_compile "$root/JP/decomp/tools/replay_room_state_0541.py" "$root/JP/decomp/tools/test_room_state_0541.py"
python3 "$root/JP/decomp/tools/test_room_state_0541.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_room_state_0541.py" --rom "$rom" --out "$build/0541_state_bridge"
fi
# 0543: entire post-loader caller and six original cross-bank dispatch envelopes.
# 0546: authenticated-ROM mode now executes all six 6502 foreign scripts
# against independent native translations with zero callbacks; synthetic
# ROM-free mode retains explicitly labeled ID3/ID4 fixtures.
# 0551: native Windows Mesen headless transcript parser; strictly ROM-free in CI.
python3 -m py_compile "$root/JP/decomp/tools/audit_mesen_windows_0551.py" "$root/JP/decomp/tools/test_mesen_windows_0551.py"
python3 "$root/JP/decomp/tools/test_mesen_windows_0551.py"
# 0553 combined native fixed-bank31 and raw bank0A static recompilation.
# ROM-free CI checks compiled dispatch and corruption rejection; authenticated
# private ROM mode independently compares 11740 CPU steps + 1280 room cases.
python3 -m py_compile "$root/JP/decomp/tools/static_recompile_boot_0553.py" "$root/JP/decomp/tools/static_recompile_fixed_0553.py" "$root/JP/decomp/tools/test_native_boot_0553.py"
python3 "$root/JP/decomp/tools/test_native_boot_0553.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_native_boot_0553.py" --rom "$rom" --compiler "$cxx"
fi
# 0552 full bank0A static native 6502 compilation (2357 instruction sites).
# ROM-free C++ compilation and fail-closed behavior; optional authenticated
# original 6502 comparison of all 1280 room cases plus 135 selector cases.
python3 -m py_compile "$root/JP/decomp/tools/static_recompile_bank0a.py" "$root/JP/decomp/tools/test_static_bank0a_0552.py"
# 0562 source-driven C11 emitter. Public CI uses ROM-free fixture checks;
# authenticated source-to-C output is generated locally only.
python3 "$root/JP/decomp/tools/static_recompile_c_0562.py" --smoke
# JP 0563: compile actual C emitter fixture without copyrighted ROM.
python3 "$root/JP/decomp/tools/test_c6502_regen_0563.py" --smoke
# JP 0564: whole-current-native-site C11 codegen contract (ROM-free).
python3 "$root/JP/decomp/tools/static_recompile_boot_c_0564.py" --smoke
# 0565: fully linked ROM-free C-only host (synthetic compiled bank+fixed source).
python3 "$root/JP/decomp/tools/test_c6502_native_host_0565.py" --smoke
# 0566 optional upstream PolyForm-NC NESRecomp cycle backend audit/probe.
python3 "$root/JP/decomp/tools/probe_nesrecomp_cycle_0566.py" --smoke
python3 "$root/JP/decomp/tools/test_nesrecomp_cycle_0566.py"
python3 "$root/JP/decomp/tools/test_nesrecomp_cycle_0568.py"
python3 "$root/JP/decomp/tools/test_cycle_synthetic_rom_0569.py" --smoke
python3 "$root/JP/decomp/tools/check_cycle_stats_0571.py" --smoke
python3 "$root/JP/decomp/tools/build_original_c11_0573.py" --smoke
python3 -m py_compile "$root/JP/decomp/tools/regen_c11_0564.py"
if [[ -n "$rom" ]]; then
  # Temporary source generation, C11 compile, independent 135-case 6502 replay.
  python3 "$root/JP/decomp/tools/test_c6502_regen_0563.py" --rom "$rom"
fi
python3 "$root/JP/decomp/tools/test_static_bank0a_0552.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_static_bank0a_0552.py" --rom "$rom"
fi
# 0549: fail-closed ROM-free parser and real-Mesen capture schema; no retail ROM in CI.
python3 -m py_compile "$root/JP/decomp/tools/audit_mesen_state13_0549.py" "$root/JP/decomp/tools/test_mesen_state13_0549.py"
python3 "$root/JP/decomp/tools/test_mesen_state13_0549.py"
# 0550: deterministic natural-Mesen Stage-1 fork search; ROM-free evidence/plan only.
python3 -m py_compile "$root/JP/decomp/tools/search_mesen_state13_0550.py" "$root/JP/decomp/tools/test_state13_search_0550.py"
python3 "$root/JP/decomp/tools/test_state13_search_0550.py"
python3 "$root/JP/decomp/tools/search_mesen_state13_0550.py" --plan > "$build/0550_state13_search_plan.json"
# 0548: authenticated original CPU reset->first NMI, scripted external PPU/IRQ source.
# CI runs ROM-free CPU and protocol checks; original ROM replay is opt-in.
python3 -m py_compile "$root/JP/decomp/tools/replay_reset_0548.py" "$root/JP/decomp/tools/test_reset_0548.py"
python3 "$root/JP/decomp/tools/test_reset_0548.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_reset_0548.py" --rom "$rom" --out "$build/0548_reset_nmi.json"
fi
# 0547: original 6502 NMI inline-dispatch -> native integrated six-script path.
python3 -m py_compile "$root/JP/decomp/tools/replay_nmi_dispatch_0547.py" "$root/JP/decomp/tools/test_nmi_dispatch_0547.py"
python3 "$root/JP/decomp/tools/test_nmi_dispatch_0547.py" --smoke
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_nmi_dispatch_0547.py" --rom "$rom" --out "$build/0547_nmi_dispatch" --cxx "$cxx"
fi
python3 -m py_compile "$root/JP/decomp/tools/replay_postdispatch_0543.py" "$root/JP/decomp/tools/test_postdispatch_0543.py"
python3 "$root/JP/decomp/tools/test_postdispatch_0543.py" --smoke
if command -v clang++ >/dev/null 2>&1; then
    python3 "$root/JP/decomp/tools/test_postdispatch_0543.py" --smoke --cxx clang++
fi
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_postdispatch_0543.py" --rom "$rom" --out "$build/0543_post_dispatch"
fi
# 0540: native translated JP room0A loader (five room streams),
# optional full authenticated original-6502/native 1280-case trace replay.
python3 -m py_compile "$root/JP/decomp/tools/replay_room_loader_0540.py" "$root/JP/decomp/tools/test_room_loader_0540.py"
python3 "$root/JP/decomp/tools/test_room_loader_0540.py" --smoke
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_room_loader_0540.py" --rom "$rom"
fi
# 0536 0A/0E source schema, plus authenticated original ROM optional full recomp + corruption tests.
python3 -m py_compile "$root/JP/decomp/tools/lift_bank0a_0508_0536.py" "$root/JP/decomp/tools/test_bank0a_0508_0536.py"
python3 "$root/JP/decomp/tools/test_bank0a_0508_0536.py"
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_bank0a_0508_0536.py" --rom "$rom"
fi
python3 -m py_compile "$root/JP/decomp/tools/lift_bank0a_state_0535.py" "$root/JP/decomp/tools/test_bank0a_state_0535.py"
python3 "$root/JP/decomp/tools/test_bank0a_state_0535.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_bank0a_state_0535.py" --rom "$rom"
fi
python3 -m py_compile "$root/JP/decomp/tools/lift_sound_phrase_ai_0534.py" "$root/JP/decomp/tools/test_sound_phrase_ai_0534.py"
python3 "$root/JP/decomp/tools/test_sound_phrase_ai_0534.py"
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/test_sound_phrase_ai_0534.py" --rom "$rom"
fi
python3 "$root/JP/decomp/tools/test_bank0c_sound_0533.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_bank0c_sound_0533.py" --rom "$rom"
fi
python3 -m py_compile "$root/JP/decomp/tools/lift_bank04_parser_0532.py" "$root/JP/decomp/tools/test_bank04_parser_0532.py"
python3 "$root/JP/decomp/tools/test_bank04_parser_0532.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_bank04_parser_0532.py" --rom "$rom"
fi
# Whole physical 16KiB raw0A bank is the unit of investigation. Candidate
# opcodes remain explicitly NOT CERTIFIED; do not grant new strict PRG bytes.
python3 -m py_compile "$root/JP/decomp/tools/recover_raw0a_bank_0537.py" "$root/JP/decomp/tools/test_fullbank_raw0a_0537.py"
python3 "$root/JP/decomp/tools/test_fullbank_raw0a_0537.py" --smoke
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_fullbank_raw0a_0537.py" --rom "$rom"
fi
python3 -m py_compile "$root/JP/decomp/tools/build_whole_cart_recomp_0529.py"
python3 "$root/JP/decomp/tools/build_whole_cart_recomp_0529.py" --smoke
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/build_whole_cart_recomp_0529.py" --rom "$rom" --out "$build/0529_whole_cart"
fi
python3 -m py_compile "$root/JP/decomp/tools/audit_bank05_certificate_0527.py"
python3 "$root/JP/decomp/tools/audit_bank05_certificate_0527.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/audit_bank05_certificate_0527.py" --rom "$rom"
fi
python3 "$root/JP/decomp/tools/audit_historical_prg_0526.py"
python3 "$root/JP/decomp/tools/test_recomp_6502_0526.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/audit_historical_prg_0526.py" --rom "$rom"
    python3 "$root/JP/decomp/tools/test_recomp_6502_0526.py" --rom "$rom"
fi
python3 "$root/JP/decomp/tools/test_recomp_6502_0525.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_recomp_6502_0525.py" --rom "$rom"
fi
python3 "$root/JP/decomp/tools/audit_prg_recomp_0525.py"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/audit_prg_recomp_0525.py" --rom "$rom"
fi
# Source-window accounting is intentionally ROM-free in CI. With an authentic
# private Japanese ROM, also verify 25 physical source ranges and all 0501/0508
# certificate fingerprints; never add unclaimed historical bytes to the floor.
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/audit_native_coverage_0518.py" --rom "$rom"
else
    python3 "$root/JP/decomp/tools/audit_native_coverage_0518.py"
fi

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
python3 "$root/JP/decomp/tools/test_vrc6_irq_cross_language_0508.py" "$build/vrc6_irq_trace_driver"
python3 "$root/JP/decomp/tests/test_nes_reuse.py"
python3 "$root/JP/decomp/tests/test_nes_mapper_family.py"
python3 "$root/JP/decomp/tests/test_nes_certified_reuse.py"
python3 "$root/JP/decomp/tests/test_nes_cdl_bridge_0508.py"
python3 "$root/JP/decomp/tests/test_synthetic_crossedition_0508.py"
python3 "$root/JP/decomp/tests/test_nes_fds_catalog.py"
python3 "$root/JP/decomp/tests/test_nes_trace_compare.py"
python3 "$root/JP/decomp/tests/test_mesen_reference_0508.py"
python3 "$root/JP/decomp/tests/test_mesen_stage1_branch_0508.py"
python3 "$root/JP/decomp/tests/test_mesen_fixed_live_0508.py"
python3 "$root/JP/decomp/tests/test_native_mesen_pc_0509.py"
python3 -m py_compile "$root/JP/decomp/tools/audit_mesen_stage1_branch_0508.py" "$root/JP/decomp/tools/audit_mesen_stage1_crossedition_0508.py" "$root/JP/decomp/tools/audit_mesen_fixed_live_0508.py"
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
compile actor_collision_tail_0517 "$src/actor_collision_result_0517.cpp" "$src/actor_collision_measure_0516.cpp" "$src/actor_collision_precheck_0515.cpp" "$src/actor_preflight_0514.cpp"
compile scheduler_postcollision_0519 "$src/scheduler_postcollision_0519.cpp"
compile scheduler_followup_0520 "$src/scheduler_bd11_followup_0520.cpp" "$src/scheduler_postcollision_0519.cpp"
compile scheduler_linked_actor_0524 "$src/scheduler_linked_actor_0524.cpp" "$src/scheduler_actor_reset_0523.cpp" "$src/scheduler_fe63_0522.cpp"
"$build/scheduler_linked_actor_0524"
echo "TEST PASS original JP type4D linked actor source (110592 bounded cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_linked_actor_0524_rom.py"
if [[ -n "$rom" ]]; then python3 "$root/JP/decomp/tools/audit_linked_actor_0524_rom.py" "$rom"; fi
compile scheduler_actor_reset_0523 "$src/scheduler_actor_reset_0523.cpp" "$src/scheduler_fe63_0522.cpp"
"$build/scheduler_actor_reset_0523"
echo "TEST PASS source-bounded raw0B 8193 non-4D actor reset: 138240 supported / 9216 rejected"
python3 -m py_compile "$root/JP/decomp/tools/audit_actor_reset_0523_rom.py"
if [[ -n "$rom" ]]; then python3 "$root/JP/decomp/tools/audit_actor_reset_0523_rom.py" "$rom"; fi
compile scheduler_fe63_0522 "$src/scheduler_fe63_0522.cpp"
"$build/scheduler_fe63_0522"
echo "TEST PASS provisional 0522 bounded FE63 actor callback foundation (110592 supported, 18432 rejected)"
python3 -m py_compile "$root/JP/decomp/tools/audit_fe63_0522_rom.py"
if [[ -n "$rom" ]]; then python3 "$root/JP/decomp/tools/audit_fe63_0522_rom.py" "$rom"; fi
compile actor_animation_ef93_0521 "$src/actor_animation_ef93_0521.cpp" "$src/scheduler_bd11_followup_0520.cpp" "$src/scheduler_postcollision_0519.cpp"
"$build/actor_animation_ef93_0521"
echo "TEST PASS original JP EF93 source animation descriptor0E (65547 bounded cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_animation_ef93_0521.py"
python3 -m py_compile "$root/JP/decomp/tools/audit_scheduler_followup_0520.py"
"$build/scheduler_followup_0520"
echo "TEST PASS source-mapped raw0B BD11 and fixed31 FE34 scheduler continuation (77827 cases)"
"$build/scheduler_postcollision_0519"
echo "TEST PASS original fixed bank31 FDFE actor scheduler branch (73731 cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_actor_collision_tail_0517.py"
"$build/actor_collision_tail_0517"
echo 'TEST PASS original JP $B235 postcollision tail and empty attachment scan (65539 cases)'
python3 -m py_compile "$root/JP/decomp/tools/audit_collision_measure_0516.py"
"$build/actor_collision_measure_0516"
echo "TEST PASS original JP raw0B B339/80B3/80C1 collision distance (139343 source-bounded cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_b217_original_mesen_0515.py"
"$build/actor_collision_precheck_0515"
echo "TEST PASS JP original B217 collision admission and B1F8 composition (82947 cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_actor_preflight_0514.py"
"$build/actor_preflight_0514"
echo "TEST PASS original JP 0514 delta producer / actor preflight (100357 cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_vertical_synthetic_0513.py"
"$build/actor_displacement_vertical_prg0b_0513"
"$build/actor_post8843_0513"
echo "TEST PASS original JP 0513 vertical prefix and 8843 continuation (270351 cases)"
"$build/actor_displacement_prg0b_0512"
python3 -m py_compile "$root/JP/decomp/tools/audit_mesen_displacement_0512.py"
echo 'TEST PASS faithful original JP $80E3 horizontal displacement (73742 cases)'
python3 -m py_compile "$root/JP/decomp/tools/audit_mesen_actor_motion_0511.py"
"$build/actor_motion_prg0b_0511"
echo "TEST PASS original JP raw0B two-axis native actor motion (69646 source-bounded cases)"
python3 -m py_compile "$root/JP/decomp/tools/audit_native_row32_live_0510.py"
"$build/actor_event_row32_0510"
echo "TEST PASS source-lift original JP row32 (4111 ROM-free boundary cases)"
"$build/cpu_2a03"
echo "TEST PASS cpu_2a03 (262144 exhaustive ADC/SBC and control-stack tests)"
"$build/native_machine_0509"
echo "TEST PASS native_machine_0509 (synthetic mapped CPU/VRC6/PPU/NMI)"
"$cxx" "${flags[@]}" "$root/JP/decomp/tools/native_probe_0509.cpp" "$src/cpu_2a03.cpp" "$src/native_machine_0509.cpp" "$src/vrc6_mapper.cpp" "$src/vrc6_irq.cpp" -o "$build/cviii-headless-0509"
echo "COMPILE PASS cviii-headless-0509 (requires original JP ROM to run)"
if [[ -n "$rom" ]]; then
    python3 "$root/JP/decomp/tools/test_native_mesen_pc_0509.py" "$build/cviii-headless-0509" "$rom"
    echo "TEST PASS authenticated JP original-ROM 7828-PC golden Mesen2 prefix"
fi
python3 -m py_compile "$root/JP/decomp/tools/audit_actor_slot_0509.py" "$root/JP/decomp/tools/audit_actor_cpu_abi_0509.py" "$root/JP/decomp/tools/audit_actor_spawn_0509.py" "$root/JP/decomp/tools/audit_actor_precheck_0509.py" "$root/JP/decomp/tools/audit_actor_guard_producers_0509.py" "$root/JP/decomp/tools/audit_actor_dispatch_chain_0509.py" "$root/JP/decomp/tools/audit_mesen_actor_live_0509.py" "$root/JP/decomp/tools/audit_mesen_actor_feedback_0509.py"
if [[ -n "$rom" ]]; then
  python3 "$root/JP/decomp/tools/audit_actor_slot_0509.py" "$rom" "$build/actor_lift_rom_hash_audit.json"
  python3 "$root/JP/decomp/tools/audit_actor_cpu_abi_0509.py" "$rom" --report "$build/actor_source_cpu_abi_audit.json"
  python3 "$root/JP/decomp/tools/audit_actor_spawn_0509.py" "$rom" --report "$build/actor_source_spawn_audit.json"
  python3 "$root/JP/decomp/tools/audit_actor_precheck_0509.py" "$rom" --report "$build/actor_source_precheck_audit.json"
  python3 "$root/JP/decomp/tools/audit_actor_guard_producers_0509.py" "$rom" --report "$build/actor_source_guard_producer_audit.json"
  python3 "$root/JP/decomp/tools/audit_actor_dispatch_chain_0509.py" "$rom" --report "$build/actor_source_indirect_dispatch_audit.json"
fi
# Native title -> intro -> Stage-1 prototype executes real host C++, but
# source assets/physics are provisional. Never fetch commercial art in CI.
if command -v cmake >/dev/null 2>&1 && command -v pkg-config >/dev/null 2>&1 && pkg-config --exists x11; then
  cmake -S "$root/JP/decomp/legacy/native_demo0510" -B "$build/native_demo0510" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$build/native_demo0510" --parallel
  ctest --test-dir "$build/native_demo0510" --output-on-failure
  echo "TEST PASS ROM-free native title/intro/stage state machine"
else
  echo "SKIP native title/intro/stage demo: X11 development dependency not available"
fi
echo "PASS: native test binaries and original-ROM headless CLI compiled; ROM-free suites executed"
# JP0658 bounded original room clear + PPU stream contract; media-free.
python3 "$root/JP/decomp/tools/jp_room_clear_0658.py" --smoke
# JP0659 synthetic stage-room source and exact reversible resource geometry.
python3 "$root/JP/decomp/tools/jp_room_stream_0659.py" --smoke
python3 "$root/JP/decomp/tools/jp_room_resources_0659.py" --smoke
# JP0815: ROM-free visual descriptor ABI and unsafe-count rejection.
python3 "$root/JP/decomp/tools/jp_stage1_visual_identity_0815.py" --smoke
# JP0816: 6502 source phase and 16-bit camera arithmetic, ROM-free.
python3 "$root/JP/decomp/tools/jp_stage1_horizontal_collision_0816.py" --smoke
# JP0817 original event-source motion and response predicates.
python3 "$root/JP/decomp/tools/jp_stage1_activation_response_0817.py" --smoke
# JP0818: original B249/B258 control-flow and row32 ancestry smoke.
python3 "$root/JP/decomp/tools/jp_stage1_reaction_lineage_0818.py" --smoke
# JP0819: original $B3EC absolute-byte and partner-mask arithmetic.
python3 "$root/JP/decomp/tools/jp_stage1_interaction_lifetime_0819.py" --smoke
# JP0821: owner-ROM source audit and private natural Mesen replay CLI smoke.
python3 "$root/JP/decomp/tools/jp_stage1_contact_effects_0821.py" --smoke
python3 "$root/JP/decomp/tools/jp_stage1_natural_contact_lifetime_0821.py" --smoke

# JP0738: original/native camera-actor comparison parser on entirely invented
# ZIP/CYCFRAME records; authentic owner gameplay requires separate private logs.
python3 "$root/JP/decomp/tools/jp0738_camera_window.py" --smoke

# JP0738C: verify the older original-Mesen/native-JP0719 archived ZIP
# comparator using invented RAM, input and CHR; retail files stay private.
python3 "$root/JP/decomp/tools/jp0738_compare_jp0719_zip.py" --smoke

# JP0739: ROM-free fail-closed original $62 static writer candidate census.
# Synthetic matches do not prove naturally executed stores or source credit.
python3 "$root/JP/decomp/tools/jp0739_mode62_writer_census.py" --smoke

# JP0740: synthetic-only original/native CPU-write capture provenance.
# The ROM-locked original replay is PRIVATE and is not executed in CI.
python3 "$root/JP/decomp/tools/jp0740_trace_verify.py" --smoke
python3 "$root/JP/recomp/tools/jp0740_native_write_overlay.py" --smoke
"${CC:-cc}" -std=c11 -Wall -Wextra -Werror -pedantic -fsyntax-only \
  "$root/JP/recomp/native/rom_runtime_0732/cviii_jp0740_native_trace.c"


# JP0741: invented and nonretail exact-observed-CPU-bus alignment gate.
# Requires a unique 32-event opcode-PC, bus and relative-cycle trajectory;
# ambiguities and approximate frame matching refuse a first-writer claim.
python3 "$root/JP/decomp/tools/jp0741_first_write_compare.py" --smoke

# JP0743: owner-JP0718 Mesen absolute/local input epoch conversion guards.
# No actual ROM or recorded original user button data are in public CI.
python3 "$root/JP/decomp/tools/jp0743_native_input_epoch.py" --smoke

# Stage 1 real-replay acceptance CLI must load without owner ROM/media.
# Actual acceptance deliberately fails when camera/player/room differ.
python3 "$root/JP/recomp/tools/run_stage1_original_acceptance.py" --help >/dev/null
