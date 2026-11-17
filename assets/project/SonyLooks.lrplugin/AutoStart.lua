local T=import 'LrTasks'
local A=import 'LrApplication'
local P=import 'LrPrefs'
local prefs=P.prefsForPlugin()
if prefs.autoImportEnabled==nil then prefs.autoImportEnabled=true end
if _G.SonyLooksAutoRunning then return end
_G.SonyLooksAutoRunning=true
local generation={};_G.SonyLooksAutoGeneration=generation
T.startAsyncTask(function()
 local U=dofile(_PLUGIN.path..'/Util.lua')
 local seen={};local pending={};local catalogPath
 while _G.SonyLooksAutoGeneration==generation do
  local ok,err=T.pcall(function()
   local catalog=A.activeCatalog();local path=catalog:getPath()
   local photos=catalog:getAllPhotos()
   if path~=catalogPath then
    catalogPath=path;seen={};pending={}
    -- Existing photos form a baseline. They are never swept by the import watcher.
    for _,p in ipairs(photos) do seen[p.localIdentifier]=true end
    U.write('auto-import-status.json',{catalog=path,enabled=prefs.autoImportEnabled,baseline=#photos})
    return
   end
   for _,p in ipairs(photos) do
    local id=p.localIdentifier
    if not seen[id] then
     seen[id]=true
     if prefs.autoImportEnabled and not p:getRawMetadata('isVirtualCopy') and p:getRawMetadata('path'):lower():match('%.arw$') then
      pending[id]={photo=p,first=os.time(),attempts=0}
     end
    end
   end
   if not prefs.autoImportEnabled then pending={};return end
   if _G.SonyLooksMatching then return end
   local batch={};local ids={}
   for id,item in pairs(pending) do
    if os.time()-item.first>=3 and #batch<50 then batch[#batch+1]=item.photo;ids[#ids+1]=id end
   end
   if #batch>0 then
    local E=dofile(_PLUGIN.path..'/ApplyEngine.lua')
    local rows,log=E.run(catalog,batch,true)
    if rows then
     local count=0;local retry={};local needs=0;local fixed=0
     for _,r in ipairs(rows) do
      if r.status=='applied' then count=count+1 end
      if r.status=='needs_preimport' then needs=needs+1 end
      if r.status=='applied' and r.match_mode=='recipe_profile' then fixed=fixed+1 end
      if r.status=='error' then retry[r.path]=true end
     end
     for _,id in ipairs(ids) do
      local item=pending[id];item.attempts=item.attempts+1
      if not retry[item.photo:getRawMetadata('path')] or item.attempts>=3 then pending[id]=nil end
     end
     U.write('auto-import-status.json',{catalog=path,enabled=true,applied=count,fixed_recipe_profiles=fixed,needs_preimport=needs,last_report=log,time=os.time()})
    elseif log~='busy' then
     U.write('auto-import-error.json',{error=log,time=os.time()})
     for _,id in ipairs(ids) do pending[id]=nil end
    end
   end
  end)
  if not ok then U.write('auto-import-error.json',{error=tostring(err),time=os.time()}) end
  T.sleep(5)
 end
end)
