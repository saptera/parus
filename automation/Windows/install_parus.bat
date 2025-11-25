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

ECHO Press any key to start...
ECHO.
PAUSE >NUL
ECHO ----------------------------------------

:: Update PIP
%TPR% -m pip install --upgrade pip

:: Install required packages
%TPR% -m pip install h5py
%TPR% -m pip install "numpy>=2.0.0"
%TPR% -m pip install "scipy>=1.14.0"
%TPR% -m pip install "matplotlib>=3.8.4"
%TPR% -m pip install plotext
%TPR% -m pip install "PySide6>=6.8"
%TPR% -m pip install pyqtgraph
:: Install PyTorch
SET IPT=%cd%%\automation\environment\install_torch.py
%TPR% %IPT%

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


:parsePythonVersion
FOR /F "tokens=1,2,3 DELIMS=." %%a IN ("%~1") DO (
    SET components[1]=%%a
    IF %%b LSS 10 (SET components[2]=0%%b) ELSE (SET components[2]=%%b)
    IF %%c LSS 10 (SET components[3]=0%%c) ELSE (SET components[3]=%%c)
)
SET %~2=%components[1]%%components[2]%%components[3]%
EXIT /B
