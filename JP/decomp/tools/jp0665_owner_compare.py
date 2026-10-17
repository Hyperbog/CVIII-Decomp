#!/usr/bin/env python3
"""Owner-private read-only original-ROM C11 event vs FamiStudio tick comparison.

No notes, samples or ROM bytes are emitted. No claim of NES CPU-cycle parity.
"""
import argparse, ctypes, hashlib, json, re
from pathlib import Path
SHA_ROM='958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28'
SHA_TXT='df25db714eb378072e797230a8d90ff105a3d010d4ea63b36e7a39950ebffd30'
class Ev(ctypes.Structure):
    _fields_=[('tick',ctypes.c_uint64),('source_pc',ctypes.c_uint16),('pitch_table_base_period',ctypes.c_uint16),('destination_period_low',ctypes.c_uint16),('destination_period_high',ctypes.c_uint16),('route',ctypes.c_uint8),('kind',ctypes.c_uint8),('note_index',ctypes.c_uint8),('note_byte',ctypes.c_uint8),('duration_units',ctypes.c_uint8),('sound_request_id',ctypes.c_uint8),('duration_ticks',ctypes.c_uint16),('exact_register_values_verified',ctypes.c_bool)]
class Voice(ctypes.Structure):
    _fields_=[('bank05',ctypes.POINTER(ctypes.c_uint8)),('pc',ctypes.c_uint16),('fd_return',ctypes.c_uint16),('fb_anchor',ctypes.c_uint16),('repeat_site',ctypes.c_uint16),('route',ctypes.c_uint8),('unit',ctypes.c_uint8),('repeat_counter',ctypes.c_uint8),('octave',ctypes.c_uint8),('ticks',ctypes.c_uint64),('events',ctypes.c_uint64),('has_return',ctypes.c_bool),('has_anchor',ctypes.c_bool),('has_repeat',ctypes.c_bool),('ended',ctypes.c_bool),('unknown_effects',ctypes.c_bool)]
def attrs(line):return dict(re.findall(r'([A-Za-z][A-Za-z0-9]*)="([^"\r\n]*)"',line))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--famistudio-txt',type=Path,required=True);ap.add_argument('--lib',type=Path,required=True);ap.add_argument('--json',type=Path);ap.add_argument('--ticks',type=int,default=1024);a=ap.parse_args()
 rb=a.rom.read_bytes();tb=a.famistudio_txt.read_bytes();assert hashlib.sha256(rb).hexdigest()==SHA_ROM and len(rb)==393232, 'wrong ROM';assert hashlib.sha256(tb).hexdigest()==SHA_TXT,'unexpected FamiStudio TXT';assert 1<=a.ticks<=20000
 raw5=(ctypes.c_uint8*16384).from_buffer_copy(rb[16+5*16384:16+6*16384]);rawc=(ctypes.c_uint8*16384).from_buffer_copy(rb[16+12*16384:16+13*16384]);v=(Voice*6)()
 lib=ctypes.CDLL(str(a.lib.resolve()));lib.cviii_jp0665_init.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(Voice)];lib.cviii_jp0665_init.restype=ctypes.c_bool
 lib.cviii_jp0665_next.argtypes=[ctypes.POINTER(Voice),ctypes.POINTER(Ev)];lib.cviii_jp0665_next.restype=ctypes.c_int
 assert lib.cviii_jp0665_init(raw5,16384,rawc,16384,v),'wrong metadata or buffer ABI'
 original={i:[] for i in [0,1,2,3,4,7]}
 for voice in v:
  for i in range(25000):
   e=Ev();t=lib.cviii_jp0665_next(ctypes.byref(voice),ctypes.byref(e));assert t==1, f'fail during mode{voice.route} event {i}, code {t}'
   if e.tick>=a.ticks:break
   if (e.kind==1 and voice.route!=7) or (e.kind in [3,4] and voice.route==7):
    original[voice.route].append((e.tick,e.kind))
  else:raise AssertionError('decoder failed to advance')
 songs={};inst={};ch=None;pat=None
 for l in tb.decode('utf-8-sig').splitlines():
  typ=l.strip().split(' ',1)[0] if l.strip() else ''; d=attrs(l)
  if typ=='Channel':ch=d['Type'];songs[ch]={};inst[ch]=[]
  elif typ=='Pattern' and ch:pat=d['Name'];songs[ch][pat]=[]
  elif typ=='Note' and ch and 'Value' in d:songs[ch][pat].append((int(d['Time']),d['Value']))
  elif typ=='PatternInstance' and ch:inst[ch].append((int(d['Time']),d['Pattern']))
 track={}
 for ch,p in songs.items():track[ch]=[(idx*256+tim,note) for idx,name in inst[ch] for tim,note in p[name] if idx*256+tim<a.ticks]
 comparison={}
 for m,ch in [(0,'VRC6Square1'),(1,'VRC6Square2'),(2,'VRC6Saw'),(3,'Square1'),(4,'Square2'),(7,'DPCM')]:
  got={t for t,k in original[m] if (m!=7 or k==4)}
  expected={t for t,n in track[ch]}
  comparison[ch]={'original_candidate_ticks':len(got),'famistudio_trigger_ticks':len(expected),'matching_tick_positions':len(got&expected),'missing_original_ticks_from_famistudio':len(got-expected),'missing_famistudio_ticks_from_original':len(expected-got)}
 # Noise is event volume/retrigger rich: one original noise program request
 # can produce >1 reconstructed tracker note row, so do not force one-to-one.
 srcnoise={t for t,k in original[7] if k==3}; famnoise={t for t,n in track['Noise']}
 comparison['Noise']={'original_noise_program_request_ticks':len(srcnoise),'famistudio_note_triggers':len(famnoise),'source_requests_visible_in_tracker_at_same_tick':len(srcnoise&famnoise),'warning':'noise effect program can produce multiple tracker note rows'}
 result={'schema':'jp0665-native-c11-vs-famistudio-tick-metadata/v1','original_rom_source_authentication':'SHA256 exact','famistudio_txt_sha256':SHA_TXT,'first_tick_inclusive':0,'last_tick_exclusive':a.ticks,'music_program':'51','command_to_channels':'6502 static physical route, not live gameplay','comparisons':comparison,'raw_events_emitted':False,'verified_pcm_parity':False,'verified_envelopes':False,'verified_original_game_liveness':False,'phase':'detached native read-only prototype'}
 if a.json:a.json.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
