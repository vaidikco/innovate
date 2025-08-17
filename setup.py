import os
import subprocess
import sys
import time
import shutil
from colorama import Fore, Style, init
import fade

init(autoreset=True)

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", package])

def print_section_title(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}\n{'-' * len(text)}")

def create_start_menu_shortcut(exe_path, shortcut_name="Innovate CLI"):
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        install("pywin32")
        import pythoncom
        import win32com.client

    start_menu_path = os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs")
    shortcut_path = os.path.join(start_menu_path, f"{shortcut_name}.lnk")

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.save()
        print(Fore.GREEN + f"Start Menu shortcut created: {shortcut_path}")
    except Exception as e:
        print(Fore.RED + f"Failed to create Start Menu shortcut: {e}")

def add_to_path(directory):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
            try:
                existing_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                existing_path = ""
        if directory.lower() in existing_path.lower():
            print(Fore.YELLOW + "Directory already in PATH.")
        else:
            new_path = existing_path + ";" + directory if existing_path else directory
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(Fore.GREEN + f"Added to PATH: {directory}")
            print(Fore.YELLOW + "You may need to restart terminal or log out/in for it to take effect.")
    except Exception as e:
        print(Fore.RED + "Failed to update PATH:", e)

def main():
    splash = fade.purplepink("""
 INSTALLATION FOR INNOVATE ClI
                                                      
        """)
    print(splash)
    print(Fore.LIGHTWHITE_EX + "Innovate CLI Environment Setup\n")

    # Step 1: Install dependencies
    print_section_title("Installing dependencies")
    for pkg in ["google-genai", "fade", "python-dotenv", "colorama", "pywin32"]:
        install(pkg)
    print(Fore.GREEN + "All dependencies installed successfully.")
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")

    # Step 2: Get Gemini API Key
    print_section_title("Gemini API Configuration")
    print("Get your Gemini API key from:")
    print("https://makersuite.google.com/app or Google Cloud Console\n")
    api_key = input("Enter your Gemini API Key: ").strip()
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    print(Fore.GREEN + ".env file created successfully.")

    # Step 3: Install to C:\innovate
    print_section_title("Installing to C:\\innovate")
    install_path = "C:\\innovate"
    current_path = os.getcwd()
    try:
        if not os.path.exists(install_path):
            shutil.copytree(current_path, install_path)
            print(Fore.GREEN + f"Copied to {install_path}")
        else:
            print(Fore.YELLOW + f"{install_path} already exists. Skipping copy.")
    except Exception as e:
        print(Fore.RED + "Failed to copy directory:", e)
        return

    # Step 4: Add to PATH
    print_section_title("PATH Configuration")
    add_to_path(install_path)

    # Step 5: Create Start Menu Shortcut
    print_section_title("Creating Start Menu Shortcut")
    exe_path = os.path.join(install_path, "innovate.exe")
    create_start_menu_shortcut(exe_path)

    # Final
    print_section_title("Setup Complete")
    print(Fore.LIGHTGREEN_EX + "Innovate CLI installed successfully.")
    print("You can now launch it by typing:")
    print(Fore.CYAN + "innovate" + Fore.LIGHTWHITE_EX + " in CMD or by searching in Start Menu.")
    input(Fore.LIGHTBLACK_EX + "\nPress Enter to exit...")

if __name__ == "__main__":
    main()
