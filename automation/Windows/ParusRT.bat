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

:: Set valid Python version range [inclusive, exclusive)
SET minVersion=3.10.0
SET maxVersion=9.9.9

:: Set Python interpreter
IF EXIST %cd%%\venv\ (
    SET TPR=%cd%%\venv\Scripts\python.exe
) ELSE (
    SET TPR=python
)

:: Check Python installation
%TPR% -V 2>NUL
IF errorLevel 1 GOTO errorNoPython
:: Check Python version
CALL :parsePythonVersion %minVersion%, parMinVer
CALL :parsePythonVersion %maxVersion%, parMaxVer
FOR /F "tokens=2 USEBACKQ DELIMS= " %%F IN (`python -V`) DO (SET version=%%F)
CALL :parsePythonVersion %version%, parVer
IF %parVer% LSS %parMinVer% (
    ECHO Version too low, Python ^>^=%minVersion% required.
    PAUSE >NUL
    EXIT
) ELSE IF %parVer% GEQ %parMaxVer% (
    ECHO Version too high, Python ^<%maxVersion% required.
    PAUSE >NUL
    EXIT
)

:: Launch PARUS RT GUI
ECHO Starting PARUS Real-Time System...
ECHO.
ECHO Python command line outputs
ECHO ----------------------------------------

SET GUI=%cd%%\parus\app\pac_rt.py
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


:parsePythonVersion
FOR /F "tokens=1,2,3 DELIMS=." %%a IN ("%~1") DO (
    SET components[1]=%%a
    IF %%b LSS 10 (SET components[2]=0%%b) ELSE (SET components[2]=%%b)
    IF %%c LSS 10 (SET components[3]=0%%c) ELSE (SET components[3]=%%c)
)
SET %~2=%components[1]%%components[2]%%components[3]%
EXIT /B
