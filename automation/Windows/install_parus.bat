@ECHO OFF
TITLE PARUS Installer
ECHO  __^| ^|_____________________________^| ^|__
ECHO (__   _____________________________   __)
ECHO    ^| ^|                             ^| ^|
ECHO    ^| ^|  PARUS Installation Script  ^| ^|
ECHO  __^| ^|_____________________________^| ^|__
ECHO (__   _____________________________   __)
ECHO    ^| ^|                             ^| ^|
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

ECHO Press any key to start...
ECHO.
PAUSE >NUL
ECHO ----------------------------------------

:: Call installation script
FOR %%i IN ("%~dp0..") DO SET "SCPT=%%~fi\environment\install_parus.py"
%TPR% %SCPT%

ECHO ----------------------------------------
ECHO.
ECHO DONE
ECHO Press any key to exit...
PAUSE >NUL
EXIT


:errorNoPython
ECHO Error^: Python not installed or not in PATH
PAUSE >NUL
EXIT
