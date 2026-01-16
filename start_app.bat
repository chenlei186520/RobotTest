@echo off
chcp 65001 >nul
echo ========================================
echo    机器人静态测试系统 - 启动脚本
echo ========================================
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查Python是否可用
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境！
    echo [错误] 请确保已安装Python并添加到系统PATH
    echo [错误] 或使用完整路径指定Python解释器
    pause
    exit /b 1
)

REM 检查虚拟环境是否存在
if exist "venv\Scripts\activate.bat" (
    echo [启动] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo [警告] 虚拟环境激活失败，使用系统Python环境
    ) else (
        echo [启动] 虚拟环境已激活
    )
    echo.
) else (
    echo [启动] 未检测到虚拟环境，使用系统Python环境
    echo.
)

REM 检查app.py是否存在
if not exist "app.py" (
    echo [错误] 未找到 app.py 文件！
    echo [错误] 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

REM 检查requirements.txt中的依赖是否已安装（可选检查）
echo [启动] 检查Python环境...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] Flask未安装，请先运行: pip install -r requirements.txt
    echo [警告] 继续尝试启动...
    echo.
)

echo [启动] 正在启动Flask应用...
echo [启动] 服务地址: http://localhost:5000
echo [启动] 浏览器将自动打开
echo [启动] 按 Ctrl+C 停止服务
echo.
echo ========================================
echo.

REM 在后台启动Flask应用（不打开新窗口）
start /B python app.py

REM 等待Flask应用启动（根据网络和系统性能，等待4秒）
echo [启动] 等待Flask应用启动...
timeout /t 4 /nobreak >nul

REM 自动打开浏览器（只打开一次）
echo [启动] 正在打开浏览器...
start "" http://localhost:5000

REM 关闭启动脚本窗口，Flask应用在后台继续运行
echo.
echo [提示] Flask应用已在后台启动
echo [提示] 浏览器已自动打开
echo [提示] 如需停止Flask应用，请使用任务管理器结束python.exe进程
timeout /t 2 /nobreak >nul
exit
