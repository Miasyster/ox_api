@echo off
REM Windows 编译脚本 - 股票下单程序

echo === 编译股票下单程序 ===

REM 设置路径
set INCLUDE_DIR=..\include
set LIB_DIR=..\lib
set LIB_FILE=GuosenOXAPI.lib

REM 编译选项
set COMPILE_OPTIONS=/EHsc /std:c++14 /I%INCLUDE_DIR% /D_CRT_SECURE_NO_WARNINGS
set LINK_OPTIONS=/LIBPATH:%LIB_DIR% %LIB_FILE%

REM 编译
echo 正在编译...
cl %COMPILE_OPTIONS% order_stock.cpp /link %LINK_OPTIONS% /OUT:order_stock.exe

if %ERRORLEVEL% EQU 0 (
    echo.
    echo === 编译成功 ===
    echo 可执行文件: order_stock.exe
    echo.
    echo 注意: 运行前请确保以下文件在同一目录:
    echo   - order_stock.exe
    echo   - GuosenOXAPI.dll
    echo   - uaAPI.dll
    echo   - uaAuth.dll
    echo   - uaCrypto.dll
    echo   - uaPacker.dll
    echo   - gxtrade.ini
) else (
    echo.
    echo === 编译失败 ===
    echo 请检查:
    echo   1. Visual Studio 编译环境是否已设置
    echo   2. include 目录路径是否正确
    echo   3. lib 目录路径是否正确
    echo   4. 库文件是否存在
)

pause

