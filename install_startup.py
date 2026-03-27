import os
import sys
import subprocess

def create_startup_shortcut():
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, 'ScreenDash.lnk')
    
    # We assume app.py is in the same directory as this installer script
    app_path = os.path.abspath('app.py')
    
    # Locate pythonw.exe corresponding to current python executable
    pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
    if not os.path.exists(pythonw_path):
        print(f"Warning: Could not find {pythonw_path}. Trying fallback...")
        pythonw_path = "pythonw.exe"
    
    ps_script = f'''
$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut("{shortcut_path}")
$shortcut.TargetPath = "{pythonw_path}"
$shortcut.Arguments = '"{app_path}"'
$shortcut.WorkingDirectory = "{os.path.dirname(app_path)}"
$shortcut.Save()
'''
    result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Success! Startup shortcut created at: {shortcut_path}")
        print("ScreenDash will now automatically start in the background when you log in.")
    else:
        print(f"Error creating shortcut: {result.stderr}")

if __name__ == "__main__":
    create_startup_shortcut()
