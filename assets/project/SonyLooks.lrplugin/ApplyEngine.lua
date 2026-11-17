local U=dofile(_PLUGIN.path..'/Util.lua')
local T=import 'LrTasks'
local C=dofile(_PLUGIN.path..'/Config.lua')
local E={}
local shell=U.shell
local function defaultProfile(s)
 local name=s.Look and s.Look.Name
 return (name=='Adobe Color' or name=='Adobe Monochrome' or not name)
  and (s.CameraProfile=='Adobe Standard' or s.CameraProfile=='Adobe Color' or s.CameraProfile=='Adobe Monochrome')
end
local function otherSettings(s)
 local result={}
 for k,v in pairs(s) do if k~='Look' and k~='CameraProfile' then result[k]=v end end
 return U.json(result)
end
function E.run(catalog,photos,automatic)
 if _G.SonyLooksMatching then return nil,'busy' end
 _G.SonyLooksMatching=true
 local ok,rows,logname=T.pcall(function()
  local request={};local byPath={};local before={}
  for _,p in ipairs(photos) do
   local path=p:getRawMetadata('path')
   if path:lower():match('%.arw$') and not p:getRawMetadata('isVirtualCopy') and not byPath[path] then
    local s=p:getDevelopSettings()
    if not automatic or defaultProfile(s) then
     request[#request+1]=path;byPath[path]=p;before[path]=s
    end
   end
  end
  if #request==0 then return {},nil end
  _G.SonyLooksRequestCounter=(_G.SonyLooksRequestCounter or 0)+1
  local id=tostring(os.time())..'-'..tostring(_G.SonyLooksRequestCounter)
  local req=U.path.child(U.data,'reports/import-request-'..id..'.json')
  local result=U.path.child(U.data,'reports/import-result-'..id..'.lua')
  local f=assert(io.open(req,'wb'));f:write(U.json(request));f:close()
  local cmd=shell(C.python)..' '..shell(U.path.child(U.root,'core/bridge.py'))..' '..shell(req)..' '..shell(result)..' --allow-recipe-profile'
  if T.execute(U.command(cmd))~=0 then error('SonyLooks metadata helper failed') end
  local matches=assert(loadfile(result))()
  local log='import-match-'..id..'.json'
  -- Persist the original catalog settings before entering the write transaction.
  U.write('import-before-'..id..'.json',{catalog=catalog:getPath(),settings=before})
  catalog:withWriteAccessDo('SonyLooks match imported creator looks',function()
   for _,r in ipairs(matches) do
    if r.status=='matched' then
     local p=byPath[r.path];local s=p:getDevelopSettings()
     if U.json(s)~=U.json(before[r.path]) then
      r.status='changed_during_matching'
     else
      p:applyDevelopSettings(r.settings,'SonyLooks '..r.name)
      r.status='pending';r.before=s
     end
    end
   end
  end)
  -- LRC publishes develop settings after the write transaction has completed.
  T.sleep(1)
  for _,r in ipairs(matches) do
   if r.status=='pending' then
    local p=byPath[r.path];local got=p:getDevelopSettings()
    local digest=got.Look and got.Look.Parameters and got.Look.Parameters.RGBTable
    r.after=got;r.other_settings_preserved=otherSettings(r.before)==otherSettings(got)
    if digest==r.settings.Look.Parameters.RGBTable and got.CameraProfile==r.settings.CameraProfile then
     r.status='applied'
    else
     if got.CameraProfile==r.settings.CameraProfile then
      catalog:withWriteAccessDo('Restore SonyLooks profile attempt',function()
       p:applyDevelopSettings({CameraProfile=r.before.CameraProfile,Look=r.before.Look or {}},'Restore previous profile')
      end)
     end
     r.status='profile_unavailable';r.reason='LRC did not retain the expected RGBTable'
    end
   end
  end
  U.write(log,{catalog=catalog:getPath(),automatic=automatic,photos=matches})
  return matches,log
 end)
 _G.SonyLooksMatching=false
 if not ok then return nil,tostring(rows) end
 return rows,logname
end
return E
