@echo off
echo 正在启动售后报修工单系统...
echo.
:: 激活虚拟环境
call .venv\Scripts\activate
:: 启动 Flask 服务
python src/app.py
pause