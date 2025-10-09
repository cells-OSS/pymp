import subprocess
import os
import sys
from packaging import version
import requests

__version__ = "v1.1"


def get_latest_release_tag():
    try:
        url = "https://api.github.com/repos/cells-OSS/pymp/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print("Failed to check for updates:", e)
        return __version__.lstrip("v")


def is_update_available(current_version):
    latest = get_latest_release_tag()
    return version.parse(latest) > version.parse(current_version.lstrip("v"))


def download_latest_script():
    latest_version = get_latest_release_tag()
    filename = f"pymp-v{latest_version}.py"
    url = "https://raw.githubusercontent.com/cells-OSS/pymp/main/pymp.py"
    response = requests.get(url)
    lines = response.text.splitlines()
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
    print(
        f"Current version: {__version__}, Latest: v{get_latest_release_tag()}")
    print(
        f"Downloaded update as '{filename}'. You can now safely delete the old version.")

    input("Press Enter to exit...")
    exit()


def download_youtube_mp3(youtube_url, output_path):
    try:
        yt_dlp_cmd = 'yt-dlp.exe' if os.name == 'nt' else 'yt-dlp'
        subprocess.run([
            yt_dlp_cmd,
            '-x', '--audio-format', 'mp3',
            '-o', output_path,
            youtube_url
        ], check=True)
        print(f"Audio downloaded and saved as {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def download_youtube_mp4(youtube_url, output_path):
    try:
        yt_dlp_cmd = 'yt-dlp.exe' if os.name == 'nt' else 'yt-dlp'
        subprocess.run([
            yt_dlp_cmd,
            '-f', 'mp4',
            '-o', output_path,
            youtube_url
        ], check=True)
        print(f"Video downloaded and saved as {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


if os.path.exists("auto-update.conf"):
    if is_update_available(__version__):
        print("New version available!")
        download_latest_script()

if os.path.exists("welcome_message.conf"):
    with open("welcome_message.conf", "rb") as configFile:
        welcomeMessage = configFile.read().decode()
else:
    welcomeMessage = """
    ===============WELCOME===============
    """

menu = """
  1. Download MP3 (Audio)
  2. Download MP4 (Video)
  3. Settings
  
  TIP: To come back to this menu at any time, just type "back".
"""
print(welcomeMessage, menu)
choice = input("Which option would you like to choose(1/2/3)?: ")

if choice == '1':
    youtube_url = input("Enter the YouTube URL: ")

    if youtube_url.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    output_path = input("Enter the output file path (include 'output.mp3'): ")

    if output_path.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    download_youtube_mp3(youtube_url, output_path)
if choice == '2':
    youtube_url = input("Enter the YouTube URL: ")

    if youtube_url.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    output_path = input("Enter the output file path (include 'output.mp4'): ")

    if output_path.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    download_youtube_mp4(youtube_url, output_path)

if choice == '3':
    settingsMenu = """
===========================================
            Settings Menu
    1 = Turn auto-update on or off
    2 = Change welcome message
===========================================
"""

print(settingsMenu)

settings_choice = input("Which option would you like to choose(1/2)?: ")

if settings_choice.lower() == "back":
    os.execv(sys.executable, [sys.executable] + sys.argv)

if settings_choice == '1':

    with open("auto-update.conf", "wb") as updateSetting:
        updateSetting.write("True".encode())
    print("Auto-update is now enabled.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

if settings_choice == '2':
    new_welcome_message = input(
        "New welcome message(use \\n for new lines): ")
    with open("welcome_message.conf", "w", encoding="utf-8") as f:
        f.write(new_welcome_message.replace("\\n", "\n"))
    print("Welcome message updated.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

else:
    print("Invalid choice.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)
