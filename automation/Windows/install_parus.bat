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
IF EXIST "%PKG%\venv\" (
    SET TPR="%PKG%\venv\Scripts\python.exe"
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
%TPR% "%SCPT%"
ECHO ----------------------------------------
ECHO.
:: Create desktop shortcuts
CHOICE /C YN /N /T 5 /D Y /M "Create shortcuts on desktop (Y/n)?"
IF %ERRORLEVEL% EQU 1 GOTO createShortcut

:finalPrint
ECHO.
ECHO DONE
ECHO Press any key to exit...
PAUSE >NUL
EXIT


:errorNoPython
ECHO Error^: Python not installed or not in PATH
PAUSE >NUL
EXIT


:createShortcut
:: Create shortcut for PARUS Train
ECHO Creating shortcut for model training GUI
SET BAT_PATH="%PKG%\automation\Windows\ParusTrn.bat"
SET ICO_PATH="%PKG%\parus\gui\assets\icon_trn.ico"
SET SHORTCUT_PATH="%USERPROFILE%\Desktop\PARUS Train.lnk"
powershell -command ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
    $Shortcut.TargetPath = '%BAT_PATH%'; ^
    $Shortcut.IconLocation = '%ICO_PATH%'; ^
    $Shortcut.Save()
:: Create shortcut for PARUS Data
ECHO Creating shortcut for data pipeline GUI
SET BAT_PATH="%PKG%\automation\Windows\ParusDat.bat"
SET ICO_PATH="%PKG%\parus\gui\assets\icon_dat.ico"
SET SHORTCUT_PATH="%USERPROFILE%\Desktop\PARUS Data.lnk"
powershell -command ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
    $Shortcut.TargetPath = '%BAT_PATH%'; ^
    $Shortcut.IconLocation = '%ICO_PATH%'; ^
    $Shortcut.Save()
:: Create shortcut for PARUS Real-Time
ECHO Creating shortcut for real-time GUI
SET BAT_PATH="%PKG%\automation\Windows\ParusRT.bat"
SET ICO_PATH="%PKG%\parus\rt\assets\icon_rt.ico"
SET SHORTCUT_PATH="%USERPROFILE%\Desktop\PARUS Real-Time.lnk"
powershell -command ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
    $Shortcut.TargetPath = '%BAT_PATH%'; ^
    $Shortcut.IconLocation = '%ICO_PATH%'; ^
    $Shortcut.Save()
GOTO finalPrint
