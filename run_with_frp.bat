@echo off
setlocal
chcp 65001 > nul

echo ======================================================
echo   LoseWeightEasily 启动程序 (后端 + 内网穿透)
echo ======================================================

:: 1. 启动后端服务
echo [1/2] 正在启动后端服务 (端口 16666)...
start "LoseWeight-Backend" /D "%~dp0backend" uv run uvicorn src.app:app --host 127.0.0.1 --port 16666

:: 等待几秒钟确保后端启动
echo 正在等待后端初始化...
timeout /t 5 /nobreak > nul

:: 2. 启动 ChmlFrp
echo [2/2] 正在启动 ChmlFrp 内网穿透...
set FRP_DIR=D:\FlutterApp\LoseWeightEasily\backend\ChmlFrp-0.51.2_251023_windows_amd64
start "ChmlFrp" /D "%FRP_DIR%" frpc.exe -u Uuvg5rxjB5puayb2r3SJBq0A -p 253235

echo.
echo ------------------------------------------------------
echo 启动完成！后端与 FRP 均在独立窗口中运行。
echo 请保持窗口开启以维持服务运行。
echo ------------------------------------------------------
pause
