local P=import 'LrPrefs'
local D=import 'LrDialogs'
local prefs=P.prefsForPlugin()
prefs.autoImportEnabled=not prefs.autoImportEnabled
if prefs.autoImportEnabled then dofile(_PLUGIN.path..'/AutoStart.lua') else dofile(_PLUGIN.path..'/AutoStop.lua') end
D.message('索尼创作者外观',prefs.autoImportEnabled and '导入后自动匹配已开启。' or '导入后自动匹配已关闭。','info')
