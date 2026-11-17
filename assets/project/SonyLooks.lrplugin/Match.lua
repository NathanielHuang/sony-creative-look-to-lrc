local U=dofile(_PLUGIN.path..'/Util.lua')
local T=import 'LrTasks'
local A=import 'LrApplication'
local D=import 'LrDialogs'
local C=dofile(_PLUGIN.path..'/Config.lua')
local shell=U.shell
T.startAsyncTask(function()
 if _G.SonyLooksMatching then D.message('索尼创作者外观','正在匹配，请稍候。','info');return end
 _G.SonyLooksMatching=true
 local ok,err=T.pcall(function()
  local catalog=A.activeCatalog();local selected=catalog:getTargetPhotos()
  local request={};local byPath={}
  for _,p in ipairs(selected) do
   local path=p:getRawMetadata('path')
   if path:lower():match('%.arw$') and not byPath[path] then
    request[#request+1]=path;byPath[path]=p
   end
  end
  if #request==0 then D.message('索尼创作者外观','请先选中ARW照片。','info');return end
  local suffix=tostring(os.time())
  local req=U.path.child(U.data,'reports/plugin-request-'..suffix..'.json')
  local result=U.path.child(U.data,'reports/plugin-result-'..suffix..'.lua')
  local f=assert(io.open(req,'wb'));f:write(U.json(request));f:close()
  local cmd=shell(C.python)..' '..shell(U.path.child(U.root,'core/bridge.py'))..' '..shell(req)..' '..shell(result)..' --allow-recipe-profile'
  if T.execute(U.command(cmd))~=0 then error('元数据读取失败，请查看运行记录。') end
  local rows=assert(loadfile(result))();local eligible={};local specs={};local before={}
  for _,r in ipairs(rows) do
   if r.status=='matched' then
    local p=byPath[r.path];eligible[#eligible+1]=p;specs[r.path]=r
    before[r.path]=p:getDevelopSettings()
   end
  end
  if #eligible==0 then U.write('plugin-match-'..suffix..'.json',rows);D.message('索尼创作者外观','没有匹配到已配置的外观，请检查配方和适配记录。','info');return end
  -- Create virtual copies from the current edits. Originals and their sidecars stay intact.
  catalog:setSelectedPhotos(eligible[1],eligible)
  local copies=catalog:createVirtualCopies('SonyLooks creator look')
  catalog:withWriteAccessDo('SonyLooks creator looks on virtual copies',function()
   for _,p in ipairs(copies) do
    local path=p:getRawMetadata('path');local r=specs[path]
    p:applyDevelopSettings(r.settings,'SonyLooks '..r.name)
    p:setRawMetadata('copyName',r.name)
   end
  end)
  T.sleep(1)
  local passed=0
  for _,p in ipairs(copies) do
   local path=p:getRawMetadata('path');local r=specs[path];local got=p:getDevelopSettings()
   local digest=got.Look and got.Look.Parameters and got.Look.Parameters.RGBTable
   r.original_unchanged=U.json(before[path])==U.json(byPath[path]:getDevelopSettings())
   r.before=before[path];r.after=got
   if digest==r.settings.Look.Parameters.RGBTable and r.original_unchanged then
    r.status='applied_to_virtual_copy';passed=passed+1
   else
    catalog:withWriteAccessDo('Restore unrenderable SonyLooks virtual copy',function()p:applyDevelopSettings(before[path],'Restore original settings')end)
    r.status='table_not_registered';r.reason='RGBTable unavailable in LRC; copy restored. Load complete XMP or restart after profile installation.'
   end
  end
  U.write('plugin-match-'..suffix..'.json',rows)
  D.message('索尼创作者外观','已为'..passed..'张照片创建外观虚拟副本。运行记录：'..U.data..'/reports/plugin-match-'..suffix..'.json','info')
 end)
 _G.SonyLooksMatching=false
 if not ok then D.message('索尼创作者外观',tostring(err),'critical') end
end)
