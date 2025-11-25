@ECHO OFF
TITLE PARUS Model Training
ECHO  __^| ^|________________________^| ^|__
ECHO (__   ________________________   __)
ECHO    ^| ^|                        ^| ^|
ECHO    ^| ^|  PARUS Model Training  ^| ^|
ECHO  __^| ^|________________________^| ^|__
ECHO (__   ________________________   __)
ECHO    ^| ^|                        ^| ^|
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

:: Launch PARUS training GUI
ECHO Starting PARUS Training System...
ECHO.
ECHO Python command line outputs
ECHO ----------------------------------------

SET GUI=%PKG%\parus\app\pac_ma.py
%TPR% %GUI% -m trn

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
