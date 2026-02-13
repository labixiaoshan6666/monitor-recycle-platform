@echo off
chcp 65001 >nul
REM Windows 系统定时任务配置脚本
REM 用途：设置每天早上6点自动运行爬虫

echo ========================================
echo   二手回收爬虫定时任务配置脚本 (Windows)
echo ========================================
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%run_daily_crawl.py"

REM 检查 Python 脚本是否存在
if not exist "%PYTHON_SCRIPT%" (
    echo [错误] 找不到 run_daily_crawl.py
    pause
    exit /b 1
)

REM 查找 Python 路径
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('where python') do set "PYTHON_PATH=%%i"
    goto :found_python
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('where python3') do set "PYTHON_PATH=%%i"
    goto :found_python
)

echo [错误] 未找到 Python，请先安装 Python
pause
exit /b 1

:found_python
echo [✓] Python 路径: %PYTHON_PATH%

REM 创建日志目录
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"
echo [✓] 日志目录: %SCRIPT_DIR%logs

REM 删除已存在的任务（如果有）
schtasks /Query /TN "RecycleCrawlerDaily" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [!] 检测到已存在的任务，正在删除...
    schtasks /Delete /TN "RecycleCrawlerDaily" /F >nul 2>&1
)

REM 创建定时任务
echo [*] 正在创建定时任务...
schtasks /Create ^
    /TN "RecycleCrawlerDaily" ^
    /TR "\"%PYTHON_PATH%\" \"%PYTHON_SCRIPT%\"" ^
    /SC DAILY ^
    /ST 06:00 ^
    /F ^
    /RU "%USERNAME%"

if %ERRORLEVEL% EQU 0 (
    echo [✓] 定时任务创建成功
) else (
    echo [✗] 定时任务创建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 定时任务详情：
echo ========================================
echo   任务名称: RecycleCrawlerDaily
echo   执行时间: 每天早上 6:00
echo   执行命令: "%PYTHON_PATH%" "%PYTHON_SCRIPT%"
echo   日志目录: %SCRIPT_DIR%logs
echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 提示：
echo   1. 查看任务: schtasks /Query /TN "RecycleCrawlerDaily"
echo   2. 运行任务: schtasks /Run /TN "RecycleCrawlerDaily"
echo   3. 删除任务: schtasks /Delete /TN "RecycleCrawlerDaily" /F
echo   4. 手动测试: "%PYTHON_PATH%" "%PYTHON_SCRIPT%"
echo   5. 查看日志: type "%SCRIPT_DIR%logs\crawl_*.log"
echo.
pause
