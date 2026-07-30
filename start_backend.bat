@echo off
title Financial Backend

cd /d "%~dp0"

..\.venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8080 FinantialEv_v1.wsgi:application

pause