local U={}
U.path=import 'LrPathUtils'
local F=import 'LrFileUtils'
local C=dofile(_PLUGIN.path..'/Config.lua')
U.root=_PLUGIN.path
U.data=C.dataDir or U.path.child(U.path.getStandardFilePath('appData'),'SonyCreativeLooks')
F.createAllDirectories(U.path.child(U.data,'reports'))
function U.quote(s)
 return '"'..s:gsub('[%z\1-\31\\"]',function(c)
  if c=='"' then return '\\"' elseif c=='\\' then return '\\\\' end
  return string.format('\\u%04x',string.byte(c)) end)..'"'
end
function U.json(t)
 local k=type(t)
 if k=='string' then return U.quote(t) end
 if k=='number' or k=='boolean' then return tostring(t) end
 if k=='nil' then return 'null' end
 if k~='table' then return U.quote(tostring(t)) end
 local a={}; local n=0; local seq=true
 for key in pairs(t) do n=n+1;if type(key)~='number' then seq=false end end
 if seq and n>0 and #t==n then
  for i=1,n do a[#a+1]=U.json(t[i]) end
  return '['..table.concat(a,',')..']'
 end
 for key,value in pairs(t) do a[#a+1]=U.quote(tostring(key))..':'..U.json(value) end
 table.sort(a);return '{'..table.concat(a,',')..'}'
end
function U.write(name,value)
 assert(not name:find('[/\\]'),'Invalid report name')
 local f=assert(io.open(U.path.child(U.data,'reports/'..name),'wb'))
 f:write(U.json(value));f:close()
end
function U.shell(s)
 if WIN_ENV then
  assert(not s:find('["%%!\r\n]'),'Unsupported special character in Windows path')
  return '"'..s..'"'
 end
 return "'"..s:gsub("'","'\\''").."'"
end
function U.command(s) return WIN_ENV and ('"'..s..'"') or s end
return U
