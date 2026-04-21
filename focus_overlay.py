import tkinter as tk
import time
import ctypes
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config_manager

def set_focus_mode_false():
    config = config_manager.load_config()
    config["focus_mode"] = False
    config_manager.save_config(config)

class FocusOverlay:
    def __init__(self):
        self.config = config_manager.load_config()
        self.lang = self.config.get("lang", "en")
        self.focus_text = "ENFOQUE 🙏 time" if self.lang == "es" else "FOCUS 🙏 time"
        
        self.root = tk.Tk()
        self.root.title("FocusOverlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")
        
        # Ensure it's rendered to get HWND
        self.root.update_idletasks()
        
        # Make the window click-through (WS_EX_LAYERED | WS_EX_TRANSPARENT)
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
                
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20
            WS_EX_TOOLWINDOW = 0x80
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW)
        except Exception as e:
            print("Failed to make click-through:", e)

        # Canvas for drawing text with a glow/outline since tk.Label doesn't support it natively
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        
        # Position at the bottom right. Taskbar clock is usually here.
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Estimate: width 320px, height 40px, positioned above the taskbar clock.
        self.root.geometry(f"320x40+{screen_width - 330}+{screen_height - 90}")

        self.time_left = 30 * 60
        self.update_timer()

    def update_timer(self):
        if len(sys.argv) > 1 and self.time_left % 5 == 0:
            try:
                parent_pid = int(sys.argv[1])
                SYNCHRONIZE = 0x00100000
                process_handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, parent_pid)
                if process_handle:
                    wait_res = ctypes.windll.kernel32.WaitForSingleObject(process_handle, 0)
                    ctypes.windll.kernel32.CloseHandle(process_handle)
                    if wait_res == 0:
                        self.root.destroy()
                        return
                else:
                    self.root.destroy()
                    return
            except Exception:
                pass

        if self.time_left <= 0:
            set_focus_mode_false()
            self.root.destroy()
            return
            
        m = self.time_left // 60
        s = self.time_left % 60
        text_str = f"{self.focus_text} {m}m {s:02d}s"
        
        self.canvas.delete("all")
        font = ("Segoe UI", 20, "bold")
        cx, cy = 160, 20
        
        # Draw 1px indigo outline (glow)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                self.canvas.create_text(cx + dx, cy + dy, text=text_str, font=font, fill="indigo")
                
        # Draw main purple text
        self.canvas.create_text(cx, cy, text=text_str, font=font, fill="#A020F0")
        
        self.time_left -= 1
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    overlay = FocusOverlay()
    overlay.root.mainloop()
