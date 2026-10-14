-- JP0616: ORIGINAL Mesen2 sound dispatch branch witnesses.
-- Read-only, owner-local; this script does not change the original ROM.
-- These callbacks are meaningful only when fixed E249 is in its $0C bank.
local ram=emu.memType.nesInternalRam
local n=0
local MAX=20000
local active_low=false
local active_dmc=false

local function read(a) return emu.read(a,ram) end
local function guard()
  return read(0x23)==0x0C and read(0x26)==0xFF
end
local function emit(kind,pc,cmd,prior,state)
  if n>=MAX then
    if n==MAX then emu.log('JP0616_TRUNCATED') end
    n=n+1
    return
  end
  emu.log(string.format('JP0616_GATE %s %04X %02X %02X %02X',
    kind,pc,cmd,prior,state))
  n=n+1
end
local function tap(pc,func)
  emu.addMemoryCallback(function(addr,value)
    if guard() then func() end
  end,emu.callbackType.exec,pc,pc,emu.cpuType.nes,emu.memType.nesMemory)
end

tap(0x8842,function()
  active_low=true
  emit('low_enter',0x8842,read(0xEF),0,read(0x0109))
end)
tap(0x884F,function()
  if active_low then
    emit('low_return',0x884F,read(0xEF),0,read(0x0109))
    active_low=false
  end
end)
tap(0x8860,function()
  if active_low then
    emit('low_install',0x8860,read(0xEF),0,read(0x0109))
    active_low=false
  end
end)
tap(0x8908,function()
  active_dmc=true
  local cpu=emu.getState().cpu
  emit('dmc_enter',0x8908,cpu.a,read(0x019E),read(0x06DD))
end)
tap(0x8922,function()
  if active_dmc then
    emit('dmc_return',0x8922,read(0xEF),read(0x019E),read(0x06DD))
    active_dmc=false
  end
end)
tap(0x8928,function()
  if active_dmc then
    emit('dmc_install',0x8928,read(0xEF),read(0x019E),read(0x06DD))
    active_dmc=false
  end
end)
