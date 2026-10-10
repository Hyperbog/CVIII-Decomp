local f=0
local prior=''
emu.addEventCallback(function()
  f=f+1
  local a=emu.read(0x18,emu.memType.nesInternalRam)
  local b=emu.read(0x19,emu.memType.nesInternalRam)
  local c=emu.read(0x68,emu.memType.nesInternalRam)
  local d=emu.read(0x2C,emu.memType.nesInternalRam)
  local e=emu.read(0x7A0,emu.memType.nesInternalRam)
  local g=emu.read(0x7A6,emu.memType.nesInternalRam)
  local state=string.format('%02X %02X %02X %02X %02X %02X',a,b,c,d,e,g)
  if state~=prior or f%120==0 then
    emu.log(string.format('STATE frame=%d s=%s',f,state))
    prior=state
  end
end,emu.eventType.endFrame)
