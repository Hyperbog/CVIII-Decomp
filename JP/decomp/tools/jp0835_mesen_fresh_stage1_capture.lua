-- JP0835: new owner-private original-JP Stage 1-02 reference capture.
-- MesenCE original Japanese ROM only. Controller inputs are intentionally
-- scripted from the previously documented JP0509 natural gameplay route.
-- Run from a fresh power-on, preferably with MesenCE --testRunner.
-- The two TSV files are PRIVATE and are not compatible with JP0718 directly.

local ROM_SHA1 = "a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f"
local info = emu.getRomInfo() or {}
assert(tostring(info.fileSha1Hash or ""):lower() == ROM_SHA1,
       "Wrong cartridge: original Japanese VRC6 ROM required")
assert(io and os, "Enable Script Window > Restrictions > Allow I/O and OS")
local folder = emu.getScriptDataFolder()
assert(type(folder) == "string" and folder ~= "", "No private script data directory")
local origin = (emu.getState() or {}).frameCount
assert(type(origin) == "number" and origin <= 2,
       "Must begin at power-on; do not start in an existing session")

local prefix = folder .. "/jp0835_" .. os.date("%Y%m%d_%H%M%S")
local input_file = assert(io.open(prefix .. "_input.tsv", "wb"))
local ram_file   = assert(io.open(prefix .. "_ram.tsv", "wb"))
input_file:write("JP0835INPUT\t1\t", ROM_SHA1, "\t", origin, "\n")
ram_file:write("JP0835RAM\t1\t", ROM_SHA1, "\t", origin, "\n")
input_file:flush(); ram_file:flush()
emu.log("JP0835 private input file: " .. prefix .. "_input.tsv")
emu.log("JP0835 private RAM file: " .. prefix .. "_ram.tsv")

local RAM = emu.memType.nesInternalRam
local CT = emu.cpuType.nes
local LAST_FRAME = 3900
local frame, polls, samples = 0, 0, 0
local last_polled = -1
local source3, source4 = 0, 0
local done = false

local function finish(why, code)
  if done then return end
  done = true
  input_file:write("END\t", why, "\t", polls, "\t", frame, "\n")
  ram_file:write("END\t", why, "\t", samples, "\t", source3,
                 "\t", source4, "\n")
  input_file:flush(); ram_file:flush()
  input_file:close(); ram_file:close()
  emu.log(string.format(
    "JP0835_END %s frames=%d polls=%d RAM=%d source3=%d source4=%d",
    why, frame, polls, samples, source3, source4))
  emu.stop(code)
end

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

local function button(mask, bit)
  return math.floor(mask / bit) % 2 == 1
end
local function buttons(mask)
  return {
    a=button(mask,128), b=button(mask,64),
    select=button(mask,32), start=button(mask,16),
    up=button(mask,8), down=button(mask,4),
    left=button(mask,2), right=button(mask,1)
  }
end

emu.addEventCallback(function(c)
  if done or (c and c ~= CT) then return end
  local value = mask_at(frame)
  emu.setInput(buttons(value), 0, 0)
  emu.setInput(buttons(0), 0, 1)
  if last_polled ~= frame then
    input_file:write(string.format("P\t%d\t%02X\t00\n", frame, value))
    last_polled = frame
    polls = polls + 1
  end
end, emu.eventType.inputPolled)

local function at(address)
  return emu.read(address, RAM)
end
local function actor_parent(slot)
  if at(0x54e + slot) ~= 0x3d then return nil end
  if math.floor(at(0x470 + slot) / 4) % 2 ~= 1 then return nil end
  local parent = at(0x645 + slot)
  if parent == 3 or parent == 4 then return parent end
  return nil
end

emu.addEventCallback(function(c)
  if done or (c and c ~= CT) then return end
  if at(0x34) == 0 and at(0x35) == 1 and at(0x36) == 0 then
    local hex = {}
    for address = 0, 2047 do
      hex[#hex + 1] = string.format("%02X", at(address))
    end
    local cycle = math.floor(emu.getCpuCycleCount(CT))
    ram_file:write(string.format("R\t%d\t%d\t%s\n",
                                frame, cycle, table.concat(hex)))
    samples = samples + 1
    for slot = 1, 12 do
      local parent = actor_parent(slot)
      if parent == 3 then source3 = source3 + 1 end
      if parent == 4 then source4 = source4 + 1 end
    end
    if samples % 120 == 0 then
      input_file:flush(); ram_file:flush()
    end
  end
  frame = frame + 1
  if frame > LAST_FRAME then
    if source3 > 0 and source4 > 0 and samples >= 2 then
      finish("COMPLETE", 0)
    else
      finish("NO_VERIFIED_STAGE1_SOURCE_ACTORS", 1)
    end
  end
end, emu.eventType.endFrame)

emu.addEventCallback(function()
  finish("STATE_LOAD_INVALIDATES_EPOCH", 1)
end, emu.eventType.stateLoaded)

emu.addEventCallback(function()
  finish("SCRIPT_INTERRUPTED", 1)
end, emu.eventType.scriptEnded)

emu.log("JP0835 started. Do not load states, reset, or change ROM.")
