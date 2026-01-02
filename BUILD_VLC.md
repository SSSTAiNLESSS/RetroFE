# libVLC Replacement - Build Instructions

## Overview

The GStreamer video backend has been completely replaced with libVLC. This document provides step-by-step instructions to compile and test the new implementation.

**Branch:** `feature/vlc-replacement`
**Implementation:** CORE Team

**IMPORTANT:** This guide is for **developers compiling RetroFE**. End users do NOT need to download or install VLC - the required DLLs are automatically bundled with the compiled RetroFE distribution.

## Changes Summary

- **Removed:** GStreamerVideo.cpp, GStreamerVideo.h, all GStreamer/GLib dependencies
- **Added:** VLCVideo.cpp, VLCVideo.h - complete libVLC implementation
- **Modified:**
  - VideoFactory.cpp - Creates VLCVideo instances
  - VideoComponent.cpp - Smart volume-based playback
  - CMakeLists.txt - VLC configuration
  - Sound.cpp/h - Added stop() function
  - Page.cpp - Stops sounds on menu switch
  - SDL.cpp - Fixed audio to stereo

## Prerequisites

Before building, you need:

1. **Visual Studio 2019 or newer** (with C++ desktop development workload)
2. **CMake** (version 2.8 or newer)
3. **libVLC SDK for Windows (32-bit)**

## Step 1: Download libVLC SDK

1. Download VLC 3.0.21 (32-bit) - **ZIP version**:
   - **Direct link (ZIP):** https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win32/vlc-3.0.21-win32.zip
   - Alternative: https://get.videolan.org/vlc/3.0.21/win32/vlc-3.0.21-win32.zip

2. Extract to `C:\libvlc\`:
```powershell
# Download and extract
Expand-Archive C:\libvlc\vlc-3.0.21-win32.zip -DestinationPath C:\libvlc\
```

After extraction, the structure should be `C:\libvlc\vlc-3.0.21\` containing all VLC files.

After extraction, verify you have:
```
C:\libvlc\vlc-3.0.21\
├── sdk\
│   ├── include\
│   │   └── vlc\
│   │       └── vlc.h
│   └── lib\
│       ├── libvlc.lib
│       └── libvlccore.lib
├── libvlc.dll
├── libvlccore.dll
└── plugins\
    └── (many .dll files)
```

**Important:** CMake will look for:
- Headers: `C:\libvlc\vlc-3.0.21\sdk\include\vlc\vlc.h`
- Libraries: `C:\libvlc\vlc-3.0.21\sdk\lib\libvlc.lib`
- Runtime DLLs: `C:\libvlc\vlc-3.0.21\libvlc.dll`

You'll need to set `LIBVLC_ROOT` to `C:\libvlc\vlc-3.0.21` in the next step.

## Step 2: Checkout the Branch

```powershell
cd P:\Documents\github\RetroFE
git checkout feature/vlc-replacement
```

Verify you're on the correct branch:
```powershell
git status
```

Should show: `On branch feature/vlc-replacement`

## Step 3: Configure CMake

Clean any previous build:
```powershell
Remove-Item -Recurse -Force .\RetroFE\Build\* -ErrorAction SilentlyContinue
```

Generate Visual Studio solution with libVLC path:

```powershell
cmake -A Win32 -B .\RetroFE\Build -D LIBVLC_ROOT=C:\libvlc\vlc-3.0.21 -S .\RetroFE\Source
```

**If you extracted/installed to a different location, adjust the path accordingly.**

**Expected output:**
```
-- Found libVLC include: C:/libvlc/vlc-3.0.21/sdk/include
-- Found libVLC library: C:/libvlc/vlc-3.0.21/sdk/lib/libvlc.lib
-- Found libVLCcore library: C:/libvlc/vlc-3.0.21/sdk/lib/libvlccore.lib
-- Configuring done
-- Generating done
```

**If you see an error:**
```
FATAL_ERROR "libVLC not found! Please set LIBVLC_ROOT to the libVLC installation directory. Expected structure: C:/libvlc/vlc-3.0.21/sdk/include/vlc/vlc.h and C:/libvlc/vlc-3.0.21/sdk/lib/libvlc.lib"
```

This means CMake cannot find libVLC. Verify:
1. The path is correct: `C:\libvlc\vlc-3.0.21`
2. The SDK directory exists: `C:\libvlc\vlc-3.0.21\sdk`
3. The header file exists: `C:\libvlc\vlc-3.0.21\sdk\include\vlc\vlc.h`
4. The library files exist: `C:\libvlc\vlc-3.0.21\sdk\lib\libvlc.lib`

## Step 4: Build

**Option A: Manual cmake build**
```powershell
cmake --build .\RetroFE\Build --config Release --clean-first
```

Then manually copy libVLC DLLs:
```powershell
Copy-Item C:\libvlc\vlc-3.0.21\libvlc.dll .\RetroFE\Build\Release\
Copy-Item C:\libvlc\vlc-3.0.21\libvlccore.dll .\RetroFE\Build\Release\
Copy-Item -Recurse C:\libvlc\vlc-3.0.21\plugins .\RetroFE\Build\Release\
```

**Option B: Use build_and_store.ps1 (RECOMMENDED - automatic bundling)**

First, verify the libVLC path in the script matches your installation:
```powershell
# Edit line 9 of Scripts\build_and_store.ps1 if needed:
# $LIBVLC_ROOT = "C:\libvlc\vlc-3.0.21"
```

Then run:
```powershell
.\Scripts\build_and_store.ps1
```

This script will:
1. Let you select a branch
2. Configure cmake with libVLC at `C:\libvlc\vlc-3.0.21`
3. Compile the project
4. **Automatically bundle libVLC DLLs and plugins**
5. Store everything in `Builds\<timestamp>_<branch>` folder

**Expected output (end of build):**
```
[2/4] Compiling (Release Mode)...
  retrofe.vcxproj -> P:\Documents\github\RetroFE\RetroFE\Build\Release\retrofe.exe
Build succeeded.

[3/4] Bundling libVLC runtime files...
  Copied libvlc.dll
  Copied libvlccore.dll
  Copied plugins directory (247 files)

[4/4] Storing Build (vlc)...

SUCCESS (vlc)!
Build saved to: .\Builds\2026-01-02_14-30-15_feature-vlc-replacement
  - retrofe.exe
  - libvlc.dll, libvlccore.dll
  - plugins\ directory
```

## Step 5: Copy Runtime DLLs (AUTOMATIC)

**The build script now automatically bundles libVLC DLLs!**

During the build process (Step 4), the script will:
- Copy `libvlc.dll` and `libvlccore.dll` to the build directory
- Copy the entire `plugins\` directory
- Include all files in the `Builds\` timestamped folder

You should see output like:
```
[3/4] Bundling libVLC runtime files...
  Copied libvlc.dll
  Copied libvlccore.dll
  Copied plugins directory (247 files)
```

Verify the files are present:
```powershell
dir .\RetroFE\Build\Release\
```

Should show:
```
libvlc.dll
libvlccore.dll
retrofe.exe
plugins\ (directory)
```

**Note:** If you're using `Scripts\build_and_store.ps1`, the DLLs will also be copied to the timestamped build folder automatically.

## Step 6: Test Video Playback

1. Launch RetroFE:
```powershell
cd .\RetroFE\Build\Release
.\retrofe.exe
```

2. Navigate to a collection with video artwork
3. Check if videos play in the background

## Step 7: Check Log File

After running RetroFE, check the log for video-related messages:

```powershell
type log.txt | Select-String "Video"
```

**Success indicators:**
```
[INFO] [Video] libVLC initialized successfully
[INFO] [Video] Playing: <path-to-video>
```

**Failure indicators:**
```
[ERROR] [Video] Failed to initialize libVLC
[ERROR] [Video] Failed to create media from file: <path>
[ERROR] [Video] Failed to create media player
```

If you see errors:
1. Verify all DLLs are present in the executable directory
2. Check that the plugins folder exists and contains .dll files
3. Verify video file paths are correct
4. Try a different video file format (mp4, avi, mkv all supported)

## Known Differences from GStreamer

- **Initialization:** libVLC initializes faster (no GStreamer pipeline setup)
- **Format support:** libVLC has native support for more formats
- **DLL count:** Only 3 core DLLs + plugins (vs 278 GStreamer DLLs)
- **Seeking controls:** VLC implementation supports both time-based (10s) and percentage-based (5%) seeking
- **Performance:** Smart playback - videos/audio only decode when volume > 0.01
- **Audio:** Fixed to stereo output with optimized buffer size (was mono)

## Testing Checklist

- [ ] Build completes without errors
- [ ] retrofe.exe launches without crashes
- [ ] Intro video plays and transitions to menu
- [ ] Videos play in collection views
- [ ] Video loops correctly (if configured)
- [ ] Volume control works (layout controls actual volume)
- [ ] Background audio/video only plays when needed (performance)
- [ ] Audio plays in correct menus only
- [ ] SDL images display correctly (PNG/JPG)
- [ ] No errors in log.txt related to libVLC

## Troubleshooting

### Build Error: "Cannot open include file: 'vlc/vlc.h'"

**Solution:** libVLC SDK not found. Verify:
```powershell
Test-Path C:\libvlc\include\vlc\vlc.h
```

If false, re-extract libVLC SDK to C:\libvlc or specify correct path with `-D LIBVLC_ROOT=<path>`

### Runtime Error: "The code execution cannot proceed because libvlc.dll was not found"

**Solution:**
- If using `build_and_store.ps1`: This should not happen (DLLs are auto-bundled)
- If manual build: Copy runtime DLLs to executable directory (see Step 4, Option A)
- Check that `libvlc.dll`, `libvlccore.dll`, and `plugins\` directory are in the same folder as `retrofe.exe`

### Video Not Playing (No Error in Log)

**Solution:**
1. Check video file exists and path is correct
2. Try a different video format (mp4 recommended)
3. Check collection configuration for video path settings
4. Verify plugins directory was copied correctly

### Black Screen (retrofe.exe crashes immediately)

**Solution:**
1. Check for missing SDL2 DLLs (should already exist from previous builds)
2. Verify libVLC is 32-bit (x86), not 64-bit
3. Check log.txt for crash details

### SDL2 Runtime DLLs Required

If images don't display or you get missing DLL errors, ensure these are present:
```
SDL2.dll
SDL2_image.dll
SDL2_mixer.dll
SDL2_ttf.dll
libjpeg-9.dll
libpng16-16.dll
libtiff-5.dll
libwebp-7.dll
zlib1.dll
libfreetype-6.dll
```

These should be copied from `RetroFE\ThirdParty\SDL2*\lib\x86\`

### Performance Issues (Choppy Audio/Video)

**Problem:** All videos/audio playing simultaneously causing poor performance

**Solution:** The CORE Team's VLC implementation includes smart playback:
- Videos/audio with volume = 0 don't decode (no CPU usage)
- Only media with volume > 0.01 actually plays
- Layout controls playback through volume animations

Example layout.xml usage:
```xml
<video src="sounds/menu.mp3" volume="0">
    <onMenuEnter menuIndex="0">
        <animate type="volume" to="0.5"/>
    </onMenuEnter>
    <onMenuExit menuIndex="0">
        <animate type="volume" to="0"/>
    </onMenuExit>
</video>
```

## Reporting Issues

If you encounter issues:

1. Capture the full build output
2. Capture log.txt contents (especially lines with [ERROR] or [Video])
3. Note which step failed
4. Provide libVLC SDK version used

## Packaging for Distribution

The `Package.py` script has been updated to automatically include libVLC DLLs:

```powershell
python Scripts\Package.py --os=windows --build=full
```

This will create a complete RetroFE distribution at `Artifacts\windows\RetroFE\` with:
- retrofe.exe in `core\` folder
- libvlc.dll and libvlccore.dll in `core\` folder (automatically copied from build)
- plugins\ directory in `core\` folder (automatically copied from build)
- All layouts, collections, and configuration files

**End users receive a ready-to-run package:**
- No VLC installation required
- No manual DLL copying required
- Just extract and run RetroFE.exe

The build script automatically bundles all required DLLs during compilation, and Package.py copies them to the distribution package.

## Next Steps After Successful Testing

Once video playback is confirmed working:

1. Test with multiple video formats (mp4, avi, mkv, wmv)
2. Test video looping behavior
3. Test on your actual RetroFE setup (not just test build)
4. Performance comparison with GStreamer (if applicable)
5. Package with `Package.py` to verify distribution
6. Consider merging to master after validation

---

*Original VLC implementation by RFSVIEIRA*
*Current implementation and performance optimizations by the CORE Team*
*Building a better RetroFE experience*
