# JP native private Windows packaging: source locations, not a public ROM/game payload.
# Imported by Build-Alpha.ps1 and validated before compilation and in Windows CI.
@{
    launchers = @(
        'Play-CVIII.bat'
        'Debug-Stage-Companion.bat'
        'Capture-QA-0602.ps1'
        'Build-And-Play.ps1'
        'Build-And-Play.bat'
        'Resolve-Python.ps1'
        'Control-Profiles.py'
        'Controls.ps1'
        'Controls.bat'
    )
    native_tools = @(
        'jp_asset_pack_0597.py'
        'jp_asset_runtime_0598.py'
        'jp_chr_fetch_report_0600.py'
        'jp_frame_evidence_report_0601.py'
        'jp_nt_trace_report_0606.py'
        'jp_object_oam_report_0609.py'
        'jp_audio_bus_report_0610.py'
        'jp_audio_session_verify_0614.py'
    )
    support_tools = @(
        'jp_password_stage_0593.py'
        'jp_password_debug_menu_0593.py'
        'jp_qa_matrix_0602.py'
        'jp_mapper_audit_0602.py'
        'jp_mesen_sound_requests_0615.py'
        'mesen_jp_sound_requests_0615.lua'
        'jp_sound_priority_paths_0616.py'
        'jp_mesen_gate_report_0616.py'
        'mesen_jp_sound_gates_0616.lua'
        'jp_sound_decision_reference_0617.py'
        'mesen_jp_sound_decisions_0617.lua'
        'jp_audio_ui_chr_0619.py'
    )
}
