# ScreenDash

This app allows using dynamic hotkey registration to make window management incredibly fast and easy. Once launched, it simply runs in your background system tray. All code and images were created securely and locally.
app.py relies heavily on ctypes.windll.user32. We are directly talking to the native Windows operating system API to grab window coordinates, calculate monitor bounds, and snap them.

**Absolutely Zero Networking:** The Python scripts
(`app.py`, `settings.py`, etc.) do not use any internet or network libraries. 
It doesn't open any ports, host any server, or send any data anywhere.

## Software Requirements:
- Python 3.10 or higher
- pystray (creates the system tray icon so the app can run silently)
- pynput (detects global mouse scrolling and middle-click events)
- keyboard (listens for and registers your global keyboard shortcuts)
- Pillow (powers generating and loading the icon logo images)
- customtkinter (builds the modern dark-themed Settings window)

## How to Install:
1. Make sure Python 3.10+ is installed on your Windows machine.
2. Open your terminal or command prompt in this directory.
3. Install the required dependencies by running:
   `pip install pystray pynput keyboard Pillow customtkinter`
4. Double-click `app.py` or run `python app.py` to start the application. It will run quietly in your system tray!
5. (Optional) Run `python install_startup.py` if you want ScreenDash to automatically start every time you log into Windows!

##How to Uninstall:
1. **Stop the App**: Right-click the ScreenDash icon in your system tray and select "Quit".
2. **Remove from Startup**: If you installed the startup shortcut, press `Win + R`, type `shell:startup`, and press Enter. Delete the `ScreenDash.lnk` file inside.
3. **Delete Files**: You can now safely delete the entire `window_manager` folder and its configuration files.

3/26/2026 hotkeys, move top right move to next monitor, minimize window, max window, close window, restore minimized windows, move left half, move right half

Latest fixes:
-ensuring all hotkeys are unhooked when the master_enable state transitions to 'False'.
-bug: exec_action() function not working. Variable action_name was not being passed correctly.
-bug fix: get_window_under_cursor had funky results with the system tray handle and minimize hotkey.
- Windows taskbar (Shell_TrayWnd) and system tray popup (NotifyIconOverflowWindow) would literally minimize Windows
- Explorer's core UI elements, causing them to disappear completely.
-if cls in ["Shell_TrayWnd", "NotifyIconOverflowWindow", "Progman", "WorkerW"]: return 0
-added Gather All Windows button to the settings window.
-adding ability to re-organize the hotkeys in the settings window.
-Fixed record function by disabled listening of hotkeys prior to recording a new hotkey.
-added master toggle to disable the app's hotkeys.
-bug fix: keyboard library calling keyboard.unhook_all_hotkeys() at startup was returning 
-Added default=True flag to the Settings menu item in app.py  left-click (or double-click, depending on your Windows taskbar settings) right on the icon itself and the ScreenDash Settings window will pop open immediately, no context menu required!
-Added hotkey recording.lock for accurate keyboard/mouse shortcut recording.
-Renamed App to ScreenDash.
-Fixed an issue where the app would not start up because the config file was missing.
AttributeError. Fixed by wrapping the call in a try-except block.

# future thoughts
GetWindowRect vs. DwmGetWindowAttribute. The standard GetWindowRect often includes invisible "drop shadows" in its calculations. Using DWMWA_EXTENDED_FRAME_BOUNDS gives you the frame the user actually sees. Actual Width = Right - Left - Invisible Shadow Padding.

# Thought of adding BOSS MODE (window hiding feature) , and the (Always on Top toggle feature), but both might introduce bugs (especially the BOSS Mode).

