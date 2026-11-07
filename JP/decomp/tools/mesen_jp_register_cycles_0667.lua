-- JP0667 original Japanese ROM observer: live 2A03/VRC6 write callbacks.
-- Intended for independently verified MesenCE/Mesen2 build, read-only.
-- Original gameplay inputs and Mesen build must be recorded privately.
-- This is a CAPTURE SCRIPT, not proof of emulator execution by itself.
local next_seq = 0
local logged = 0
local cap = 200000
local stopped = false
local function log(msg)
  if logged >= cap then
    if not stopped then emu.log('JP0667_TRUNCATED'); stopped = true end
    return
  end
  logged = logged + 1
  emu.log(msg)
end
local function tap(start_addr, end_addr)
  emu.addMemoryCallback(function(address, value)
    if stopped then return end
    local st = emu.getState()
    local cpu = st and st.cpu
    local cyc = cpu and cpu.cycleCount
    if type(cyc) ~= 'number' or cyc < 0 or cyc ~= math.floor(cyc) then
      log('JP0667_INVALID cycle_unavailable')
      stopped = true
      return
    end
    next_seq=next_seq+1
    log(string.format('JP0667_WRITE %d %.0f %04X %02X',
                      next_seq,cyc,address,value))
  end,emu.callbackType.write,start_addr,end_addr,emu.cpuType.nes,emu.memType.nesMemory)
end
-- The original native trace observes these CPU register write intents.
tap(0x4000,0x4013)
tap(0x4015,0x4015)
tap(0x4017,0x4017)
tap(0x9000,0x9003)
tap(0xA000,0xA002)
tap(0xB000,0xB002)
local function boundary(name)
   if stopped then return end
   log('JP0667_BOUNDARY '..name)
end
emu.addEventCallback(function() boundary('reset') end,emu.eventType.reset)
emu.addEventCallback(function() boundary('state_loaded') end,emu.eventType.stateLoaded)
