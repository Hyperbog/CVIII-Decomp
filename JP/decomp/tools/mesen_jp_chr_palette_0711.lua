-- JP0711: passive, original-JP Mesen2 VRC6 CHR/palette evidence.
-- Copy the script log privately. No input, memory or PPU is changed.
local ram = emu.memType.nesInternalRam
local active, n, frame = true, 0, 0
local max_events, max_frames = 50000, 10000

local function field(state, section, key)
  if state and type(state[section]) == "table" then
    return state[section][key]
  end
  return state and state[section .. "." .. key]
end
local function status()
  local st = emu.getState()
  local cycle = field(st, "cpu", "cycleCount")
  local pc = field(st, "cpu", "pc")
  if type(cycle) ~= "number" or type(pc) ~= "number" then
    active = false
    emu.log("JP0711_FATAL missing_cpu_debug_state")
    return nil, nil
  end
  return math.floor(cycle), pc
end
local function physical(cpu)
  local m = emu.convertAddress(cpu, emu.memType.nesMemory, emu.cpuType.nes)
  if m and m.memType == emu.memType.nesPrgRom then return m.address end
  return 0xFFFFF
end
local function selected()
  return emu.read(0x34,ram), emu.read(0x35,ram), emu.read(0x36,ram),
         emu.read(0x7A0,ram), emu.read(0x19,ram)
end
local function chrmap()
  local values = {}
  for page = 0, 7 do
    local lo = emu.convertAddress(page*1024,emu.memType.nesPpuMemory,emu.cpuType.nes)
    local hi = emu.convertAddress(page*1024+1023,emu.memType.nesPpuMemory,emu.cpuType.nes)
    if lo and hi and lo.memType == emu.memType.nesChrRom and
       hi.memType == emu.memType.nesChrRom and
       lo.address >= 0 and lo.address < 131072 and
       lo.address % 1024 == 0 and hi.address == lo.address + 1023 then
      values[#values+1] = string.format("%02X",math.floor(lo.address/1024))
    else
      values[#values+1] = "--"
    end
  end
  return table.concat(values)
end
local function palette()
  local values = {}
  for i=0,31 do
    local v = emu.read(i,emu.memType.nesPaletteRam)
    if type(v) ~= "number" or v < 0 or v > 63 then
      active = false
      emu.log("JP0711_FATAL palette_read")
      return nil
    end
    values[#values+1] = string.format("%02X",v)
  end
  return table.concat(values)
end
local function write_event(addr,value)
  if not active then return end
  if n >= max_events then
    active = false
    emu.log("JP0711_TRUNCATED events")
    return
  end
  local cycle,pc = status()
  if not cycle then return end
  n=n+1
  emu.log(string.format("JP0711_EVENT %d %d %.0f %04X %05X %04X %02X",
    n,frame,cycle,pc,physical(pc),addr,value))
end
for _,range in ipairs({{0x2000,0x2007},{0xB003,0xB003},
                         {0xD000,0xD003},{0xE000,0xE003}}) do
  emu.addMemoryCallback(write_event,emu.callbackType.write,
    range[1],range[2],emu.cpuType.nes,emu.memType.nesMemory)
end
emu.addEventCallback(function(cpu)
  if not active or (cpu and cpu~=emu.cpuType.nes) then return end
  if frame>=max_frames then
    active=false
    emu.log("JP0711_TRUNCATED frames")
    return
  end
  local cycle = status()
  if not cycle then return end
  local pixels=palette()
  if not pixels then return end
  local a,b,c,d,e = selected()
  emu.log(string.format("JP0711_FRAME %d %.0f %s %s %02X %02X %02X %02X %02X",
      frame,cycle,chrmap(),pixels,a,b,c,d,e))
  frame=frame+1
end,emu.eventType.endFrame)
for _,kind in ipairs({{"JP0711_STATE_LOADED",emu.eventType.stateLoaded},
                        {"JP0711_RESET",emu.eventType.reset}}) do
  emu.addEventCallback(function()
    active=false
    emu.log(kind[1])
  end,kind[2])
end
emu.addEventCallback(function()
  emu.log(string.format("JP0711_END %d %d",n,frame))
end,emu.eventType.scriptEnded)
local info=emu.getRomInfo()
local sha=tostring(info and info.fileSha1Hash or ""):lower()
emu.log("JP0711_BEGIN 1 "..sha)
