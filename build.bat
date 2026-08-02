@echo off
REM 打包学生端为单个 exe（需先安装 pyinstaller：pip install pyinstaller）
cd /d "%~dp0"
pyinstaller --noconfirm --clean --onefile --windowed ^
  --name DocFormatTool ^
  --paths . ^
  --add-data "configs;configs" ^
  app\main.py
echo.
echo 打包完成：dist\DocFormatTool.exe
pause
