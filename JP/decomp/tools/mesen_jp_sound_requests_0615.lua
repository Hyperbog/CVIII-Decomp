-- JP0615: original MesenCE/Mesen2 CPU E249 executes, read-only.
-- Private original Japanese ROM session only. No audio/CPU writes.
local count=0
local limit=20000
emu.addMemoryCallback(function(addr, value)
  if count>=limit then
    if count==limit then emu.log('JP0615_TRUNCATED') end
    count=count+1
    return
  end
  local st=emu.getState()
  local cpu=st and st.cpu
  if cpu==nil or cpu.pc~=0xE249 then return end
  local s=cpu.sp
  local bank=emu.read(0x23,emu.memType.nesInternalRam)
  local lo=emu.read(0x100+((s+1)%256),emu.memType.nesInternalRam)
  local hi=emu.read(0x100+((s+2)%256),emu.memType.nesInternalRam)
  emu.log(string.format('JP0615_REQ %d E249 %02X %02X %02X %02X %02X %02X %02X %02X',
    cpu.cycleCount,cpu.a,cpu.x,cpu.y,s,cpu.status,bank,lo,hi))
  count=count+1
end,emu.callbackType.exec,0xE249,0xE249,emu.cpuType.nes,emu.memType.nesMemory)
