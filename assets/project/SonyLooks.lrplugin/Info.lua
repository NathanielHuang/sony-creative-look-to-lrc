return {
 LrSdkVersion=13.0, LrSdkMinimumVersion=13.0,
 LrToolkitIdentifier='local.sonylooks.creatorlooks', LrPluginName='SonyLooks创作者外观',
 VERSION={major=0,minor=3,revision=0},
 LrInitPlugin='AutoStart.lua',LrForceInitPlugin=true,
 LrEnablePlugin='AutoStart.lua',LrDisablePlugin='AutoStop.lua',LrShutdownPlugin='AutoStop.lua',
 LrLibraryMenuItems={
  {title='应用到选中照片',file='ApplyCurrent.lua'},
  {title='创建外观虚拟副本',file='Match.lua'},
  {title='开关导入后自动匹配',file='AutoToggle.lua'},
  {title='查看运行状态',file='Status.lua'},
 },
}
