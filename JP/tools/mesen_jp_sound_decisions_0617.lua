-- JP0617: owner-private MesenCE/Mesen2 original JP sound-dispatch decisions.
-- All observations are read-only; no CPU/mapper/APU change is made.
-- Only attribute the $8852 path while fixed E249's $0C wrapper is active.
local ram=emu.memType.nesInternalRam
local next_id=0
local pending=nil
local count=0
local max_lines=40000

local function byte(addr) return emu.read(addr,ram) end
local function active() return byte(0x23)==0x0C and byte(0x26)==0xFF end
local function log(line)
  if count==max_lines then emu.log('JP0617_TRUNCATED') end
  if count>=max_lines then return end
  emu.log(line)
  count=count+1
end
local function fault(why)
  log('JP0617_INVALID '..why)
end
local function on_entry()
  if pending~=nil then fault('nested_dispatch'); return end
  local command=byte(0xEF)
  pending={id=next_id,command=command,low=byte(0x0109),
           priority=byte(0x019E),counter=byte(0x06DD)}
  log(string.format('JP0617_ENTRY %d 8852 %02X %02X %02X %02X',
      pending.id,command,pending.low,pending.priority,pending.counter))
  next_id=next_id+1
end
local function on_terminal(which,pc)
  if pending==nil then fault('orphan_terminal'); return end
  local p=pending
  log(string.format('JP0617_EXIT %d %s %04X %02X %02X %02X %02X',
      p.id,which,pc,byte(0xEF),byte(0x0109),byte(0x019E),byte(0x06DD)))
  pending=nil
end
local function tap(pc,fn)
  emu.addMemoryCallback(function(address,value)
    if not active() then return end
    fn()
  end,emu.callbackType.exec,pc,pc,emu.cpuType.nes,emu.memType.nesMemory)
end

tap(0x8852,on_entry) -- after the original STA $EF at $8850
-- These are mutually exclusive decision boundaries for one $8852 entry.
tap(0x884F,function() on_terminal('low_return',0x884F) end)
tap(0x8860,function() on_terminal('low_install',0x8860) end)
tap(0x885D,function() on_terminal('meta_reset',0x885D) end)
tap(0x8922,function() on_terminal('dmc_return',0x8922) end)
tap(0x8928,function() on_terminal('dmc_program',0x8928) end)

local function boundary(kind)
  if pending~=nil then fault('inflight_'..kind) end
  pending=nil
  log(string.format('JP0617_BOUNDARY %s %d',kind,next_id))
end
emu.addEventCallback(function() boundary('reset') end,emu.eventType.reset)
emu.addEventCallback(function() boundary('state_loaded') end,emu.eventType.stateLoaded)
