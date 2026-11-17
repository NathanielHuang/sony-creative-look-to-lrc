#!/bin/zsh
set -eu
PROJECT_DIR=${0:A:h}
for candidate in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  if [[ -x "$candidate" ]]; then
    "$candidate" "$PROJECT_DIR/install.py" "$@"
    print '按回车关闭此窗口。'
    read -r reply
    exit 0
  fi
done
print '请先从python.org安装Python3，再运行此文件。'
exit 1
