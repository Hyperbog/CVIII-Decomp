-- Original-JP unmodified-ROM Mesen2 Windows headless provenance replay.
-- Target: verified input schedule, 1100 continuous emulator frames.
-- Only controller setInput is changed; never write ROM/RAM/CPU state.
-- Log is named CV0551, intentionally distinct from Linux mesen-agent CV0549.
local frame = 0
local count = 0
local limit = 25000
local truncated = false
local mem = emu.memType.nesInternalRam
local mapShadow = -1
local function rd(a) return emu.read(a, mem) end
local function out(msg)
  count = count + 1
  if count <= limit then emu.log('CV0551 ' .. msg)
  elseif not truncated then
    emu.log('CV0551 kind=truncated frame=' .. frame)
    truncated = true
  end
end
local function physical(a)
  local ok, result = pcall(emu.convertAddress, a, emu.memType.nesMemory)
  if ok and type(result)=='table' and result.memType == emu.memType.nesPrgRom
     and type(result.address)=='number' and result.address >= 0
     and result.address < 0x40000 then
    return string.format('%06X', result.address)
  end
  return 'UNKNOWN'
end
local function pc()
  local ok, state = pcall(emu.getState)
  if ok and type(state)=='table' and type(state.cpu)=='table'
     and type(state.cpu.pc)=='number' then return state.cpu.pc end
  return 0xffff
end
local function at(a,b,e) return frame+1>=a and frame+1<=e end
local function buttons()
  -- Frame numbers are relative to one cold boot, not independent savestates.
  -- These match the three original 0508 input schedules after adding offsets.
  return {
    start = at(90,92) or at(180,182) or at(300,302) or at(530,531) or at(745,746),
    right = at(370,520) or at(645,730) or at(830,1065),
    a = at(460,469) or at(1010,1012),
    b = at(470,475) or at(650,652) or at(870,872),
    select = false, up = false, down = false, left = false
  }
end
emu.addEventCallback(function()
  emu.setInput(buttons(), 0)
end, emu.eventType.inputPolled)
emu.addMemoryCallback(function(addr,val)
  out(string.format('kind=write18 frame=%d addr=0018 old=%02X value=%02X pc=%04X shadow=%02X',
      frame, rd(0x18), val, pc() & 0xffff, mapShadow & 0xff))
end, emu.callbackType.write, 0x0018)
emu.addMemoryCallback(function(addr,val)
  mapShadow = val
end, emu.callbackType.write, 0x8000)
for _, a in ipairs({0xE35C,0xE526,0xB873,0xB7F7}) do
  emu.addMemoryCallback(function(addr,val)
    out(string.format('kind=exec frame=%d pc=%04X state=%02X sub=%02X guard=%02X shadow=%02X phys=%s',
        frame, addr, rd(0x18), rd(0x19), rd(0x1c), mapShadow & 0xff, physical(addr)))
  end, emu.callbackType.exec, a)
end
emu.addEventCallback(function()
  frame = frame+1
  out(string.format('kind=frame frame=%d state=%02X sub=%02X guard=%02X room=%02X slot=%02X shadow=%02X',
       frame, rd(0x18), rd(0x19), rd(0x1c), rd(0x68), rd(0x7a6), mapShadow & 0xff))
  if frame == 1100 then
    out(string.format('kind=complete frames=1100 truncated=%d', truncated and 1 or 0))
    emu.exit(0)
  end
end, emu.eventType.endFrame)
out('kind=ready schema=jp-mesen-windows-native-0551 passive=1 input_only=1 frames=1100')
