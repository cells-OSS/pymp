from logging import config
import subprocess
import json
import os
import sys
import shutil

__version__ = "v1.9"


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
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def download_youtube_mp3_partial(youtube_url, output_path, start_time, end_time):
    """
    Download only a section as MP3 using yt-dlp's --download-sections and extract audio.
    start_time / end_time accept formats like SS, MM:SS or HH:MM:SS.
    """
    yt_dlp_cmd = 'yt-dlp.exe' if os.name == 'nt' else 'yt-dlp'
    ffmpeg_cmd = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'

    # normalize path, ensure .mp3 extension, create parent dir if possible
    output_path = os.path.expanduser(output_path)
    output_path = os.path.abspath(output_path)
    if not output_path.lower().endswith(".mp3"):
        output_path += ".mp3"
    parent = os.path.dirname(output_path) or "."

    if parent and not os.path.exists(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except PermissionError:
            print(f"Permission denied creating '{parent}'. Falling back to current directory.")
            output_path = os.path.basename(output_path)

    # require yt-dlp and ffmpeg (yt-dlp uses ffmpeg to extract)
    if shutil.which(yt_dlp_cmd) is None:
        print("yt-dlp not found. Please install yt-dlp and ensure it's on your PATH.")
        return
    if shutil.which(ffmpeg_cmd) is None:
        print("ffmpeg not found. Please install ffmpeg and ensure it's on your PATH.")
        return

    cmd = [
        yt_dlp_cmd,
        "--download-sections", f"*{start_time}-{end_time}",
        "-x", "--audio-format", "mp3",
        "-o", output_path,
        youtube_url
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Trimmed audio saved to: {output_path}")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as e:
        print("yt-dlp failed:", e)
    except PermissionError as e:
        print("Permission error:", e)

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
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def download_youtube_mp4_partial(youtube_url, output_path, start_time, end_time):
    yt_dlp = "yt-dlp.exe" if os.name == "nt" else "yt-dlp"
    subprocess.run([yt_dlp, "--download-sections", f"*{start_time}-{end_time}", "-t", "mp4", "-o", output_path, youtube_url], check=True)
    print(f"Trimmed video downloaded and saved as {output_path}")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def convert_mp4_to_mp3(input_file, output_file, bitrate="192k"):
    """
    Convert an MP4 (or other video file) to .mp3 using ffmpeg.
    Requires ffmpeg on PATH or ffmpeg.exe on Windows.
    """
    ffmpeg_cmd = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
    if shutil.which(ffmpeg_cmd) is None:
        print("ffmpeg not found. Please install ffmpeg and ensure it's on your PATH.")
        return

    if not os.path.exists(input_file):
        print("Input file does not exist:", input_file)
        return

    if not output_file.lower().endswith(".mp3"):
        output_file += ".mp3"

    cmd = [
        ffmpeg_cmd,
        "-y",           # overwrite output without asking
        "-i", input_file,
        "-vn",          # no video
        "-ab", bitrate,  # audio bitrate
        "-ar", "44100",  # audio sampling rate
        output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Converted '{input_file}' -> '{output_file}'")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except subprocess.CalledProcessError as e:
        print("ffmpeg failed:", e)


def install_packages(package):
    if os.name == 'nt':
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])
    else:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--break-system-packages"])


required_packages = ["yt-dlp", "requests", "packaging", "pyfiglet"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing required package {package}...")
        install_packages(package)

os.system('cls' if os.name == 'nt' else 'clear')

from packaging import version
import requests
import pyfiglet

if os.name == "nt":
    config_dir = os.path.join(os.getenv("APPDATA"), "pymp")
else:
    config_dir = os.path.expanduser("~/.config/pymp")

os.makedirs(config_dir, exist_ok=True)

config_path = os.path.join(config_dir, "config.json")

def load_config():
    path = os.path.join(config_dir, "config.json")
    if not os.path.exists(path):
        default = {"auto_updates": True, "figlet_welcome": False}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

def load_config():
    path = os.path.join(config_dir, "config.json")
    if not os.path.exists(path):
        default = {"auto_updates": True, "figlet_welcome": False}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(os.path.join(config_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def toggle_auto_updates():
    config = load_config()
    
    config["auto_updates"] = not config.get("auto_updates", True)
    
    save_config(config)
    print(f"Auto updates are now {'ON' if config['auto_updates'] else 'OFF'}")

def toggle_figlet():
    config = load_config()
    
    config["figlet_welcome"] = not config.get("figlet_welcome", False)
    
    save_config(config)
    print(f"Figlet welcome message is now {'ON' if config['figlet_welcome'] else 'OFF'}")

welcomeMessage_config_path = os.path.join(config_dir, "welcome_message.conf")

if os.path.exists(welcomeMessage_config_path):
    with open(welcomeMessage_config_path, "rb") as configFile:
        welcomeMessage = configFile.read().decode()
else:
    welcomeMessage = """
#####################################
              WELCOME
#####################################
    """

if config["figlet_welcome"]:
    welcomeMessage = pyfiglet.figlet_format(welcomeMessage)

if config["auto_updates"]:
    if is_update_available(__version__):
        print("A new version of Pyculator is available!")
        user_input = input(
            "Would you like to download the latest version? (y/n): ").strip().lower()
        if user_input == "y":
            download_latest_script()

menu = """
  1. Download MP3 (Audio)
  2. Download MP4 (Video)
  3. Convert MP4 (Video) to MP3 (Audio)
  4. Settings
  
  TIP: To come back to this menu at any time, just type "back".
"""
print(welcomeMessage, menu)
choice = input("Which option would you like to choose(1/2/3/4)?: ")

if choice == '1':
    mp3downloadMenu = """
###########################################
        MP3 Download Options
1 = Download the entire audio
2 = Download a specific part of the audio
###########################################
"""
    print(mp3downloadMenu)
    mp3download_choice = input("Which option would you like to choose(1/2)?: ")
    if mp3download_choice.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)
    if mp3download_choice == '1':
        youtube_url = input("Enter the YouTube URL: ")

        if youtube_url.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        output_path = input("Enter the output file path (include the name of the file): ")

        if output_path.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        download_youtube_mp3(youtube_url, output_path + ".mp3")

    if mp3download_choice == '2':
        youtube_url = input("Enter the YouTube URL: ")

        if youtube_url.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        output_path = input("Enter the output file path (include the name of the file): ")

        if output_path.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        start_time = input("Enter the start time (in seconds or HH:MM:SS): ")

        if start_time.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        end_time = input("Enter the end time (in seconds or HH:MM:SS): ")

        if end_time.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        download_youtube_mp3_partial(youtube_url, output_path + ".mp3", start_time, end_time)

    else:
        print("Invalid choice.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


if choice == '2':
    mp4downloadMenu = """
###########################################
        MP4 Download Options
1 = Download the entire video
2 = Download a specific part of the video
###########################################
"""
    print(mp4downloadMenu)
    mp4download_choice = input("Which option would you like to choose(1/2)?: ")

    if mp4download_choice.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if mp4download_choice == '1':

        youtube_url = input("Enter the YouTube URL: ")

        if youtube_url.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        output_path = input("Enter the output file path (include the name of the file): ")

        if output_path.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        download_youtube_mp4(youtube_url, output_path + ".mp4")

    if mp4download_choice == '2':
        youtube_url = input("Enter the YouTube URL: ")
        
        if youtube_url.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        output_path = input("Enter the output file path (include the name of the file): ")

        if output_path.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        start_time = input("Enter the start time (in seconds or HH:MM:SS): ")

        if start_time.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        end_time = input("Enter the end time (in seconds or HH:MM:SS): ")

        if end_time.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        download_youtube_mp4_partial(youtube_url, output_path + ".mp4", start_time, end_time)

    else:
        print("Invalid choice.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


if choice == '3':
    input_file = input("Enter path to the MP4 file: ")
    if input_file.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    output_file = input("Enter desired output MP3 path (or name): ")
    if output_file.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    convert_mp4_to_mp3(input_file, output_file)
    print("Conversion complete.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


if choice == '4':
    settingsMenu = """
###########################################
            Settings Menu
1 = Turn auto-update on or off
2 = Change welcome message
3 = Reset welcome message
4 = Toggle figlet welcome message
###########################################
"""

    print(settingsMenu)

    settings_choice = input("Which option would you like to choose(1/2/3)?: ")

    if settings_choice.lower() == "back":
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if settings_choice == '1':

        auto_update_menu = """
#########################################
              Auto-Updates
1 = Toggle auto-updates
#########################################
    """
        print(auto_update_menu)

        auto_update_choice = input("Which option would you like to choose(1/2)?: ")

        if auto_update_choice.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        if auto_update_choice == '1':
            toggle_auto_updates()
            print("Auto-update is now enabled.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        else:
            print("Auto-Updates are already disabled!")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    if settings_choice == '2':
        new_welcome_message = input("New welcome message(use \\n for new lines): ")

        config_path = os.path.join(config_dir, "welcome_message.conf")

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_welcome_message.replace("\\n", "\n"))
        print("Welcome message updated.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if settings_choice == '3':
        config_path = os.path.join(config_dir, "welcome_message.conf")

        if os.path.exists(config_path):
            os.remove(config_path)
            print("Welcome message have successfully been reset.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        else:
            print("Welcome message is already the default.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    if settings_choice == '4':
        figlet_welcome = """
######################################
           Figlet Welcome
1 = Toggle figlet welcome message
######################################
        """
        print(figlet_welcome)

        figlet_choice = input("Which option would you like to choose(1/2)?: ")
        
        if figlet_choice.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        if figlet_choice == '1':
            toggle_figlet()
            print("Figlet welcome message setting toggled.")
            input("Press Enter to continue...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    else:
        print("Invalid choice.")
        input("Press Enter to continue...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
else:
    print("Invalid choice.")
    input("Press Enter to continue...")
    os.execv(sys.executable, [sys.executable] + sys.argv)
