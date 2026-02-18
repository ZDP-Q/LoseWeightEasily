@echo off
setlocal
chcp 65001 > nul

echo ======================================================
echo   LoseWeightEasily 内网穿透启动程序 (ChmlFrp)
echo ======================================================

set FRP_DIR=D:\FlutterApp\LoseWeightEasily\backend\ChmlFrp-0.51.2_251023_windows_amd64
echo 正在启动 ChmlFrp 内网穿透...
cd /d "%FRP_DIR%"
frpc.exe -u Uuvg5rxjB5puayb2r3SJBq0A -p 253947

pause
