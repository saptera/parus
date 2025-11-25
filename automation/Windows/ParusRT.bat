@ECHO OFF
TITLE PARUS Real-Time System
ECHO  __^| ^|__________________________^| ^|__
ECHO (__   __________________________   __)
ECHO    ^| ^|                          ^| ^|
ECHO    ^| ^|  PARUS Real-Time System  ^| ^|
ECHO  __^| ^|__________________________^| ^|__
ECHO (__   __________________________   __)
ECHO    ^| ^|                          ^| ^|
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

:: Launch PARUS RT GUI
ECHO Starting PARUS Real-Time System...
ECHO.
ECHO Python command line outputs
ECHO ----------------------------------------

SET GUI=%PKG%\parus\app\pac_rt.py
%TPR% %GUI%

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
