local T=import 'LrTasks'
local A=import 'LrApplication'
local D=import 'LrDialogs'
local E=dofile(_PLUGIN.path..'/ApplyEngine.lua')
T.startAsyncTask(function()
 local catalog=A.activeCatalog()
 local rows,log=E.run(catalog,catalog:getTargetPhotos(),false)
 if not rows then D.message('索尼创作者外观',tostring(log),'critical');return end
 local count=0
 for _,r in ipairs(rows) do if r.status=='applied' then count=count+1 end end
 D.message('索尼创作者外观','已为'..count..'张当前照片应用外观。其他调整已保留。\n'..tostring(log or ''),'info')
end)
