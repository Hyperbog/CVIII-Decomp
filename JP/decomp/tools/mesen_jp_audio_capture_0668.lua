-- JP0668: Read-only original Japanese ROM hardware WRITE observer, plus
-- deterministic controller schedule from project's historic JP0551 trial.
-- Only inputs are injected. No ROM, RAM, APU, mapper or CPU state is patched.
-- The original ROM must be loaded and power-cycled after this script starts.
-- The private log, executable hashes and cycle interpretation require audit.
local TARGET_FRAMES=1100
local MAX_WRITES=199999
local frame,writes,polls=0,0,0
local started=false
local done=false
local last_clock=-1

local function emit(s) emu.log(s) end
local function fault(why)
  if not done then emit('JP0668_INVALID '..why) end
  done=true
end
local function clock()
  local ok,s=pcall(emu.getState)
  local v=ok and type(s)=='table' and type(s.cpu)=='table' and s.cpu.cycleCount or nil
  if type(v)~='number' or v<0 or v>9007199254740991 or v~=math.floor(v) then
    fault('cpu_cycleCount_unavailable')
    return nil
  end
  if v<last_clock then fault('cycle_regression');return nil end
  last_clock=v
  return v
end
local function on_reset()
  if started or frame~=0 or writes~=0 or polls~=0 then
    fault('duplicate_reset_or_mid_session_reset')
    return
  end
  started=true
  emit('JP0668_BOUNDARY reset')
end
local function in_range(n,a,b) return n>=a and n<=b end
local function mask_at(n)
  local m=0
  if in_range(n,90,92) or in_range(n,180,182) or
     in_range(n,300,302) or in_range(n,530,531) or in_range(n,745,746)
     then m=m|8 end
  if in_range(n,370,520) or in_range(n,645,730) or
     in_range(n,830,1065) then m=m|128 end
  if in_range(n,460,469) or in_range(n,1010,1012) then m=m|1 end
  if in_range(n,470,475) or in_range(n,650,652) or
     in_range(n,870,872) then m=m|2 end
  return m
end
local function on_input()
  if done or not started then return end
  local c=clock();if not c then return end
  if polls~=frame then fault('not_exactly_one_input_poll_per_frame');return end
  local mask=mask_at(frame+1)
  local t={a=(mask&1)~=0,b=(mask&2)~=0,select=false,start=(mask&8)~=0,
           up=false,down=false,left=false,right=(mask&128)~=0}
  emu.setInput(t,0)
  emu.setInput({a=false,b=false,select=false,start=false,up=false,
                down=false,left=false,right=false},1)
  polls=polls+1
  emit(string.format('JP0668_INPUT %d %.0f %02X',polls,c,mask))
end
local function register(startaddr,endaddr)
  emu.addMemoryCallback(function(address,value)
    if done or not started then return end
    if writes>=MAX_WRITES then
      emit('JP0668_TRUNCATED');done=true;return
    end
    local c=clock();if not c then return end
    if type(address)~='number' or type(value)~='number' or
       address<0 or address>65535 or value<0 or value>255 then
      fault('invalid_register_callback');return
    end
    writes=writes+1
    emit(string.format('JP0668_WRITE %d %.0f %04X %02X',writes,c,address,value))
  end,emu.callbackType.write,startaddr,endaddr,emu.cpuType.nes,emu.memType.nesMemory)
end
register(0x4000,0x4013)
register(0x4015,0x4015)
register(0x4017,0x4017)
register(0x9000,0x9003)
register(0xA000,0xA002)
register(0xB000,0xB002)
emu.addEventCallback(on_reset,emu.eventType.reset)
emu.addEventCallback(function()
  if done or not started then return end
  local c=clock();if not c then return end
  if polls~=frame+1 then fault('input_poll_frame_count_mismatch');return end
  frame=frame+1
  emit(string.format('JP0668_FRAME %d %.0f',frame,c))
  if frame==TARGET_FRAMES then
    done=true
    emit(string.format('JP0668_END %d %d %d %.0f',frame,writes,polls,c))
    emu.stop(0)
  end
end,emu.eventType.endFrame)
emu.addEventCallback(function() if started and not done then
  fault('state_loaded') end end,emu.eventType.stateLoaded)
emu.addEventCallback(function() if started and not done then
  fault('state_saved') end end,emu.eventType.stateSaved)
emu.addEventCallback(function() if started and not done then
  fault('script_interrupted') end end,emu.eventType.scriptEnded)
emit('JP0668_READY v1')
