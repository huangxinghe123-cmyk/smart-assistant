@echo off
chcp 65001 >nul
title 数智助手 - 打包工具

echo ========================================
echo    数智助手 Smart Assistant v2.0
echo   正在打包为 EXE ...
echo ========================================
echo.

cd /d "%~dp0"

if not exist user_data mkdir user_data
if not exist user_data\notes mkdir user_data\notes
if not exist logs mkdir logs
if not exist config mkdir config

REM 确保 icon 存在
if not exist "assets\app_icon.ico" (
    echo ⚠️ 未找到图标文件，跳过图标
    set ICON_ARG=
) else (
    set ICON_ARG=--icon "assets\app_icon.ico"
)

pyinstaller --onefile --windowed ^
    --name "数智助手" ^
    %ICON_ARG% ^
    --add-data "assets;assets" ^
    --add-data "scraper;scraper" ^
    --add-data "ui;ui" ^
    --add-data "config;config" ^
    --add-data "version.json;." ^
    --hidden-import playwright.async_api ^
    --hidden-import playwright.sync_api ^
    --hidden-import pdfplumber ^
    --collect-all playwright ^
    --distpath ".\dist" ^
    --workpath ".\build" ^
    --specpath ".\" ^
    main.py

echo.
echo ========================================
if exist "dist\数智助手.exe" (
    echo ✅ 打包成功！
    echo 📍 文件位置: "%~dp0dist\数智助手.exe"
    copy /Y "dist\数智助手.exe" "%USERPROFILE%\Desktop\数智助手.exe" >nul
    echo ✅ 桌面快捷方式已创建！
    echo 文件大小: %~z0 字节
) else (
    echo ❌ 打包失败，请检查错误信息
)
echo ========================================
pause
