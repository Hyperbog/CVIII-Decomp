-- JP0629: read-only Mesen2 original-JP room-selector provenance.
-- Events: P=raw01:$BB57 entry; W=any NES RAM $07A0 write;
-- C=raw0A:$B7F7 entry. All captures preserve physical PRG identity.
-- Mesen CPU memory write callback reports NEW value BEFORE RAM mutation.
local ram=emu.memType.nesInternalRam
local n=0
local max_events=50000
local enabled=true
local function r(a) return emu.read(a,ram) end
local function phys(cpu_pc)
  local map=emu.convertAddress(cpu_pc,emu.memType.nesMemory,emu.cpuType.nes)
  if map and map.memType==emu.memType.nesPrgRom then return map.address end
  return 0xFFFFF
end
local function emit(kind,pc,bank,offset,value,aux)
  if not enabled then return end
  if n>=max_events then
    enabled=false
    emu.log('JP0629_TRUNCATED')
    return
  end
  local st=emu.getState()
  local cycles=st and st.cpu and st.cpu.cycleCount or -1
  n=n+1
  emu.log(string.format('JP0629_EVT %d %s %04X %05X %02X %02X %04X %d',
                       n,kind,pc,offset,bank,value,aux,cycles))
end
local function watch_exec(pc,expected,kind)
  emu.addMemoryCallback(function(addr,value)
    local pos=phys(pc)
    if pos~=expected then return end
    local bank=r(0x23)
    if kind=='P' then
      emit('P',pc,bank,pos,r(0x30),r(0x7A0))
    else
      local sel=r(0x7A0)
      local idx=(sel*2)%256
      local addr=0xB8C2+idx
      if phys(addr)~=(0x28000+addr-0x8000)
         or phys(addr+1)~=(0x28000+addr+1-0x8000) then
        emu.log('JP0629_MAPPING_ERROR pointer_table_not_raw0A')
        enabled=false
        return
      end
      local lo=emu.read(addr,emu.memType.nesDebug)
      local hi=emu.read(addr+1,emu.memType.nesDebug)
      emit('C',pc,bank,pos,sel,lo+hi*256)
    end
  end,emu.callbackType.exec,pc,pc,emu.cpuType.nes,emu.memType.nesMemory)
end
watch_exec(0xBB57,0x7B57,'P')
watch_exec(0xB7F7,0x2B7F7,'C')

local function watch_write(addr,value)
  local state=emu.getState()
  local pc=state and state.cpu and state.cpu.pc or 0xFFFF
  -- 'value' is pending new RAM byte. 'aux' is the old byte.
  emit('W',pc,r(0x23),phys(pc),value,r(0x7A0))
end
for mirror=0,3 do
  local addr=0x07A0+mirror*0x0800
  emu.addMemoryCallback(watch_write,emu.callbackType.write,addr,addr,
                        emu.cpuType.nes,emu.memType.nesMemory)
end
emu.addEventCallback(function()
  enabled=false
  emu.log('JP0629_STATE_LOADED')
end,emu.eventType.stateLoaded)
emu.addEventCallback(function()
  emu.log('JP0629_END '..n)
end,emu.eventType.scriptEnded)
emu.log('JP0629_BEGIN 1')
