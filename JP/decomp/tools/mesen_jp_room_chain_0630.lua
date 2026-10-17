-- JP0630: read-only, physically qualified original-JP selector chain capture.
-- Requires retail JP Mapper24 ROM; authenticate log with the Python validator.
-- P=producer entry, T=producer STA instruction, R=RAM $30 write,
-- W=RAM $07A0 write, C=consumer entry, S=consumer pointer postcondition,
-- N/I=interrupt entry. Runtime entry alone does not establish causal parity.
local ram=emu.memType.nesInternalRam
local active=true
local count=0
local limit=100000
local function r(a) return emu.read(a,ram) end
local function mapped(pc)
  local t=emu.convertAddress(pc,emu.memType.nesMemory,emu.cpuType.nes)
  if t and t.memType==emu.memType.nesPrgRom then return t.address end
  return 0xFFFFF
end
local function emit(kind,pc,physical,value,aux)
  if not active then return end
  if count>=limit then
    active=false
    emu.log('JP0630_TRUNCATED')
    return
  end
  local st=emu.getState()
  local cycle=st and st.cpu and st.cpu.cycleCount or -1
  count=count+1
  emu.log(string.format('JP0630_EVT %d %s %04X %05X %02X %02X %04X %d',
       count,kind,pc,physical,r(0x23),value,aux,cycle))
end
local function exec(pc,physical,kind,read)
  emu.addMemoryCallback(function()
    if mapped(pc)~=physical then return end
    local v,a=read()
    emit(kind,pc,physical,v,a)
  end,emu.callbackType.exec,pc,pc,emu.cpuType.nes,emu.memType.nesMemory)
end
exec(0xBB57,0x07B57,'P',function() return r(0x30),r(0x7A0) end)
exec(0xBB5E,0x07B5E,'T',function()
  local st=emu.getState()
  return (st and st.cpu and st.cpu.a or 0),r(0x30)
end)
exec(0xB7F7,0x2B7F7,'C',function()
  local sel=r(0x7A0)
  local ptr=0xB8C2+((sel*2)%256)
  if mapped(ptr)~=0x28000+ptr-0x8000 or
     mapped(ptr+1)~=0x28000+ptr+1-0x8000 then
    active=false
    emu.log('JP0630_MAPPING_ERROR')
    return sel,0
  end
  local lo=emu.read(ptr,emu.memType.nesDebug)
  local hi=emu.read(ptr+1,emu.memType.nesDebug)
  return sel,lo+hi*256
end)
exec(0xB806,0x2B806,'S',function()
  return r(0x7A0),r(0x08)+256*r(0x09)
end)
local function writes(addr,kind,old_address)
  emu.addMemoryCallback(function(_,value)
    local st=emu.getState()
    local pc=st and st.cpu and st.cpu.pc or 0xFFFF
    emit(kind,pc,mapped(pc),value,r(old_address))
  end,emu.callbackType.write,addr,addr,emu.cpuType.nes,emu.memType.nesMemory)
end
for mirror=0,3 do
  writes(0x0030+mirror*0x0800,'R',0x30)
  writes(0x07A0+mirror*0x0800,'W',0x7A0)
end
for _,entry in ipairs({{'N',emu.eventType.nmi},{'I',emu.eventType.irq}}) do
  local kind,event=entry[1],entry[2]
  emu.addEventCallback(function(cpu)
    if cpu~=emu.cpuType.nes then return end
    local st=emu.getState()
    local pc=st and st.cpu and st.cpu.pc or 0xFFFF
    emit(kind,pc,mapped(pc),0,0)
  end,event)
end
emu.addEventCallback(function()
  active=false
  emu.log('JP0630_RESET')
end,emu.eventType.reset)
emu.addEventCallback(function()
  active=false
  emu.log('JP0630_STATE_LOADED')
end,emu.eventType.stateLoaded)
emu.addEventCallback(function()
  emu.log('JP0630_END '..count)
end,emu.eventType.scriptEnded)
emu.log('JP0630_BEGIN 1')
