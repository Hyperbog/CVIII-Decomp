-- JP0740: authenticated original Japanese MesenCE write/read provenance.
-- Replays existing JP0718 controller inputs; NO guest-RAM, ROM or PPU writes.
-- Requires JP0740_INPUT_TSV, JP0740_ANCHORS_TSV, JP0740_TRACE_TSV paths
-- and Mesen script host I/O permission. Output is owner-PRIVATE.
-- Original captured RAM snapshots are local-frame zero-based; input polls
-- use absolute frameCount with origin=1. Do not merge these domains.
local ct,mem,ram=emu.cpuType.nes,emu.memType.nesMemory,emu.memType.nesInternalRam
local SHA1='a0f3b31d4e3b0d2ca2e8a34f91f14ad99a5ad11f'
assert(tostring((emu.getRomInfo() or {}).fileSha1Hash or ''):lower()==SHA1,
       'JP0740 original Japanese ROM SHA1 mismatch')
assert(io and io.open and os and os.getenv,'JP0740 host I/O must be enabled')
local f=assert(io.open(assert(os.getenv('JP0740_INPUT_TSV')),'rb'))
local header=assert(f:read('*l'))
assert(header:match('^JP0718INPUT\t1\t([0-9a-fA-F]+)\t'):lower()==SHA1,
       'JP0740 wrong original input header')
local epoch=tonumber(header:match('\t(%d+)$'))
assert(epoch==1,'JP0740 original title-start epoch mismatch')
local inputs,prev,n={},1,0
for line in f:lines() do
  if line:sub(1,2)=='P\t' then
    local af,lf,seq,a,b,cyc=line:match(
       '^P\t(%d+)\t(%d+)\t(%d+)\t(%x%x)\t(%x%x)\t(%d+)$')
    assert(af and tonumber(af)==prev+1 and tonumber(lf)==n+1 and
           tonumber(seq)==n+1,'JP0740 input chronology')
    prev=tonumber(af);n=n+1
    inputs[prev]={tonumber(a,16),tonumber(b,16)}
  else
    assert(line=='END\tUSER_STOP\t17562','JP0740 input footer mismatch')
  end
end
f:close()
assert(n==17562 and prev==17563,'JP0740 original input count mismatch')
local watch={0x62,0x53,0x54,0x55,0x63,0x6B,
             0x41C,0x438,0x4C4,0x4F2,0x509,0x520,0x565,0x5C1}
local anchors={}
local af=assert(io.open(assert(os.getenv('JP0740_ANCHORS_TSV')),'rb'))
assert(af:read('*l')=='JP0740_ANCHORS\t1','JP0740 anchor version')
local anchor_count=0
for line in af:lines() do
  local k,cyc,hex=line:match('^(%d+)\t(%d+)\t([0-9A-F]+)$')
  assert(k and #hex==#watch*2,'JP0740 invalid anchor row')
  anchors[tonumber(k)]={tonumber(cyc),hex}
  anchor_count=anchor_count+1
end
af:close()
assert(anchor_count==4 and anchors[9376] and anchors[9440]
       and anchors[9504] and anchors[9576], 'JP0740 missing four anchors')
local out=assert(io.open(assert(os.getenv('JP0740_TRACE_TSV')),'wb'))
out:write('JP0740\t1\t',SHA1,'\t17562\n');out:flush()
local begin_frame,stop_frame=9350,9600
local frame,count,polls,checked,alive=0,0,0,0,true
local lastpc,lastphys,lastframe=0xFFFF,0xFFFFF,-1
local function cycle() return math.floor(emu.getCpuCycleCount(ct) or -1) end
local function phys(pc)
  local map=emu.convertAddress(pc,mem,ct)
  if map and map.memType==emu.memType.nesPrgRom and
     type(map.address)=='number' then return map.address end
  return 0xFFFFF
end
local function finish(reason)
  if not alive then return end
  alive=false
  out:write('END\t',reason,'\t',count,'\t',polls,'\t',checked,'\n')
  out:flush();out:close()
  emu.log('JP0740_END '..reason)
end
local function buttons(mask)
  local names={'a','b','select','start','up','down','left','right'}
  local ret={}
  for i,name in ipairs(names) do
    ret[name]=(math.floor(mask/(2^(8-i)))%2)==1
  end
  return ret
end
emu.addEventCallback(function(c)
  if not alive or (c and c~=ct) then return end
  local state=emu.getState() or {}
  local abs=state.frameCount
  if type(abs)~='number' or abs~=frame+epoch then
    finish('INPUT_EPOCH_MISMATCH');return
  end
  local masks=inputs[abs]
  if not masks then finish('MISSING_INPUT');return end
  emu.setInput(buttons(masks[1]),0)
  emu.setInput(buttons(masks[2]),1)
  polls=polls+1
end,emu.eventType.inputPolled)
-- Capture the actually executed CPU PC, then bind following writes to it.
-- The Mesen callback order is not independently proven by this log alone.
emu.addMemoryCallback(function(pc)
  if not alive or frame<begin_frame or frame>stop_frame then return end
  lastpc,lastphys,lastframe=pc,phys(pc),frame
end,emu.callbackType.exec,0x0000,0xFFFF,ct,mem)
for _,addr in ipairs(watch) do
  for mirror=0,3 do
    local bus=addr+0x800*mirror
    emu.addMemoryCallback(function(_,new)
      if not alive or frame<begin_frame or frame>stop_frame then return end
      count=count+1
      if count>150000 then finish('EVENT_LIMIT');return end
      local pc=lastframe==frame and lastpc or 0xFFFF
      local prg=lastframe==frame and lastphys or 0xFFFFF
      out:write(string.format('W\t%d\t%d\t%d\t%04X\t%02X\t%02X\t%04X\t%04X\t%05X\n',
          count,frame,cycle(),addr,emu.read(addr,ram),new,bus,pc,prg))
    end,emu.callbackType.write,bus,bus,ct,mem)
  end
end
for _,addr in ipairs({0x4016,0x4017}) do
  emu.addMemoryCallback(function(_,value)
    if not alive or frame<begin_frame or frame>stop_frame then return end
    count=count+1
    if count>150000 then finish('EVENT_LIMIT');return end
    local pc=lastframe==frame and lastpc or 0xFFFF
    local prg=lastframe==frame and lastphys or 0xFFFFF
    out:write(string.format('R\t%d\t%d\t%d\t%04X\t%02X\t%04X\t%05X\n',
       count,frame,cycle(),addr,value,pc,prg))
  end,emu.callbackType.read,addr,addr,ct,mem)
end
emu.addEventCallback(function(c)
  if not alive or (c and c~=ct) then return end
  local anchor=anchors[frame]
  if anchor then
    local state={}
    for _,addr in ipairs(watch) do
      state[#state+1]=string.format('%02X',emu.read(addr,ram))
    end
    local here=table.concat(state)
    local cyc=cycle()
    if cyc~=anchor[1] or here~=anchor[2] then
      out:write(string.format('ANCHOR_FAIL\t%d\t%d\t%d\t%s\t%s\n',
                frame,cyc,anchor[1],here,anchor[2]))
      finish('ANCHOR_MISMATCH');return
    end
    checked=checked+1
    out:write('ANCHOR_OK\t',frame,'\t',cyc,'\n')
  end
  if frame>=stop_frame then
    finish(checked==4 and 'COMPLETE' or 'ANCHORS_MISSING')
  end
  frame=frame+1
end,emu.eventType.endFrame)
emu.addEventCallback(function() finish('STATE_LOADED') end,emu.eventType.stateLoaded)
emu.addEventCallback(function() finish('SCRIPT_ENDED') end,emu.eventType.scriptEnded)
emu.log('JP0740 replay installed: original ROM and input, writes read-only, 4 authentic anchors required')
