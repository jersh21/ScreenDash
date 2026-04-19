# ScreenDash
<img width="1615" height="904" alt="image" src="https://github.com/user-attachments/assets/a2cc8bb6-112d-4fad-913a-5d394d0695b7" />
https://www.youtube.com/watch?v=Je2Sgmmo-jY&pp=0gcJCdkKAYcqIYzv
    ScreenDash is one of the lightest-weight system-tray applications for Windows of all time!

    Each feature comes with two sets of recordable hotkeys that can all be toggled.
** All features affect the window that the mouse is hovering over to save time and mouse clicks! Awesome!

**Absolutely Zero Networking:** The Python scripts (`app.py`, `settings.py`, etc.) do not use any internet or network libraries. It doesn't open any ports, host any server, or send any data anywhere.
    It directly hooks into the native Windows operating system API (via `ctypes.windll.user32`). All code and images generated locally and securely.

## Software Requirements
**IMPORTANT During PYTHON Installation make sure ADD TO PATH is checked (it should be on by default)**
- **Python 3.10** or higher 
- **pystray**: Creates the system tray icon so the app can run silently.
- **pynput**: Global mouse scrolling and middle-click events.
- **keyboard**: Global keyboard shortcut register.
- **Pillow**: Generating and loading the icon logo images.
- **customtkinter**: Builds the Settings window.

## Installation
1. Ensure Python 3.10+ is installed on your Windows machine.
2. Open your terminal or command prompt in this directory.
3. Install the required dependencies:
   ```bash
   pip install pystray pynput keyboard Pillow customtkinter
   ```
4. Double-click `app.py` or run `python app.py` to start the application. It will run quietly in your system tray!
5. *(Optional)* Run `python install_startup.py` if you want ScreenDash to automatically start every time you log into Windows.

## Uninstallation
1. **Stop the App**: Right-click the ScreenDash icon in your system tray and select "Quit".
2. **Remove from Startup**: If you installed the startup shortcut, press `Win + R`, type `shell:startup`, and press Enter. Delete the `ScreenDash.lnk` file inside.
3. **Delete Files**: Delete the entire folder and its configuration files.

## Features & Hotkeys
ScreenDash supports customizable hotkeys for the following features:
- Minimize / Maximize / Close window
- Minimize all windows
- Restore minimized windows
- Move window to left half / right half
- Move window to the next monitor
- Gather all windows (my favorite)
- Move window to top right

## Side note
    This app may not affect notoriously buggy applications like "WACUP", 
    and it may be unable to affect or act as normal with higher privalege apps open 
    like the "Windows Task Manager". This is by Microsoft's design called 
    User Interface Privilege Isolation (UIPI) system.
    For faster load times I run the app at login using Task Schedular. 
    (if you do this you may have to remove the app from the shell startup if you notice a duplicate).
   
## Developer Notes & Changelog

**Latest Fixes:** Last updated 2026-04-18
- Added background-image feature.
- Improved close window reliability.
- Added Left-click and Right-click features, but they are a little buggy.
- Fixed a key press bug that made the app believe the alt key was being held down while it is not.
- Update: Now utilizing WM_SYSCOMMAND messages (specifically SC_MINIMIZE, WM_CLOSE, SC_RESTORE, and SC_MAXIMIZE) for a broader scope of window management.
- Bug fix: ScreenDash wasn't closing properly in Spanish mode due to a change in the title of the Settings window. updated quit_app() function to fix it.
- Added language toggle feature (English / Spanish).
- Added focus timer.
- Improved Quit behavior.
- Improved UI.
- Bug fix (internal EnumWindows loop error). Fixed by gathering all the window IDs first then sequencing through them.
- Added minimize all feature.
- Added ALREADY_EXISTS to prevent multiple instances of settings windows.
- Ensured all hotkeys are unhooked when the `master_enable` state transitions to `False`.
- Fixed `exec_action()` function where the `action_name` variable was not being passed correctly.
- Resolved an issue with `get_window_under_cursor` where Windows taskbar elements (`Shell_TrayWnd`, `NotifyIconOverflowWindow`, `Progman`, `WorkerW`) would accidentally get minimized or disappear.
- Added "Gather All Windows" button to the settings window.
- Added re-organize hotkeys feature.
- Fixed the hotkey recording function by disabling the listening of hotkeys prior to recording a new one.
- Added a master toggle to entirely disable the app's hotkeys.
- Wrapped the startup `keyboard.unhook_all_hotkeys()` call in a try-except block to fix an `AttributeError` from missing config files.
- Added a `default=True` flag to the Settings menu item in `app.py` so a left-click (or double-click) on the tray icon pops open the Settings window immediately.
- Implemented `recording.lock` for accurate keyboard/mouse shortcut recording.
- Renamed application to ScreenDash.

**Future Thoughts:**
- I thought to automatically show ScreenDash in the system tray, but Microsoft doesn't allow apps to do that I found out!
- Explore using `DwmGetWindowAttribute` with `DWMWA_EXTENDED_FRAME_BOUNDS` instead of `GetWindowRect`. The standard `GetWindowRect` often includes invisible "drop shadows", whereas DWM bounds give the visible frame. (Actual Width = Right - Left - Invisible Shadow Padding).
- Considered adding a "BOSS MODE" window hiding feature or "Always on Top" toggle. Note: could cause annoying bugs so deciding not to do it here.

