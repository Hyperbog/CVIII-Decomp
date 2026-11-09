-- JP0841: owner-private, bounded MesenCE original-JP A-button first-cause trace.
-- ROM / controller intentions identical to JP0835; never modify CPU/PPU/mapper RAM.
-- Captures actual $4016/$4017 reads, strobe writes and RAM-input/vertical-Y writers.
-- Power on original Japanese ROM and run with MesenCE --testRunner + I/O access.
-- New, independent recording: do not substitute this for JP0835 RAM archives.
local SHA1 = "a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f"
local CT, MEM, RAM = emu.cpuType.nes, emu.memType.nesMemory, emu.memType.nesInternalRam
assert(tostring((emu.getRomInfo() or {}).fileSha1Hash or ""):lower() == SHA1,
       "JP0841 requires the exact original Japanese mapper24 ROM")
local origin = (emu.getState() or {}).frameCount
assert(type(origin) == "number" and origin <= 2, "JP0841 must start at power-on")
assert(io and os and io.open and os.date, "Enable MesenCE script I/O and OS access")
local folder = emu.getScriptDataFolder()
assert(type(folder) == "string" and folder ~= "", "Private MesenCE data folder unavailable")
local path = folder .. "/jp0841_" .. os.date("%Y%m%d_%H%M%S") .. "_bus.tsv"
local file = assert(io.open(path, "wb"))
local FIRST, LAST, STOP, MAX_RECORDS = 3506, 3519, 3520, 12000
local frame, seq, polls, actual_bus_reads, done = 0, 0, 0, 0, false
file:write(string.format("JP0841\t1\t%s\t%d\t%d\t%d\n", SHA1, origin, FIRST, LAST))
file:flush()

local function mask_at(f)
  -- JP0509 controller-only phase 0: initial menu -> first stage.
  if f < 1502 then
    local start = (f >= 50 and f <= 54) or
                  (f >= 170 and f <= 174) or
                  (f >= 270 and f <= 274) or
                  (f >= 370 and f <= 374)
    local mask = start and 16 or 0
    if f >= 780 then mask = mask + 1 end   -- RIGHT
    if f >= 820 then mask = mask + 128 end -- A
    return mask
  end
  if f < 2602 then return 129 end         -- RIGHT + A
  -- JP0509 phase 2: original source phases 3/4 were reached near 3092.
  local tick = f - 2602
  local mask = 1                           -- RIGHT
  if tick % 43 >= 4 and tick % 43 <= 9 then mask = mask + 128 end
  if tick % 107 >= 34 and tick % 107 <= 65 then mask = mask + 8 end
  return mask
end


local function bit(mask, flag)
  return math.floor(mask / flag) % 2 == 1
end
local function buttons(mask)
  return { a=bit(mask,128), b=bit(mask,64), select=bit(mask,32),
           start=bit(mask,16), up=bit(mask,8), down=bit(mask,4),
           left=bit(mask,2), right=bit(mask,1) }
end
local function at(addr)
  return emu.read(addr, RAM)
end
local function cycle()
  return math.floor(emu.getCpuCycleCount(CT))
end
local function cpu_pc()
  local state = (emu.getState() or {}).cpu or {}
  return type(state.pc) == "number" and state.pc or 0xFFFF
end
local function record(kind, addr, value)
  if done or frame < FIRST or frame > LAST then return end
  seq = seq + 1
  if seq > MAX_RECORDS then error("JP0841 bounded event limit exceeded") end
  file:write(string.format("%s\t%d\t%d\t%04X\t%04X\t%02X\t%02X\t%02X\t%02X\n",
    kind, frame, cycle(), cpu_pc(), addr, value or 0,
    at(0x28), at(0x2a), at(0x41c)))
end
local function finish(why, exit_code)
  if done then return end
  -- Do not set `done` before writing the complete footer.
  file:write(string.format("END\t%s\t%d\t%d\t%d\n",
    why, frame, polls, actual_bus_reads))
  file:flush(); file:close(); done = true
  emu.log("JP0841 " .. why .. " private log " .. path)
  emu.stop(exit_code)
end

-- Original JP0835 input callbacks copied verbatim in behavior; P events are
-- INPUT REFRESH EVENTS, not evidence of CPU $4016 reads.
emu.addEventCallback(function(cpu)
  if done or (cpu and cpu ~= CT) then return end
  local intent = mask_at(frame)
  emu.setInput(buttons(intent), 0, 0)
  emu.setInput(buttons(0), 0, 1)
  polls = polls + 1
  record("P", 0xFFFF, intent)
end, emu.eventType.inputPolled)

-- Actual CPU memory-access callbacks.  `read` fires AFTER the CPU read;
-- `write` fires BEFORE the CPU write. Return nothing: observer only.
emu.addMemoryCallback(function(addr, value)
  if frame >= FIRST and frame <= LAST then actual_bus_reads = actual_bus_reads + 1 end
  record("R", addr, value)
end, emu.callbackType.read, 0x4016, 0x4017, CT, MEM)
emu.addMemoryCallback(function(addr, value)
  record("S", addr, value)
end, emu.callbackType.write, 0x4016, 0x4016, CT, MEM)
for _, addr in ipairs({0x0028, 0x002A, 0x041C, 0x04DB, 0x0520, 0x0537}) do
  emu.addMemoryCallback(function(address, value)
    record("W", address, value)
  end, emu.callbackType.write, addr, addr, CT, MEM)
end

emu.addEventCallback(function(cpu)
  if done or (cpu and cpu ~= CT) then return end
  if frame >= FIRST and frame <= LAST then
    -- E markers are sampled at the same PPU boundary as JP0835.
    record("E", 0xFFFF, at(0x04db))
    file:write(string.format("V\t%d\t%d\t%02X\t%02X\t%02X\t%02X\t%02X\n",
      frame, cycle(), at(0x28), at(0x2a), at(0x41c), at(0x04db), at(0x0520)))
    file:flush()
  end
  frame = frame + 1
  if frame > STOP then finish("COMPLETE", 0) end
end, emu.eventType.endFrame)
emu.addEventCallback(function() finish("INVALID_STATE_LOAD", 1) end, emu.eventType.stateLoaded)
emu.addEventCallback(function() finish("INTERRUPTED", 1) end, emu.eventType.scriptEnded)
emu.log("JP0841 began original Japanese controller/bus verification: " .. path)