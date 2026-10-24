-- JP0740 original-Japanese MesenCE, read-only CPU write provenance.
-- Requires env JP0740_INPUT_TSV, JP0740_ANCHORS_TSV, JP0740_TRACE_TSV.
-- Input is the PRIVATE owner JP0718 original -input.tsv (not generated content).
-- The trace is rejected unless original archived Mesen states reproduce.
local SHA='a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
local ct,cm,ram=emu.cpuType.nes,emu.memType.nesMemory,emu.memType.nesInternalRam
assert(tostring((emu.getRomInfo() or {}).fileSha1Hash or ''):lower()==SHA,
       'JP0740 wrong original Japanese ROM')
assert(io and io.open and os and os.getenv,'Mesen I/O access must be enabled')
local function env(key)
  local v=os.getenv(key)
  assert(type(v)=='string' and v~='',key..' required')
  return v
end
local inputs,anchors={},{}
local f=assert(io.open(env('JP0740_INPUT_TSV'),'rb'))
local header=assert(f:read('*l'))
assert(header:find('^JP0718INPUT\t1\t'..SHA..'\t'),'wrong input archive')
local previous,n,last=-1,0,false
for line in f:lines() do
  if line:sub(1,2)=='P\t' then
    local frame,lframe,seq,p1,p2,cycle=line:match(
      '^P\t(%d+)\t(%d+)\t(%d+)\t(%x%x)\t(%x%x)\t(%d+)$')
    assert(frame and p1 and p2,'malformed original input')
    frame=tonumber(frame)
    assert(frame>previous,'nonmonotone source input frames')
    previous=frame
    inputs[frame]={tonumber(p1,16),tonumber(p2,16)}
    n=n+1
  else
    local total=line:match('^END\tUSER_STOP\t(%d+)$')
    assert(total and tonumber(total)==n,'bad original input footer')
    last=true
  end
end
f:close()
assert(last and n==17562 and previous==17563,'incomplete JP0718 original input')
local WATCH={0x62,0x53,0x54,0x55,0x63,0x6B,0x41C,0x438,
             0x4C4,0x4F2,0x509,0x520,0x565,0x5C1}
f=assert(io.open(env('JP0740_ANCHORS_TSV'),'rb'))
assert(f:read('*l')=='JP0740_ANCHORS\t1','invalid reference anchors')
local anchor_n=0
for line in f:lines() do
  local frame,cycles,hex=line:match('^(%d+)\t(%d+)\t([0-9A-F]+)$')
  assert(frame and #hex==2*#WATCH,'bad anchor byte format')
  anchors[tonumber(frame)]={cycle=tonumber(cycles),state=hex}
  anchor_n=anchor_n+1
end
f:close()
assert(anchor_n>=3 and anchors[9440] and anchors[9504] and anchors[9576],
       'missing owner Mesen 9440/9504/9576 anchors')
local out=assert(io.open(env('JP0740_TRACE_TSV'),'wb'))
out:write('JP0740\t1\t',SHA,'\t',n,'\n')
out:flush()
local BEGIN,FINISH,LIMIT=9370,9600,150000
local active,count,observed,checked=true,0,0,0
local pc,phys,pcframe=0xFFFF,0xFFFFF,-1
-- JP0718 local snapshot frames begin at zero; Mesen frameCount is
-- absolute and the archived input header has origin=1. Never conflate them.
local local_frame=0
local function framecount() return local_frame end
local function absolute_frame()
  local v=(emu.getState() or {}).frameCount
  assert(type(v)=='number' and v==math.floor(v),'missing Mesen absolute frame')
  return v
end
local function cycle() return math.floor(emu.getCpuCycleCount(ct) or -1) end
local function source(at)
  local m=emu.convertAddress(at,cm,ct)
  if m and m.memType==emu.memType.nesPrgRom and
     type(m.address)=='number' then return m.address end
  return 0xFFFFF
end
local function finish(reason)
  if not active then return end
  active=false
  out:write('END\t',reason,'\t',count,'\t',observed,'\t',checked,'\n')
  out:flush();out:close()
  emu.log('JP0740_END '..reason)
  -- MesenCE CLI headless TestRunner exits only when the guest Lua script
  -- invokes emu.stop; emu.exit is not implemented in the current core.
  emu.stop(reason=='COMPLETE' and 0 or 1)
end
local function buttons(mask)
  local names={'a','b','select','start','up','down','left','right'}
  local b={}
  for i,name in ipairs(names) do
    local bit=2^(8-i)
    b[name]=(math.floor(mask/bit)%2==1)
  end
  return b
end
emu.addEventCallback(function(c)
  if not active or (c and c~=ct) then return end
  local fr=absolute_frame()
  if fr~=local_frame+1 then finish('FRAME_EPOCH_MISMATCH');return end
  if local_frame>FINISH then return end
  local v=inputs[fr]
  if not v then finish('INPUT_FRAME_MISSING');return end
  -- This requests identical button intent, NOT verified $4016 bus phase.
  emu.setInput(buttons(v[1]),0)
  emu.setInput(buttons(v[2]),1)
  observed=observed+1
end,emu.eventType.inputPolled)
-- Record executing PC, rather than assuming write-callback PC is opcode PC.
emu.addMemoryCallback(function(at)
  if not active then return end
  local fr=framecount()
  if fr<BEGIN or fr>FINISH then return end
  pc=at
  phys=source(at)
  pcframe=fr
end,emu.callbackType.exec,0x0000,0xFFFF,ct,cm)
for _,addr in ipairs(WATCH) do
  for mirror=0,3 do
    local bus=addr+0x800*mirror
    emu.addMemoryCallback(function(at,v)
      if not active then return end
      local fr=framecount()
      if fr<BEGIN or fr>FINISH then return end
      count=count+1
      if count>LIMIT then finish('EVENT_LIMIT');return end
      local old=emu.read(addr,ram)
      local codepc=(pcframe==fr and pc) or 0xFFFF
      local codephys=(pcframe==fr and phys) or 0xFFFFF
      out:write(string.format(
        'W\t%d\t%d\t%d\t%04X\t%02X\t%02X\t%04X\t%04X\t%05X\n',
        count,fr,cycle(),addr,old,v,bus,codepc,codephys))
    end,emu.callbackType.write,bus,bus,ct,cm)
  end
end
-- Controller latch is a CPU write, not an inputPolled event. Capture it
-- with bus/address provenance, but do NOT read the write-only latch for "old".
emu.addMemoryCallback(function(_,v)
  if not active then return end
  local fr=framecount()
  if fr<BEGIN or fr>FINISH then return end
  count=count+1
  if count>LIMIT then finish('EVENT_LIMIT');return end
  local codepc=(pcframe==fr and pc) or 0xFFFF
  local codephys=(pcframe==fr and phys) or 0xFFFFF
  out:write(string.format(
    'W\t%d\t%d\t%d\t4016\tFF\t%02X\t4016\t%04X\t%05X\n',
      count,fr,cycle(),v,codepc,codephys))
end,emu.callbackType.write,0x4016,0x4016,ct,cm)
for _,addr in ipairs({0x4016,0x4017}) do
  emu.addMemoryCallback(function(a,v)
    if not active then return end
    local fr=framecount()
    if fr<BEGIN or fr>FINISH then return end
    count=count+1
    if count>LIMIT then finish('EVENT_LIMIT');return end
    local codepc=(pcframe==fr and pc) or 0xFFFF
    local codephys=(pcframe==fr and phys) or 0xFFFFF
    out:write(string.format('R\t%d\t%d\t%d\t%04X\t%02X\t%04X\t%05X\n',
              count,fr,cycle(),addr,v,codepc,codephys))
  end,emu.callbackType.read,addr,addr,ct,cm)
end
local function snap()
  local t={}
  for _,addr in ipairs(WATCH) do
    t[#t+1]=string.format('%02X',emu.read(addr,ram))
  end
  return table.concat(t)
end
emu.addEventCallback(function(c)
  if not active or (c and c~=ct) then return end
  local fr=framecount()
  local anchor=anchors[fr]
  if anchor then
    local actual=snap()
    if actual~=anchor.state or cycle()~=anchor.cycle then
      out:write(string.format('ANCHOR_FAIL\t%d\t%d\t%d\t%s\t%s\n',
           fr,cycle(),anchor.cycle,actual,anchor.state))
      finish('ANCHOR_MISMATCH');return
    end
    checked=checked+1
    out:write('ANCHOR_OK\t',fr,'\t',cycle(),'\n')
  end
  if fr>=FINISH then
    if checked<3 then finish('ANCHORS_MISSING')
    else finish('COMPLETE') end
  end
  local_frame=local_frame+1
end,emu.eventType.endFrame)
emu.addEventCallback(function() finish('ABORT_STATE_LOAD') end,emu.eventType.stateLoaded)
emu.addEventCallback(function() finish('SCRIPT_ENDED') end,emu.eventType.scriptEnded)
emu.log('JP0740_STARTED: read-only watched writes; input from original owner archive')
