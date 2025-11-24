@echo off
REM 切换到bin目录，确保Tradelog.prop等配置文件能被正确找到
cd /d %~dp0..\bin
REM 运行demo程序，配置文件路径相对于bin目录
demo.exe --file=config/config.ini
pause