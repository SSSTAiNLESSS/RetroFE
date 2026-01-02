@echo off
echo Deploying RetroFE test build to CORE - TYPE R...

set SOURCE=P:\Documents\github\RetroFE\Builds
set DEST=P:\Desktop\CORE - TYPE R\core

REM Find the most recent build folder
for /f "delims=" %%i in ('dir /b /od "%SOURCE%\*feature-vlc-replacement*"') do set LATEST=%%i

if "%LATEST%"=="" (
    echo ERROR: No VLC build found!
    exit /b 1
)

echo Using build: %LATEST%

REM Copy all files
copy /Y "%SOURCE%\%LATEST%\retrofe.exe" "%DEST%\retrofe.exe"
copy /Y "%SOURCE%\%LATEST%\libvlc.dll" "%DEST%\libvlc.dll"
copy /Y "%SOURCE%\%LATEST%\libvlccore.dll" "%DEST%\libvlccore.dll"
xcopy /E /I /Y "%SOURCE%\%LATEST%\plugins" "%DEST%\plugins"

REM Copy SDL2 DLLs
set THIRDPARTY=P:\Documents\github\RetroFE\RetroFE\ThirdParty
copy /Y "%THIRDPARTY%\SDL2-2.0.14\lib\x86\SDL2.dll" "%DEST%\SDL2.dll"
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\SDL2_image.dll" "%DEST%\SDL2_image.dll"
copy /Y "%THIRDPARTY%\SDL2_mixer-2.0.4\lib\x86\SDL2_mixer.dll" "%DEST%\SDL2_mixer.dll"
copy /Y "%THIRDPARTY%\SDL2_ttf-2.0.15\lib\x86\SDL2_ttf.dll" "%DEST%\SDL2_ttf.dll"

REM Copy image format support DLLs
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\libjpeg-9.dll" "%DEST%\libjpeg-9.dll"
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\libpng16-16.dll" "%DEST%\libpng16-16.dll"
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\libtiff-5.dll" "%DEST%\libtiff-5.dll"
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\libwebp-7.dll" "%DEST%\libwebp-7.dll"
copy /Y "%THIRDPARTY%\SDL2_image-2.0.5\lib\x86\zlib1.dll" "%DEST%\zlib1.dll"
copy /Y "%THIRDPARTY%\SDL2_ttf-2.0.15\lib\x86\libfreetype-6.dll" "%DEST%\libfreetype-6.dll"

echo.
echo Deployment complete!
echo You can now test RetroFE in: %DEST%