# ScreenDash
<img width="1078" height="943" alt="image" src="https://github.com/user-attachments/assets/0390de15-fc40-48b4-9ce8-bd94695db7ab" />



ScreenDash is a lightweight system-tray application for Windows that enables dynamic hotkey registration to make window management incredibly fast and easy. 

It directly hooks into the native Windows operating system API (via `ctypes.windll.user32`) to grab window coordinates, calculate monitor bounds, and snap them cleanly. All code and image assets operate securely and locally.

**Absolutely Zero Networking:** The Python scripts (`app.py`, `settings.py`, etc.) do not use any internet or network libraries. It doesn't open any ports, host any server, or send any data anywhere.

## Software Requirements
** IMPORTANT During PYTHON Installation make sure ADD TO PATH is checked (it should be on by default) **
- **Python 3.10** or higher 
- **pystray**: Creates the system tray icon so the app can run silently.
- **pynput**: Detects global mouse scrolling and middle-click events.
- **keyboard**: Listens for and registers your global keyboard shortcuts.
- **Pillow**: Powers generating and loading the icon logo images.
- **customtkinter**: Builds the modern dark-themed Settings window.

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
3. **Delete Files**: You can now safely delete the entire folder and its configuration files.

## Features & Hotkeys
ScreenDash supports customizable hotkeys for the following actions:
- Move window to top right
- Move window to next monitor
- Minimize / Maximize / Close window
- Minimize all windows
- Restore minimized windows
- Move window to left half / right half
- Gather all windows 

---

## Developer Notes & Changelog

**Latest Fixes:** Last updated 2026-03-28
- Added focus mode toggle feature with 30 minute unminimizable timer. Timer turns off within 5 seconds of app close since it will inherit a unique Process ID from ScreenDash.
- Improved Quit behavior.
- Increased font size. Reduced Record button's margins. Increased hotkey input's width. Added shortcut 1 and 2 text at the top for clarity.
- Bug fix  internal EnumWindows loop error. Fixed by gathering all the window IDs first then sequencing through them.
- Added minimize all feature.
- Ensure new features are added to config.json and settings.py codebase in order to work.
- Added ALREADY_EXISTS to prevent multiple instances of settings windows.
- Ensured all hotkeys are unhooked when the `master_enable` state transitions to `False`.
- Fixed `exec_action()` function where the `action_name` variable was not being passed correctly.
- Resolved an issue with `get_window_under_cursor` where Windows taskbar elements (`Shell_TrayWnd`, `NotifyIconOverflowWindow`, `Progman`, `WorkerW`) would accidentally get minimized or disappear.
- Added "Gather All Windows" button to the settings window.
- Added ability to re-organize hotkeys in the settings window.
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

