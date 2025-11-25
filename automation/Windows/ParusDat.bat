@ECHO OFF
TITLE PARUS Data Pipeline
ECHO  __^| ^|_______________________^| ^|__
ECHO (__   _______________________   __)
ECHO    ^| ^|                       ^| ^|
ECHO    ^| ^|  PARUS Data Pipeline  ^| ^|
ECHO  __^| ^|_______________________^| ^|__
ECHO (__   _______________________   __)
ECHO    ^| ^|                       ^| ^|
ECHO.

:: Set Python interpreter
FOR %%i IN ("%~dp0..\..") DO SET "PKG=%%~fi"
IF EXIST %PKG%\venv\ (
    SET TPR=%PKG%\venv\Scripts\python.exe
) ELSE (
    SET TPR=python
)

:: Check Python installation
%TPR% -V 2>NUL
IF errorLevel 1 GOTO errorNoPython

:: Launch PARUS data GUI
ECHO Starting PARUS Data System...
ECHO.
ECHO Python command line outputs
ECHO ----------------------------------------

SET GUI=%PKG%\parus\app\pac_ma.py
%TPR% %GUI% -m dat

ECHO ----------------------------------------
ECHO.
ECHO System GUI has stopped
ECHO Press any key to exit...
PAUSE >NUL
EXIT


:errorNoPython
ECHO Error^: Python not installed or not in PATH
PAUSE >NUL
EXIT
