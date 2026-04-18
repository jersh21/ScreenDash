import customtkinter as ctk
import config_manager
from tkinter import messagebox
import keyboard
import os
import sys
import threading
from pynput import mouse

# Ensure working directory is set to file's directory so it finds config properly if launched from elsewhere
os.chdir(os.path.dirname(os.path.abspath(__file__)))

LOCK_FILE = "recording.lock"

ES_DICT = {
    "ScreenDash Settings": "Configuración de ScreenDash",
    "Enable ScreenDash": "Habilitar ScreenDash",
    "Enable Focus Mode (30m)": "Habilitar Modo de Enfoque (30m)",
    "Windows Hotkey Configuration": "Configuración de Teclas Rápidas de Windows",
    "Hotkey 1": "Tecla 1",
    "Hotkey 2": "Tecla 2",
    "Record": "Grabar",
    "Listening...": "Escuchando...",
    "e.g. ctrl+shift+a": "ej. ctrl+shift+a",
    "Alternate / Mouse Actions": "Acciones de Ratón / Alternativas",
    "APPLY": "APLICAR",
    "Close": "Cerrar",
    "Note: Click 'Record' to bind standard keyboard or mouse combinations.": "Nota: Haga clic en 'Grabar' para vincular combinaciones de teclado o ratón.",
    "Mouse button BACK and FORWARD can be buggy as hotkeys.": "Los botones ATRÁS y ADELANTE del ratón pueden tener errores como atajos.",
    "Saved Dash": "Dash Guardado",
    "Move Top Right": "Mover Arriba a la Derecha",
    "Move to Next Monitor": "Mover al Siguiente Monitor",
    "Minimize Window": "Minimizar Ventana",
    "Maximize Window": "Maximizar Ventana",
    "Close Window": "Cerrar Ventana",
    "Restore Minimized Windows": "Restaurar Ventanas Minimizadas",
    "Minimize All Windows": "Minimizar Todas las Ventanas",
    "Move Left Half": "Mover Mitad Izquierda",
    "Move Right Half": "Mover Mitad Derecha",
    "Gather All Windows": "Reunir Todas las Ventanas",
    "Mouse Click": "Clic del Ratón",
    "Right Mouse Click": "Clic Derecho del Ratón"
}

CURRENT_LANG = "en"

def tr(text):
    if CURRENT_LANG == "es":
        return ES_DICT.get(text, text)
    return text

class HotkeyRecorder:
    def __init__(self, callback):
        self.callback = callback
        self.mouse_listener = None
        self.keyboard_hook = None
        self.finished = False

    def start(self):
        # Create lock file to suspend app.py hotkeys
        with open(LOCK_FILE, "w") as f:
            f.write("recording")
            
        self.keyboard_hook = keyboard.hook(self.on_keyboard)
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
        self.mouse_listener.start()

    def stop(self):
        if self.keyboard_hook:
            keyboard.unhook(self.keyboard_hook)
            self.keyboard_hook = None
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        # Remove lock
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except OSError:
                pass

    def finish(self, hotkey_str):
        if self.finished: return
        self.finished = True
        self.stop()
        self.callback(hotkey_str)

    def get_modifiers(self):
        mods = []
        for m in ['ctrl', 'alt', 'shift', 'windows']:
            if keyboard.is_pressed(m):
                mods.append(m)
        return mods

    def on_keyboard(self, event):
        if event.event_type == keyboard.KEY_UP:
            return
        if event.name in ['ctrl', 'alt', 'shift', 'windows', 'left ctrl', 'right ctrl', 'left alt', 'right alt', 'left shift', 'right shift', 'left windows', 'right windows']:
            return
            
        mods = self.get_modifiers()
        keys = mods + [event.name]
        self.finish('+'.join(keys))

    def on_click(self, x, y, button, pressed):
        if not pressed: return
        mods = self.get_modifiers()
        btn_name = str(button).replace('Button.', 'mouse_')
        if not mods and btn_name in ['mouse_left', 'mouse_right']:
            return
            
        keys = mods + [btn_name]
        self.finish('+'.join(keys))

    def on_scroll(self, x, y, dx, dy):
        mods = self.get_modifiers()
        if dy > 0: dir_name = 'scroll_up'
        elif dy < 0: dir_name = 'scroll_down'
        elif dx > 0: dir_name = 'scroll_right'
        elif dx < 0: dir_name = 'scroll_left'
        else: return
        
        keys = mods + [dir_name]
        self.finish('+'.join(keys))

class DualHotkeyEntry(ctk.CTkFrame):
    def __init__(self, master, label_text, val1, en1, val2, en2, on_up=None, on_down=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(8, weight=1)
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=0, padx=(5, 0), pady=5)
        
        self.up_btn = ctk.CTkButton(
            self.btn_frame, text="▲", width=20, height=20, font=ctk.CTkFont(size=10), command=on_up,
            fg_color="white", text_color="#1F6AA5", hover_color="gray90"
        )
        self.up_btn.pack(pady=(0, 2))
        
        self.down_btn = ctk.CTkButton(
            self.btn_frame, text="▼", width=20, height=20, font=ctk.CTkFont(size=10), command=on_down,
            fg_color="white", text_color="#1F6AA5", hover_color="gray90"
        )
        self.down_btn.pack()
        
        # Label
        self.label = ctk.CTkLabel(self, text=label_text, width=170, anchor="w", font=ctk.CTkFont(weight="bold"))
        self.label.grid(row=0, column=1, padx=10, pady=10)
        
        # Hotkey 1 Checkbox
        self.checkbox1 = ctk.CTkCheckBox(self, text="", width=20, onvalue=True, offvalue=False)
        self.checkbox1.grid(row=0, column=2, padx=(10, 5), pady=10)
        if en1:
            self.checkbox1.select()
        else:
            self.checkbox1.deselect()
        
        # Hotkey 1 Entry
        self.entry1 = ctk.CTkEntry(self, placeholder_text=tr("e.g. ctrl+shift+a"), width=180)
        self.entry1.insert(0, val1.upper())
        self.entry1.grid(row=0, column=3, sticky="ew", padx=10, pady=10)
        
        # Hotkey 1 Record
        self.record_btn1 = ctk.CTkButton(self, text=tr("Record"), width=60, command=lambda: self.start_recording(1))
        self.record_btn1.grid(row=0, column=4, padx=(5, 10), pady=10)
        
        # Splitter / Separator visual 
        self.sep = ctk.CTkFrame(self, width=2, height=20, fg_color="gray50")
        self.sep.grid(row=0, column=5, padx=10, pady=10)

        # Hotkey 2 Checkbox
        self.checkbox2 = ctk.CTkCheckBox(self, text="", width=20, onvalue=True, offvalue=False)
        self.checkbox2.grid(row=0, column=6, padx=(10, 5), pady=10)
        if en2:
            self.checkbox2.select()
        else:
            self.checkbox2.deselect()
        
        # Hotkey 2 Entry
        self.entry2 = ctk.CTkEntry(self, placeholder_text=tr("Alternate / Mouse Actions"), width=180)
        self.entry2.insert(0, val2.upper())
        self.entry2.grid(row=0, column=7, sticky="ew", padx=10, pady=10)
        
        # Hotkey 2 Record
        self.record_btn2 = ctk.CTkButton(self, text=tr("Record"), width=60, command=lambda: self.start_recording(2))
        self.record_btn2.grid(row=0, column=8, padx=(5, 10), pady=10)
        
        self.recorder = None

    def start_recording(self, idx):
        btn = self.record_btn1 if idx == 1 else self.record_btn2
        btn.configure(text=tr("Listening..."), state="disabled")
        
        def on_rec(hotkey_str, i=idx):
            self.after(0, self._update_entry, hotkey_str, i)
            
        self.recorder = HotkeyRecorder(on_rec)
        threading.Thread(target=self.recorder.start, daemon=True).start()

    def _update_entry(self, hotkey_str, idx):
        entry = self.entry1 if idx == 1 else self.entry2
        btn = self.record_btn1 if idx == 1 else self.record_btn2
        
        entry.delete(0, 'end')
        entry.insert(0, hotkey_str.upper())
        btn.configure(text=tr("Record"), state="normal")
        self.recorder = None

    def get_values(self):
        return (self.entry1.get().lower(), bool(self.checkbox1.get()), self.entry2.get().lower(), bool(self.checkbox2.get()))

class SettingsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(tr("ScreenDash Settings"))
        self.geometry("1000x880")
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dash.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        # High quality built-in dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.config = config_manager.load_config()
        self.hotkeys = self.config.get("hotkeys", {})
        self.enabled = self.config.get("enabled", {})
        
        global CURRENT_LANG
        CURRENT_LANG = self.config.get("lang", "en")
        
        self.entries = {}
        
        self.top_switches_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_switches_frame.pack(fill="x", padx=30, pady=(15, 5))
        
        self.master_enable_var = ctk.BooleanVar(value=self.config.get("master_enable", True))
        self.master_switch = ctk.CTkSwitch(
            self.top_switches_frame, 
            text=tr("Enable ScreenDash"), 
            variable=self.master_enable_var,
            font=ctk.CTkFont(weight="bold", size=28),
            switch_width=72,
            switch_height=36,
            progress_color="#28a745", # visually matches a nice green iOS toggle
            command=self.on_master_toggle
        )
        self.master_switch.pack(side="left", padx=10)
        
        self.master_focus_var = ctk.BooleanVar(value=self.config.get("focus_mode", False))
        self.master_focus_switch = ctk.CTkSwitch(
            self.top_switches_frame, 
            text=tr("Enable Focus Mode (30m)"), 
            variable=self.master_focus_var,
            font=ctk.CTkFont(weight="bold", size=16),
            switch_width=44,
            switch_height=22,
            progress_color="#28a745", 
            command=self.on_focus_toggle
        )
        self.master_focus_switch.pack(side="left", padx=20)
        
        self.lang_var = ctk.StringVar(value=CURRENT_LANG)
        self.lang_switch = ctk.CTkSwitch(
            self.top_switches_frame, text="EN / ES", variable=self.lang_var, onvalue="es", offvalue="en",
            font=ctk.CTkFont(weight="bold", size=14), switch_width=36, switch_height=18,
            progress_color="#3B8ED0", command=self.on_lang_toggle
        )
        self.lang_switch.pack(side="right", padx=10)
        
        self.title_label = ctk.CTkLabel(self, text=tr("Windows Hotkey Configuration"), font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.pack(pady=(0, 15))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Dual bindings definitions (DisplayName, Key1, Key2, Default1, Default2)
        default_mapping = [
            ("Move Top Right", "move_top_right", "alt_top_right", "ctrl+shift+right", "alt+mouse_right"),
            ("Move to Next Monitor", "move_to_next_monitor", "alt_next_monitor", "ctrl+shift+z", "ctrl+alt+mouse_middle"),
            ("Minimize Window", "minimize_window", "alt_minimize", "ctrl+shift+down", "alt+scroll_down"),
            ("Maximize Window", "maximize_window", "alt_maximize", "ctrl+shift+up", "alt+scroll_up"),
            ("Close Window", "close_window", "alt_close", "ctrl+shift+x", "alt+mouse_middle"),
            ("Restore Minimized Windows", "restore_all_minimized", "alt_restore", "ctrl+shift+r", "ctrl+alt+scroll_up"),
            ("Minimize All Windows", "minimize_all", "alt_minimize_all", "ctrl+shift+m", "ctrl+alt+scroll_down"),
            ("Move Left Half", "move_left_half", "alt_move_left", "ctrl+windows+left", "alt+scroll_left"),
            ("Move Right Half", "move_right_half", "alt_move_right", "ctrl+windows+right", "alt+scroll_right"),
            ("Gather All Windows", "gather_all_windows", "alt_gather_windows", "ctrl+shift+g", "ctrl+alt+g"),
            ("Mouse Click", "mouse_click", "alt_mouse_click", "", ""),
            ("Right Mouse Click", "right_mouse_click", "alt_right_mouse_click", "", "")
        ]
        
        # Construct exact order
        saved_order = self.config.get("order", [])
        map_dict = { m[1]: m for m in default_mapping }
        self.active_mapping = []
        for k in saved_order:
            if k in map_dict:
                self.active_mapping.append(map_dict[k])
                del map_dict[k]
        for m in default_mapping:
            if m[1] in map_dict:
                self.active_mapping.append(m)
                
        self.row_frames = []
        self.render_rows()
            
        self.btn_frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame_bottom.pack(pady=(5, 10))
        
        self.save_btn = ctk.CTkButton(self.btn_frame_bottom, text=tr("APPLY"), command=self.save_config, height=40, width=120, font=ctk.CTkFont(size=14, weight="bold"))
        self.save_btn.pack(side="left", padx=10)
        
        self.close_btn = ctk.CTkButton(self.btn_frame_bottom, text=tr("Close"), command=self.on_closing, height=40, width=120, font=ctk.CTkFont(size=14, weight="bold"), fg_color="gray40", hover_color="gray30")
        self.close_btn.pack(side="left", padx=10)
        
        self.labels_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.labels_frame.pack(pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(self.labels_frame, text=tr("Note: Click 'Record' to bind standard keyboard or mouse combinations."), text_color="lightgray")
        self.info_label.pack(side="left", padx=(0, 5))
        
        self.warning_label = ctk.CTkLabel(self.labels_frame, text=tr("Mouse button BACK and FORWARD can be buggy as hotkeys."), text_color="#FF5A5A")
        self.warning_label.pack(side="left")
        
        # Clean up lock file if window is closed during recording
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply initial visual colors to match current master toggle state
        self.update_colors(self.master_enable_var.get())
        self.update_focus_colors(self.master_focus_var.get())

    def render_rows(self):
        for frame in self.row_frames:
            k1, k2 = frame.mapping_keys
            v1, e1, v2, e2 = frame.get_values()
            self.hotkeys[k1], self.enabled[k1] = v1, e1
            self.hotkeys[k2], self.enabled[k2] = v2, e2
            frame.destroy()
            
        if hasattr(self, 'header_row') and self.header_row:
            self.header_row.destroy()
            
        self.row_frames = []
        
        self.header_row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.header_row.pack(fill="x", pady=(0, 5), padx=5)
        self.header_row.grid_columnconfigure(4, weight=1)
        self.header_row.grid_columnconfigure(8, weight=1)
        
        ctk.CTkFrame(self.header_row, width=20, height=0, fg_color="transparent").grid(row=0, column=0, padx=(5,0))
        ctk.CTkLabel(self.header_row, text="", width=170).grid(row=0, column=1, padx=10)
        ctk.CTkFrame(self.header_row, width=20, height=0, fg_color="transparent").grid(row=0, column=2, padx=(10,5))
        
        l1 = ctk.CTkLabel(self.header_row, text=tr("Hotkey 1"), font=ctk.CTkFont(weight="bold", size=14), text_color="gray70")
        l1.grid(row=0, column=3, sticky="w", padx=10)
        
        ctk.CTkFrame(self.header_row, width=2, height=0, fg_color="transparent").grid(row=0, column=5, padx=10)
        ctk.CTkFrame(self.header_row, width=20, height=0, fg_color="transparent").grid(row=0, column=6, padx=(10,5))
        
        l2 = ctk.CTkLabel(self.header_row, text=tr("Hotkey 2"), font=ctk.CTkFont(weight="bold", size=14), text_color="gray70")
        l2.grid(row=0, column=7, sticky="w", padx=10)
        
        
        for idx, (name, key1, key2, def1, def2) in enumerate(self.active_mapping):
            val1 = self.hotkeys.get(key1, "")
            if not val1: val1 = def1
            en1 = self.enabled.get(key1, True)
            
            val2 = self.hotkeys.get(key2, "")
            if not val2: val2 = def2
            en2 = self.enabled.get(key2, True)
            
            bg_color = "transparent" if idx % 2 == 0 else ("gray85", "gray24")
            
            def make_cb(i, d): return lambda i=i, d=d: self.move_row(i, d)

            entry = DualHotkeyEntry(
                self.scroll_frame, tr(name), val1, en1, val2, en2, 
                on_up=make_cb(idx, -1), on_down=make_cb(idx, 1),
                fg_color=bg_color, corner_radius=6
            )
            
            if idx == 0:
                entry.up_btn.configure(state="disabled", fg_color="transparent", text_color="gray30")
            if idx == len(self.active_mapping) - 1:
                entry.down_btn.configure(state="disabled", fg_color="transparent", text_color="gray30")
                
            entry.pack(fill="x", pady=4, padx=5)
            entry.mapping_keys = (key1, key2)
            self.row_frames.append(entry)

    def move_row(self, idx, direction):
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.active_mapping):
            return
            
        self.active_mapping[idx], self.active_mapping[new_idx] = self.active_mapping[new_idx], self.active_mapping[idx]
        self.render_rows()
        self.update_colors(self.master_enable_var.get())

    def update_colors(self, is_enabled):
        if is_enabled:
            self.master_switch.configure(button_color="#FFFFFF", button_hover_color="#E0E0E0")
            cb_fg, cb_hover = ["#3B8ED0", "#1F6AA5"], ["#36719F", "#144870"]
        else:
            self.master_switch.configure(button_color="#FF5A5A", button_hover_color="#FF7F7F")
            cb_fg, cb_hover = "#FF5A5A", "#FF7F7F"
            
        for frame in self.row_frames:
            frame.checkbox1.configure(bg_color="transparent", fg_color=cb_fg, hover_color=cb_hover)
            frame.checkbox2.configure(bg_color="transparent", fg_color=cb_fg, hover_color=cb_hover)

    def update_static_translations(self):
        self.title(tr("ScreenDash Settings"))
        self.master_switch.configure(text=tr("Enable ScreenDash"))
        self.master_focus_switch.configure(text=tr("Enable Focus Mode (30m)"))
        self.title_label.configure(text=tr("Windows Hotkey Configuration"))
        self.save_btn.configure(text=tr("APPLY"))
        self.close_btn.configure(text=tr("Close"))
        self.info_label.configure(text=tr("Note: Click 'Record' to bind standard keyboard or mouse combinations."))
        self.warning_label.configure(text=tr("Mouse button BACK and FORWARD can be buggy as hotkeys."))

    def on_lang_toggle(self):
        global CURRENT_LANG
        CURRENT_LANG = self.lang_var.get()
        self.config["lang"] = CURRENT_LANG
        config_manager.save_config(self.config)
        self.update_static_translations()
        self.render_rows()

    def update_focus_colors(self, is_focused):
        if is_focused:
            self.master_focus_switch.configure(button_color="#FFFFFF", button_hover_color="#E0E0E0")
        else:
            self.master_focus_switch.configure(button_color="#FF5A5A", button_hover_color="#FF7F7F")

    def on_focus_toggle(self):
        is_focused = self.master_focus_var.get()
        self.config["focus_mode"] = is_focused
        config_manager.save_config(self.config)
        self.update_focus_colors(is_focused)

    def on_master_toggle(self):
        is_enabled = self.master_enable_var.get()
        self.config["master_enable"] = is_enabled
        
        order = []
        for frame in self.row_frames:
            key1, key2 = frame.mapping_keys
            val1, en1, val2, en2 = frame.get_values()
            
            self.hotkeys[key1], self.enabled[key1] = val1.strip(), en1
            self.hotkeys[key2], self.enabled[key2] = val2.strip(), en2
            
            order.append(key1)
            
        self.config["hotkeys"] = self.hotkeys
        self.config["enabled"] = self.enabled
        self.config["order"] = order
        
        config_manager.save_config(self.config)
        self.update_colors(is_enabled)

    def save_config(self):
        order = []
        for frame in self.row_frames:
            key1, key2 = frame.mapping_keys
            val1, en1, val2, en2 = frame.get_values()
            
            self.hotkeys[key1], self.enabled[key1] = val1.strip(), en1
            self.hotkeys[key2], self.enabled[key2] = val2.strip(), en2
            
            order.append(key1)
        
        self.config["hotkeys"] = self.hotkeys
        self.config["enabled"] = self.enabled
        self.config["order"] = order
        config_manager.save_config(self.config)
        
        # Create a non-blocking toast popup
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        # Position at the bottom right corner
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        toast.geometry(f"160x50+{screen_width - 200}+{screen_height - 120}")
        
        lbl = ctk.CTkLabel(toast, text=tr("Saved Dash"), font=ctk.CTkFont(size=16, weight="bold"), fg_color="#2ba64e", text_color="white", corner_radius=8)
        lbl.pack(expand=True, fill="both")
        
        # Close only the toast popup after 2 seconds
        self.after(2000, toast.destroy)
        
    def on_closing(self):
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except OSError:
                pass
        self.destroy()

if __name__ == "__main__":
    import ctypes
    
    mutex_name = "Local\\ScreenDashSettingsMutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "ScreenDash Settings") or user32.FindWindowW(None, "Configuración de ScreenDash")
        if hwnd:
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    myappid = 'screendash.windowmanager.v1'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    app = SettingsApp()
    app.mainloop()
