# JP0613 — Sound-request and chip-register timing proximity (not attribution)

The owner-only native traces have two **independent** sources:

- JP0612 `CVIII-Sound-Requests.csv`: actual fixed PRG31:$E249 CPU fetch, incoming command A and register snapshots; earlier discarded game events are invisible.
- JP0610 `CVIII-Audio-Registers.csv`: actual 2A03/VRC6 register writes, previous register value, cycle and rapid rewrite classification.

[Conservative analyzer](../tools/jp_sound_request_report_0613.py) validates the exact ten-field request schema and delegates chip-register validation to [JP0610's strict checker](../tools/jp_audio_bus_report_0610.py). Both trace streams must be nondecreasing in CPU cycles. **A backward cycle counter is rejected**, not silently joined after a quick-state load. A bounded requested forward window (default 6,000 CPU cycles, max 100,000) ends at the next request's cycle; same-cycle writes on a following request boundary are excluded. A sound-register write appearing in a window is **only temporally nearby**.

The resulting owner-local JSON contains total requests and hardware writes, request windows with or without observed writes, multi-voice windows, and counts per observed chip/voice. The report intentionally contains no original sound data, per-event copyrighted byte streams or speculative voice allocations.

**Unproved:** Files need a shared capture identity/epoch marker to certify that they originate in the same uninterrupted execution. Saving/loading can create ambiguities even if both individual files are monotonic. A request with no writes in its bounded window is not necessarily dropped; sound writes can be delayed, software-held, or masked. A write inside a request window can belong to an earlier request, to continuous music, or to multiple sources. Music/SFX ownership, rejected effect detection, priority arbitration and independent virtual voices remain OPEN.

## Reproduce

```sh
python3 JP/tools/jp_sound_request_report_0613.py --smoke
python3 JP/tools/jp_sound_request_report_0613.py \
  --requests CVIII-Sound-Requests.csv \
  --registers CVIII-Audio-Registers.csv \
  --json CVIII-Sound-Proximity.json
```

The synthetic fixture exercises three requests, three register writes, two proximity-positive windows, one window without writes, one multi-voice window and eight malformed-schema/timing/window rejection cases. The GitHub Actions ROM-free smoke gate is configured; a user-owned real Japanese-ROM trace comparison has not been collected or independently MesenCE-verified in this work.

**Progress:** no strict semantic promotion. PRG 49,504/262,144 = 18.8843%; VPP 27/100; checkpoint 0508 and first unprocessed fixed bank31 $FB96 remain unchanged. The machine resume state must not be changed for this analyzer-only step.
