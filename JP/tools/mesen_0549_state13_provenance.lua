-- Passive original-JP Mesen2 instrumentation. NEVER modifies RAM, ROM or PC.
-- Compatible with emu.addMemoryCallback and endFrame from Mesen2 Lua API.
-- CV0549 events are machine-parseable; all logged game-state writes are PRE-WRITE.
local frame, eventCount, limit, dropped = 0, 0, 25000, false
local mapRegister = -1                 -- register shadow, NOT inferred physical bank
local mem = emu.memType.nesInternalRam
local function read(addr) return emu.read(addr, mem) end
local function cpuPC()
  local ok, state = pcall(emu.getState)
  if ok and type(state) == 'table' and type(state.cpu) == 'table' and type(state.cpu.pc) == 'number' then
    return state.cpu.pc
  end
  return -1  -- absence of PC provenance is explicit, never fabricated
end
local function logEvent(s)
  eventCount = eventCount + 1
  if eventCount <= limit then emu.log('CV0549 ' .. s)
  elseif not dropped then emu.log('CV0549 kind=truncated limit=' .. limit); dropped = true end
end
local function onStateWrite(addr, value)
  local prior = read(0x18)
  logEvent(string.format('kind=write18 frame=%d addr=0018 old=%02X value=%02X pc=%04X shadow=%02X',
    frame, prior, value, cpuPC() & 0xffff, mapRegister & 0xff))
  -- No integer return: callback must not alter the original CPU write.
end
local function onMapperWrite(addr, value)
  mapRegister = value
  -- Shadow is auxiliary only. Bank-qualified execution uses convertAddress().
end
local function physicalAddress(address)
  -- Mesen2 resolves the currently mapped physical ROM byte. A CPU PC alone
  -- does NOT identify banked code. Failure must stay unknown, not guessed.
  local ok, mapping = pcall(emu.convertAddress, address, emu.memType.nesMemory)
  if ok and type(mapping) == 'table' and
     mapping.memType == emu.memType.nesPrgRom and
     type(mapping.address) == 'number' and
     mapping.address >= 0 and mapping.address < 0x40000 then
    return string.format('%06X', mapping.address)
  end
  return 'UNKNOWN'
end
local function observeEntry(address, value)
  local selector = read(0x18)
  local substate = read(0x19)
  local guard = read(0x1c)
  logEvent(string.format('kind=exec frame=%d pc=%04X state=%02X sub=%02X guard=%02X shadow=%02X phys=%s',
    frame, address, selector, substate, guard, mapRegister & 0xff, physicalAddress(address)))
end
local function onFrame()
  frame = frame + 1
  logEvent(string.format('kind=frame frame=%d state=%02X sub=%02X guard=%02X room=%02X slot=%02X shadow=%02X',
    frame, read(0x18), read(0x19), read(0x1c), read(0x68), read(0x7a6), mapRegister & 0xff))
end
emu.addMemoryCallback(onStateWrite, emu.callbackType.write, 0x0018)
emu.addMemoryCallback(onMapperWrite, emu.callbackType.write, 0x8000)
for _, addr in ipairs({0xE35C, 0xE526, 0xB873, 0xB7F7}) do
  emu.addMemoryCallback(observeEntry, emu.callbackType.exec, addr)
end
emu.addEventCallback(onFrame, emu.eventType.endFrame)
emu.log('CV0549 kind=ready schema=jp-state13-provenance-v2 passive=1')
