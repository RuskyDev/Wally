import requests
import os
import time
import ctypes
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import messagebox
import json
import pystray
import PIL.Image
import threading

image = PIL.Image.open("icon-png.png")

def set_wallpaper(api_key):
    endpoint = 'https://api.unsplash.com/photos/random'
    params = {'client_id': api_key, 'query': 'wallpaper'}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        image_url = data['urls']['full']
        image_data = requests.get(image_url).content
        wallpaper_path = os.path.join(os.path.expanduser("~"), "AppData\\Local\\Temp\\wallpaper.jpg")
        with open(wallpaper_path, 'wb') as f:
            f.write(image_data)
        SPI_SETDESKWALLPAPER = 0x0014
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)
    else:
        write_error_to_log('Failed to retrieve a wallpaper from Unsplash.')

def write_error_to_log(error_message):
    appdata_dir = os.path.join(os.getenv('APPDATA'), 'Wally')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)
    log_file = os.path.join(appdata_dir, 'logs.txt')
    with open(log_file, 'a') as file:
        file.write('[Error]: ' + error_message + '\n')

def save_api_key(api_key):
    if not is_valid_api_key(api_key):
        messagebox.showerror("Error", "Invalid API Key. Please check and try again.")
        os._exit(0)
    appdata_dir = os.path.join(os.getenv('APPDATA'), 'Wally')
    if not os.path.exists(appdata_dir):
        os.makedirs(appdata_dir)
    settings_file = os.path.join(appdata_dir, 'settings.json')
    with open(settings_file, 'w') as file:
        json.dump({'api_key': api_key, 'frequency': 120}, file)

def show_api_key_ui():
    root = tk.Tk()
    root.title("Wally")
    root.iconbitmap('./icon-ico.ico')
    root.resizable(False, False)
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 14))
    style.configure('TButton', font=('Arial', 14))
    style.configure('TEntry', font=('Arial', 14))
    label = ttk.Label(root, text="Enter your Unsplash API Key:")
    label.grid(row=0, column=0, padx=10, pady=10)
    api_key_entry = ttk.Entry(root)
    api_key_entry.grid(row=1, column=0, padx=10, pady=10)
    save_button = ttk.Button(root, text="Save API Key", command=lambda: save_api_key_from_ui(api_key_entry.get()))
    save_button.grid(row=2, column=0, padx=10, pady=10)

    def save_api_key_from_ui(api_key):
        if not api_key:
            messagebox.showerror("Error", "API Key cannot be empty.")
            return
        save_api_key(api_key)
        if is_valid_api_key(api_key):
            messagebox.showinfo("Success", "API Key saved successfully!")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
    root.mainloop()

def load_api_key():
    appdata_dir = os.path.join(os.getenv('APPDATA'), 'Wally')
    settings_file = os.path.join(appdata_dir, 'settings.json')
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            data = json.load(file)
            return data.get('api_key')
    return None

def load_frequency():
    appdata_dir = os.path.join(os.getenv('APPDATA'), 'Wally')
    settings_file = os.path.join(appdata_dir, 'settings.json')
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            data = json.load(file)
            return data.get('frequency', 120)
    return 120

def is_valid_api_key(api_key):
    endpoint = 'https://api.unsplash.com/photos/random'
    params = {'client_id': api_key}
    response = requests.get(endpoint, params=params)
    return response.status_code == 200

def on_exit_clicked(icon, item):
    os._exit(0)

def tray_thread():
    icon = pystray.Icon("Wally", image, menu=pystray.Menu(
        pystray.MenuItem("Exit Wally", on_exit_clicked)
    ))
    icon.run()

tray_icon_thread = threading.Thread(target=tray_thread)
tray_icon_thread.daemon = True
tray_icon_thread.start()

def main():
    api_key = load_api_key()
    frequency = load_frequency()
    if not api_key:
        show_api_key_ui()
        api_key = load_api_key()
    while True:
        try:
            set_wallpaper(api_key)
            time.sleep(frequency)
        except Exception as e:
            write_error_to_log(str(e))

if __name__ == "__main__":
    main()
