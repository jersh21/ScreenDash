import ctypes
import keyboard
import time
import sys
import os
import threading
import subprocess
import pystray
from PIL import Image, ImageDraw
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")
from ctypes import wintypes
from pynput import mouse
import config_manager

user32 = ctypes.windll.user32

# Constants for window manipulation
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
WM_CLOSE = 0x0010
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020
SC_MAXIMIZE = 0xF030
SC_RESTORE = 0xF120
SC_CLOSE = 0xF060

GWL_STYLE = -16
WS_MAXIMIZE_STYLE = 0x01000000

# GetAncestor constant
GA_ROOT = 2

# Monitor info constants
MONITOR_DEFAULTTONEAREST = 2

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', wintypes.LONG),
        ('top', wintypes.LONG),
        ('right', wintypes.LONG),
        ('bottom', wintypes.LONG)
    ]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', RECT),
        ('rcWork', RECT),
        ('dwFlags', wintypes.DWORD)
    ]

MonitorEnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)

def get_window_class(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value

def get_window_title_internal(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0: return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def get_window_under_cursor():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    hwnd = user32.WindowFromPoint(pt)
    if hwnd:
        root_hwnd = user32.GetAncestor(hwnd, GA_ROOT)
        target = root_hwnd if root_hwnd else hwnd
        
        # Protect critical Windows OS elements
        cls = get_window_class(target)
        if cls in ["Shell_TrayWnd", "NotifyIconOverflowWindow", "Progman", "WorkerW"]:
            return 0
        if get_window_title_internal(target) == "Program Manager":
            return 0
            
        return target
    return 0

def _move_window(position):
    hwnd = get_window_under_cursor()
    if not hwnd:
        return
    
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    if style & WS_MAXIMIZE_STYLE:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0)
        time.sleep(0.05)

    hmon = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    if not hmon:
        return
        
    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmon, ctypes.byref(monitor_info))
    
    work_area = monitor_info.rcWork
    
    if position == "right_top":
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        new_x = work_area.right - width
        new_y = work_area.top
        # SWP_NOSIZE = 0x0001, SWP_NOZORDER = 0x0004 => 0x0005
        user32.SetWindowPos(hwnd, 0, new_x, new_y, 0, 0, 0x0005)
    
    elif position == "left_half":
        width = (work_area.right - work_area.left) // 2
        height = work_area.bottom - work_area.top
        new_x = work_area.left
        new_y = work_area.top
        # SWP_NOZORDER = 0x0004
        user32.SetWindowPos(hwnd, 0, new_x, new_y, width, height, 0x0004)
        
    elif position == "right_half":
        width = (work_area.right - work_area.left) // 2
        height = work_area.bottom - work_area.top
        new_x = work_area.left + width
        new_y = work_area.top
        # SWP_NOZORDER = 0x0004
        user32.SetWindowPos(hwnd, 0, new_x, new_y, width, height, 0x0004)

def move_window_to_next_monitor():
    hwnd = get_window_under_cursor()
    if not hwnd:
        return
        
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    was_maximized = bool(style & WS_MAXIMIZE_STYLE)
    
    if was_maximized:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0)
        time.sleep(0.05)
        
    hmon_current = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    if not hmon_current:
        return

    monitors = []
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        monitors.append(hMonitor)
        return True
    
    cb = MonitorEnumProc(callback)
    user32.EnumDisplayMonitors(None, None, cb, 0)
    
    if len(monitors) <= 1:
        return
        
    try:
        idx = monitors.index(hmon_current)
    except ValueError:
        idx = 0
    next_hmon = monitors[(idx + 1) % len(monitors)]
    
    current_info = MONITORINFO()
    current_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmon_current, ctypes.byref(current_info))
    
    next_info = MONITORINFO()
    next_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(next_hmon, ctypes.byref(next_info))
    
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    # Calculate offset on current screen
    x_offset = rect.left - current_info.rcWork.left
    y_offset = rect.top - current_info.rcWork.top
    
    # Prevent exceeding next monitor's workspace
    nw = next_info.rcWork.right - next_info.rcWork.left
    nh = next_info.rcWork.bottom - next_info.rcWork.top
    width = min(width, nw)
    height = min(height, nh)
    
    new_x = next_info.rcWork.left + min(x_offset, nw - width)
    new_y = next_info.rcWork.top + min(max(0, y_offset), nh - height)
    
    # SWP_NOZORDER = 0x0004
    user32.SetWindowPos(hwnd, 0, new_x, new_y, width, height, 0x0004)
    
    if was_maximized:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)

def move_window_top_right():
    _move_window("right_top")

def minimize_window():
    hwnd = get_window_under_cursor()
    if hwnd:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)

def maximize_window():
    hwnd = get_window_under_cursor()
    if hwnd:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)

def close_window():
    hwnd = get_window_under_cursor()
    if hwnd:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

def restore_all_minimized():
    hwnds = []
    def callback(hwnd, ctx):
        if user32.IsIconic(hwnd) and user32.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True
    
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback)
    user32.EnumWindows(cb, 0)
    for hwnd in hwnds:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0)

def get_window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0: return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def is_main_window(hwnd):
    if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
        return False
    title = get_window_title(hwnd)
    if not title or title in ["Program Manager", "Settings", "FocusOverlay", "ScreenDash Settings", "Configuración de ScreenDash"]:
        return False
    # Exclude dialogs/popups owned by an existing main window
    if user32.GetWindow(hwnd, 4) != 0: 
        return False
    return True

def minimize_all_windows():
    hwnds = []
    def callback(hwnd, ctx):
        if is_main_window(hwnd):
            hwnds.append(hwnd)
        return True
    
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback)
    user32.EnumWindows(cb, 0)
    for hwnd in hwnds:
        user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)

def _do_mouse_click():
    time.sleep(0.05) # Give hook time to return
    for mod in ['ctrl', 'alt', 'shift', 'windows']:
        if keyboard.is_pressed(mod):
            try: keyboard.release(mod)
            except Exception: pass
                
    time.sleep(0.02)
    user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
    time.sleep(0.03)
    user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP

def mouse_click_action():
    threading.Thread(target=_do_mouse_click, daemon=True).start()

def _do_right_mouse_click():
    time.sleep(0.05)
    for mod in ['ctrl', 'alt', 'shift', 'windows']:
        if keyboard.is_pressed(mod):
            try: keyboard.release(mod)
            except Exception: pass
                
    time.sleep(0.02)
    user32.mouse_event(0x0008, 0, 0, 0, 0) # RIGHTDOWN
    time.sleep(0.03)
    user32.mouse_event(0x0010, 0, 0, 0, 0) # RIGHTUP

def right_mouse_click_action():
    threading.Thread(target=_do_right_mouse_click, daemon=True).start()

def gather_all_windows():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    hmon = user32.MonitorFromPoint(pt, 2)
    if not hmon: return
        
    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmon, ctypes.byref(monitor_info))
    
    work_area = monitor_info.rcWork
    target_x = work_area.left + 50
    target_y = work_area.top + 50
    
    hwnds = []
    def callback(hwnd, ctx):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = get_window_title(hwnd)
        if not title or title in ["Program Manager", "Settings", "FocusOverlay", "ScreenDash Settings", "Configuración de ScreenDash"]:
            return True
        if user32.GetWindow(hwnd, 4) != 0: 
            return True
        hwnds.append(hwnd)
        return True
    
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(callback)
    user32.EnumWindows(cb, 0)
    
    offset = 0
    for hwnd in hwnds:
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        if user32.IsIconic(hwnd) or (style & WS_MAXIMIZE_STYLE):
            user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_RESTORE, 0)
            time.sleep(0.01)
            
        user32.SetWindowPos(hwnd, 0, target_x + offset, target_y + offset, 0, 0, 0x0005)
        offset = (offset + 40) % 400

tray_icon = None
listener = None
G_CONFIG = config_manager.load_config()
LOCK_FILE = "recording.lock"

def quit_app(icon=None, item=None):
    global listener, tray_icon
    
    # Clean up lingering windows from subprocesses
    for title in ["ScreenDash Settings", "Configuración de ScreenDash"]:
        hwnd_settings = user32.FindWindowW(None, title)
        if hwnd_settings:
            user32.PostMessageW(hwnd_settings, WM_CLOSE, 0, 0)
        
    hwnd_focus = user32.FindWindowW(None, "FocusOverlay")
    if hwnd_focus:
        user32.PostMessageW(hwnd_focus, WM_CLOSE, 0, 0)
        
    if listener:
        listener.stop()
    if tray_icon:
        tray_icon.stop()
    os._exit(0)

# Mouse listener handling
def get_modifiers():
    mods = []
    # Use GetAsyncKeyState for real-time hardware state, bypassing keyboard hook state issues
    if user32.GetAsyncKeyState(0x11) & 0x8000:
        mods.append('ctrl')
    if user32.GetAsyncKeyState(0x12) & 0x8000:
        mods.append('alt')
    if user32.GetAsyncKeyState(0x10) & 0x8000:
        mods.append('shift')
    if (user32.GetAsyncKeyState(0x5B) & 0x8000) or (user32.GetAsyncKeyState(0x5C) & 0x8000):
        mods.append('windows')
    return mods

def exec_action(action_name):
    if os.path.exists(LOCK_FILE):
        return
    if not G_CONFIG.get("master_enable", True):
        return
    if not G_CONFIG.get("enabled", {}).get(action_name, True):
        return
    
    mapping = {
        "move_top_right": move_window_top_right,
        "alt_top_right": move_window_top_right,
        "move_to_next_monitor": move_window_to_next_monitor,
        "alt_next_monitor": move_window_to_next_monitor,
        "minimize_window": minimize_window,
        "alt_minimize": minimize_window,
        "maximize_window": maximize_window,
        "alt_maximize": maximize_window,
        "close_window": close_window,
        "alt_close": close_window,
        "restore_all_minimized": restore_all_minimized,
        "alt_restore": restore_all_minimized,
        "minimize_all": minimize_all_windows,
        "alt_minimize_all": minimize_all_windows,
        "move_left_half": lambda: _move_window("left_half"),
        "alt_move_left": lambda: _move_window("left_half"),
        "move_right_half": lambda: _move_window("right_half"),
        "alt_move_right": lambda: _move_window("right_half"),
        "gather_all_windows": gather_all_windows,
        "alt_gather_windows": gather_all_windows,
        "mouse_click": mouse_click_action,
        "alt_mouse_click": mouse_click_action,
        "right_mouse_click": right_mouse_click_action,
        "alt_right_mouse_click": right_mouse_click_action
    }
    if action_name in mapping:
        mapping[action_name]()

def check_mouse_hotkey(hotkey_str):
    for act, hk in G_CONFIG.get("hotkeys", {}).items():
        if hk == hotkey_str:
            exec_action(act)
            return True
    return False

def on_scroll(x, y, dx, dy):
    mods = get_modifiers()
    if dy > 0: dir_name = 'scroll_up'
    elif dy < 0: dir_name = 'scroll_down'
    elif dx > 0: dir_name = 'scroll_right'
    elif dx < 0: dir_name = 'scroll_left'
    else: return
    
    keys = mods + [dir_name]
    check_mouse_hotkey('+'.join(keys))

def on_click(x, y, button, pressed):
    if pressed:
        mods = get_modifiers()
        btn_name = str(button).replace('Button.', 'mouse_')
        keys = mods + [btn_name]
        check_mouse_hotkey('+'.join(keys))

def apply_hotkeys():
    try:
        keyboard.unhook_all_hotkeys()
    except AttributeError:
        pass
        
    if not G_CONFIG.get("master_enable", True):
        return
        
    hotkeys = G_CONFIG.get("hotkeys", {})
    enabled = G_CONFIG.get("enabled", {})
    
    for action, hk in hotkeys.items():
        if enabled.get(action, True) and hk:
            try:
                keyboard.add_hotkey(hk, lambda a=action: exec_action(a))
            except Exception:
                pass

def config_watcher(interval=1.0):
    global G_CONFIG
    focus_process = None
    last_mtime = 0
    if os.path.exists(config_manager.CONFIG_FILE):
        last_mtime = os.path.getmtime(config_manager.CONFIG_FILE)
        
    while True:
        time.sleep(interval)
        
        # Clean up process reference if it exited on its own (timer reached zero).
        if focus_process is not None:
            if focus_process.poll() is not None:
                focus_process = None
                
        if os.path.exists(config_manager.CONFIG_FILE):
            current_mtime = os.path.getmtime(config_manager.CONFIG_FILE)
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                G_CONFIG = config_manager.load_config()
                apply_hotkeys()
                
                focus_enabled = G_CONFIG.get("focus_mode", False)
                if focus_enabled and focus_process is None:
                    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "focus_overlay.py")
                    focus_process = subprocess.Popen([sys.executable, script_path, str(os.getpid())], creationflags=subprocess.CREATE_NO_WINDOW)
                elif not focus_enabled and focus_process is not None:
                    try:
                        focus_process.terminate()
                    except Exception:
                        pass
                    focus_process = None

def create_image():
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dash.ico')
    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path)
        except Exception:
            pass

    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(30, 30, 30))
    dc = ImageDraw.Draw(image)
    dc.rectangle([width//4, height//4, width*3//4, height*3//4], fill=(40, 150, 255)) # update to a blue shade
    return image

def launch_settings(icon, item):
    settings_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.py")
    subprocess.Popen([sys.executable, settings_script], shell=True)

def main():
    global listener, tray_icon
    
    # Force focus mode to be OFF on launch
    init_config = config_manager.load_config()
    if init_config.get("focus_mode", True):
        init_config["focus_mode"] = False
        config_manager.save_config(init_config)
    
    apply_hotkeys()
    
    listener = mouse.Listener(
        on_scroll=on_scroll,
        on_click=on_click)
    listener.start()

    watcher_thread = threading.Thread(target=config_watcher, daemon=True)
    watcher_thread.start()

    menu = pystray.Menu(
        pystray.MenuItem('Settings', launch_settings, default=True),
        pystray.MenuItem('Quit', quit_app)
    )
    tray_icon = pystray.Icon("ScreenDash", create_image(), "ScreenDash", menu)
    tray_icon.run()

if __name__ == "__main__":
    import ctypes
    myappid = 'screendash.windowmanager.v1'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    main()
