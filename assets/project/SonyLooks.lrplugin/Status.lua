local D=import 'LrDialogs'
local P=import 'LrPrefs'
local U=dofile(_PLUGIN.path..'/Util.lua')
local C=dofile(_PLUGIN.path..'/Config.lua')
D.message(C.displayName or '索尼创作者外观',
 '导入后自动匹配：'..(P.prefsForPlugin().autoImportEnabled and '已开启' or '已关闭')..
 '\n外观：'..(C.lookNames or '')..'\n运行记录：'..U.data..'/reports','info')
