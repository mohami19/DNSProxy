@echo off
setlocal EnableDelayedExpansion

set "PYTHON_SCRIPT=.\src\dns_helper.py"
set "INPUT_FILE=.\src\random-domains.txt"

for /f "delims=" %%l in (%INPUT_FILE%) do (
    set "LINE=%%l"
    python "%PYTHON_SCRIPT%" !LINE! 127.0.0.3 5006 A
)

endlocal