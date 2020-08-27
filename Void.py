# Project V01D-Terminal

import argparse
from subprocess import call
from webbrowser import open_new_tab
from math import *
from utils import prime
import platform
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command", help="Execute following command")
parser.add_argument("-d", "--directory", help="Start in specified directory")
parser.add_argument("-v", "--verbose",help="Output everything",action="store_true")
parser.add_argument("-e", "--echo",help="Echoes all commands before executing",action="store_true")
parser.add_argument("--welcome",help="Force welcome screen",action="store_true")
parser.add_argument("-s","--skipconfig",help="Terminal will skip loading config",action="store_true")
args = parser.parse_args()

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

def iswindows() -> bool:
    return True if platform.system() == "Windows" else False

def _import():
    from pygame import mixer
    from sys import exit as _exit
    import yaml
    import requests
    import datetime
    import hashlib
    import ctypes
    from elevate import elevate

    # Prompt-toolkit - autocompletion library
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit import PromptSession
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import merge_completers, FuzzyCompleter
    from PathCompleter import PathCompleter
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit.output.color_depth import ColorDepth

    # Project stuff
    import database
    import osBased
    import utils

try:
    from pygame import mixer
    from sys import exit as _exit
    import yaml
    import datetime
    import hashlib
    import requests
    import ctypes
    from elevate import elevate

    # Prompt-toolkit - autocompletion library
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit import PromptSession
    from prompt_toolkit.shortcuts import confirm
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import merge_completers, FuzzyCompleter
    from PathCompleter import PathCompleter
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit.output.color_depth import ColorDepth

    # Project stuff
    import database
    import osBased
    import utils


except Exception as e:
    if sys.executable.find("Python") != -1:
        print(e)
        # Install main lib
        if iswindows():
            os.system("pip install prompt-toolkit")
        else:
            os.system("sudo pip3 install prompt-toolkit")

        from prompt_toolkit.shortcuts import confirm

        # Ask to install all dependencies, if denied, import error will be raised
        if confirm("Install dependencies: "):
            if iswindows():
                os.system("pip install pygame clint elevate yaml requests psutil gputil tabulate pickle screen-brightness-control pathlib typing pynput pytube3")
            else:
                os.system(
                    "sudo pip3 install pygame clint elevate yaml requests pickle screen-brightness-control pathlib typing pynput tabulate psutil gputil pytube3")
        else:
            exit(0)

        # Reimport all dependencies
        _import()
    else:
        print(e)
        if iswindows():
            os.system("pause")
        else:
            os.system("bash -c pause")

# -------------------------------------------

# Get Username
try:
    if iswindows():
        USER = os.environ["USERNAME"]
    else:
        USER = os.environ["USER"]
except:
    USER = "ERROR"

USERDOMAIN = os.environ["USERDOMAIN"]

defPath = os.getcwd()

# For use in "back"
LASTDIR = ""

playing = False
playerInitialized = False

# Path to executable
__location__ = defPath + "\\V01D-Terminal.exe"

# Find config file
if iswindows():
    CONFIG = defPath + r"\config.yml"
else:
    CONFIG = defPath + r"/config.yml"

# Local version
VERSION = "v0.7.1"

# -------------------------------------------

if iswindows():
    os.system("title Void-Terminal")

aliases = database.GetAliases() # Get user alias from database

def saveToYml(data,path) -> None:
    if not os.path.exists(path):
        if not confirm("config.yml not found, create new one ? "): print("config not saved !"); return
    try:
        with open(path, "w") as f:
            f.flush()
            yaml.safe_dump(data, f)
    except:
        print(f"Unable to save data to {path}")

# Load config or defaults
try:
    if not args.skipconfig:
        config = yaml.safe_load(open(CONFIG))
        type(config.keys())
    else: raise
except Exception as e:
    config = {
        "mode":"CMD",
        "welcome":True,
        "downloadDict":("downloadDict.yml"),
        "multithreading":True,
        "fuzzycomplete":True,
        "completeWhileTyping":True,
        "wrapLines":True,
        "mouseSupport":True,
        "searchIgnoreCase":True,
        "default": "#ff0066",
        "pointer": "#b20000",
        "path": "#22ff00",
        "user": "#ff0066",
        "completion-menu.completion": "bg:#000000 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222"
    }

    if not args.skipconfig:
        print(e)
        try:
            if os.path.exists(CONFIG):
                saveToYml(config,CONFIG) # Create new config file
            else:
                if confirm("config.yml not found, ignoring settings and using defaults, would you like to save new config? "): saveToYml(config,CONFIG) # Create new config file
        except:
            print(f"Error writing config file, please check if you are not starting Terminal from PATH, otherwise you dont have permission to write in this folder {CONFIG}")

DOWNLOAD = list(config.get("downloadDict")) # Get all download dictionaries
MODE = config.get("mode","CMD")

# Pick completer based on config and platform
if config["fuzzycomplete"] and iswindows():
    combinedcompleter = FuzzyCompleter(merge_completers([database.WinCompleter, PathCompleter(), database.winWordCompleter, database.WordCompleter(list(aliases.keys()))]))
elif iswindows():
    combinedcompleter = merge_completers([database.WinCompleter, PathCompleter(), database.winWordCompleter])
elif platform.system() == "Linux" and config["fuzzycomplete"]:
    combinedcompleter = FuzzyCompleter(merge_completers([database.LinuxCompleter, PathCompleter()]))
else:
    combinedcompleter = merge_completers([database.LinuxCompleter, PathCompleter()])

# Define console style
_style = Style.from_dict(
    {
        # Default style
        "": config.get("default"),

        # Specific style
        "pointer": config.get("pointer"),
        "path": config.get("path"),
        "user": config.get("user"),

        # Completor
        "completion-menu.completion": config.get("completion-menu.completion"),
        "completion-menu.completion.current": config.get("completion-menu.completion.current"),
        "scrollbar.background": config.get("scrollbar.background"),
        "scrollbar.button": config.get("scrollbar.button")
    }
)

# ---------------------------------------------------------------------------------------------------------------------------------------------

def argget(_splitInput: list) -> str:
    "Returns rebuild string"
    return " ".join(_splitInput)

def welcome() -> None:
    print(f"""
    ██╗   ██╗ ██████╗ ██╗██████╗     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     
    ██║   ██║██╔═══██╗██║██╔══██╗    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     
    ██║   ██║██║   ██║██║██║  ██║       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     
    ╚██╗ ██╔╝██║   ██║██║██║  ██║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     
     ╚████╔╝ ╚██████╔╝██║██████╔╝       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
      ╚═══╝   ╚═════╝ ╚═╝╚═════╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝

    Welcome to Void-Terminal, Windows compatible terminal with predefined functions for advanced users

    This help will be shown only once

    Time: {datetime.datetime.now()}

    Latest release: {utils.version()}

    'help' - show available commands
                """)

def password() -> None: 
    "Get password of wifi network (Windows only)"

    os.system("netsh wlan show profiles")

    networkName = input("Network name > ")

    os.system(f"netsh wlan show profiles {networkName} key=clear")

def void(_splitinput) -> None: # Open new terminal or configure it
    try:
        if (_splitinput[1] == "multithreading"):
            if (_splitinput[2].lower() == "true"):
                config["multithreading"] = True
            elif (_splitinput[2].lower() == "false"):
                config["multithreading"] = False
            print(f"multithreading: {config['multithreading']}")

        elif (_splitinput[1] == "fuzzycomplete"):
            if (_splitinput[2].lower() == "true"):
                config["fuzzycomplete"] = True
            elif (_splitinput[2].lower() == "false"):
                config["fuzzycomplete"] = False
            print(f"fuzzycomplete: {config['fuzzycomplete']}")

        elif (_splitinput[1] == "mouseSupport"):
            if (_splitinput[2].lower() == "true"):
                config["mouseSupport"] = True
            elif (_splitinput[2].lower() == "false"):
                config["mouseSupport"] = False
            print(f"mouseSupport: {config['fuzzycomplete']}")

        elif (_splitinput[1] == "completeWhileTyping"):
            if (_splitinput[2].lower() == "true"):
                config["completeWhileTyping"] = True
            elif (_splitinput[2].lower() == "false"):
                config["completeWhileTyping"] = False
            print(f"completeWhileTyping: {config['fuzzycomplete']}")

        elif (_splitinput[1] == "wrapLines"):
            if (_splitinput[2].lower() == "true"):
                config["wrapLines"] = True
            elif (_splitinput[2].lower() == "false"):
                config["wrapLines"] = False
            print(f"wrapLines: {config['fuzzycomplete']}")

        elif (_splitinput[1] == "welcome"):
            if (_splitinput[2].lower() == "true"):
                config["welcome"] = True
            elif (_splitinput[2].lower() == "false"):
                config["welcome"] = False
            print(f"welcome: {config['fuzzycomplete']}")

        elif (_splitinput[1] == "mode"):
            if (_splitinput[2].lower() == "powershell"):
                config["mode"] = "POWERSHELL"
            elif (_splitinput[2].lower() == "cmd"):
                config["mode"] = "CMD"
            print(f"mode: {config['mode']}")

        elif (_splitinput[1] == "linux") and platform.system() == "Linux":
            if (_splitinput[2].lower() == "generate"):
                print("This will take a while...")
                target = "commands.txt"
                os.system(f'bash -c "compgen -c >{defPath+"/"+target}"')
                print(f"generated: {target}")

        elif (_splitinput[1] == "start"):
            os.system(f"start {__location__}")

        elif (_splitinput[1] == "license"):
            try:
                if _splitinput[2] == "full":
                    if iswindows():
                        f = open(defPath +"\LICENSE")
                        print(f.read())
                    else:
                        f = open(defPath +"/LICENSE")
                        print(f.read())
            except Exception as e:
                print("""
    Void-Terminal  Copyright (C) 2020  Tomáš Novák
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `void license full' for details.
            """)

        elif (_splitinput[1] == "version"):
            if _splitinput[2] == "latest":
                print(utils.version())
            elif _splitinput[2] == "local":
                print(VERSION)

        elif (_splitinput[1] == "install"):
            if _splitinput[2] == "chocolatey":
                if isadmin() == True and iswindows():
                    os.system("powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))")
                elif iswindows():
                    print("Rerun with administrative privileges: use 'admin' or 'elevate'")
                else:
                    print("Only available on Windows")

        elif _splitinput[1] == "updatePythonPackages":
            import pkg_resources
            packages = [dist.project_name for dist in pkg_resources.working_set]
            if iswindows():
                call("pip install --upgrade --use-feature=2020-resolver" + ' '.join(packages), shell=True)
            else:
                call("sudo pip3 install --upgrade --use-feature=2020-resolver" + ' '.join(packages), shell=True)

        elif _splitinput[1] == "title":
            os.system(f"title {_splitinput[-1]}")

        elif _splitinput[1] == "config":
            print(config)
    except:
        print("Not found")
    
    if not args.skipconfig:
        saveToYml(config,CONFIG)

def isadmin() -> bool:
    "Ask if run with elevated privileges"
    try:
        _is_admin = os.getuid() == 0

    except AttributeError:
        _is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return _is_admin

def read(splitInput) -> None:
    "Prints text of file"
    if splitInput == []:
        print("""
    Usage: read [target]

    Print .txt, .py and other text filetypes from terminal

    positional arguments:       
        target     File to read
    """)
    else:
        try:
            path = splitInput[1]
            if '"' in path:
                path = path.split('"')[1]
            elif "'" in path:
                path = path.split("'")[1]
        except:
            print("Incorrrect path. Use path [pathToFile]")
            return
        
        print("\n")
        
        try:
            file = open(path)
        except:
            print("File not found")
            return
        
        try:
            content = file.read()
        except:
            print("File unreadable")
            return
        
        print(content)
        file.close()

def power() -> None:
    "Change Windows power scheme"
    print("If you want best powerscheme paste this, then paste ID of the new scheme: powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
    os.system("powercfg -list")
    _input = input("Select scheme: ")

    if _input == "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61":
        os.system(_input)
        os.system("powercfg -list")
        _input = input("Paste scheme id: ")
        os.system("powercfg /setactive " + _input)

    else:
        os.system("powercfg /setactive " + _input)

def hashfilesum(splitInput,hashalg) -> None:
    with open(splitInput[1], "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashalg.update(chunk)

# --------------------------------------------

def switch(userInput) -> None:
    splitInput = userInput.split()
    global LASTDIR
    global playing
    global playerInitialized
    try:
        arg = argget(splitInput[1:])
    except:
        pass
    if splitInput == []:
        return

    if splitInput[0].lower() == "password":
        password()
        return

    if splitInput[0] == "downloadeta":
        out = []
        mdict = {
            "KB":"1000",
            "MB":"1000000",
            "GB":"1000000000",
            "TB":"1000000000000",
            "PB":"1000000000000000",
        }
        for item in [splitInput[1],splitInput[2]]:
            for multiplier in ["KB", "MB", "GB", "TB", "PB"]:
                if str(item).find(multiplier) != -1:
                    item = item.replace(multiplier, "")
                    m = mdict.get(multiplier)
                    out.append(float(item) * float(m))
        target = out[0]
        speed = out[1]

        print(f"ETA: {((target / speed) / 60 / 60).__round__(3)} h")
        return

    if userInput.lower() == "back":
        __placeholder = os.getcwd()
        if LASTDIR == "": return
        os.chdir(LASTDIR)
        if __placeholder != LASTDIR:
            LASTDIR = __placeholder
        return

    elif userInput.lower() == "elevate" or userInput.lower() == "admin":
        elevate()
        return

    elif splitInput[0].lower() == "convert":
        utils.convert(splitInput)

    elif splitInput[0].lower() == "ytdown":
        utils.ytvid(userInput)
        return
        
    elif splitInput[0].lower() == "music-play":
        if not playerInitialized:
            mixer.init()
            playerInitialized = True
        f = argget(splitInput[1:])
        if '"' in f: f = f.replace('"','')
        f = r"{}".format(f)
        mixer.music.load(f)
        mixer.music.play()
        playing = True
        if args.verbose:
            print(f"Playing {f}")
        return        

    elif splitInput[0].lower() == "music-pause":
        if not playerInitialized: print("Player not initialized"); return
        if playing == True:
            mixer.music.pause()
            playing = False
            if args.verbose:
                print("Paused")
        return

    elif splitInput[0].lower() == "music-resume":
        if not playerInitialized: print("Player not initialized"); return
        if playing == False:
            mixer.music.unpause()
            playing = True
            if args.verbose:
                print("Resumed")
        return

    elif splitInput[0].lower() == "music-stop":
        if not playerInitialized: print("Player not initialized"); return
        if playing == True:
            mixer.music.stop()
            mixer.quit()
            playerInitialized = False
            if args.verbose:
                print("Stopped")
        return

    elif splitInput[0].lower() == "music-volume":
        if not playerInitialized:
            mixer.init()
            playerInitialized = True
        volume = float(splitInput[1]) / 100
        mixer.music.set_volume(volume)
        if args.verbose:
            print(f"Volume set to {volume}")
        return

    elif userInput.lower() == "grantfiles" and iswindows():
        os.system('ICACLS "." /INHERITANCE:e /GRANT:r %USERNAME%:(F) /T /C ')
        return

    elif splitInput[0].lower() == "brightness":
        try:
            target = splitInput[1]
            utils.setbrightness(target)
            if args.verbose:
                print(f"Brightness set to {target}")
        except:
            utils.getbrightness()
        return

    elif splitInput[0].lower() == "cheat":
        text = splitInput[1:]
        out = ""
        for item in text:
            if item != text[-1]:
                out += item + "/"
            else:
                out += item
        os.system(f"curl cht.sh/{out}")
        return

    elif splitInput[0].lower() == "checklastvid":
        os.system(f'curl -s "https://decapi.me/youtube/latest_video?user={argget(splitInput[1:])}"')
        print()
        return

    elif splitInput[0].lower() == "checklasttweet":
        os.system(f'curl -s "https://decapi.me/twitter/latest?name={argget(splitInput[1:])}"')
        print()
        return

    elif splitInput[0].lower() == "checktwitchonline":
        os.system(f'curl -s "https://decapi.me/twitch/uptime?channel={argget(splitInput[1:])}"')
        print()
        return

    elif splitInput[0].lower() == "fileconvert":
        os.system(f'curl "http://c.docverter.com/convert" -F from={splitInput[1]} -F to={splitInput[2]} -F "input_files[]=@{splitInput[3]}" -o "{splitInput[4]}"')
        return

    elif splitInput[0].lower() == "ping.gg":
        try:
            os.system("curl ping.gg/"+splitInput[1])
        except:
            os.system("curl ping.gg")
        return

    elif splitInput[0].lower() == "guid":
        os.system("curl givemeguid.com")
        print()
        return

    elif splitInput[0].lower() == "shorten":
        os.system(f'curl -F shorten="{splitInput[1]}" https://ttm.sh')
        return

    elif splitInput[0].lower() == "transfer":
        os.system(f'curl -F file=@"{argget(splitInput[1:])}" https://ttm.sh')
        return

    elif splitInput[0].lower() == "dns":
        os.system("curl -L https://edns.ip-api.com/json")
        print()
        return

    elif splitInput[0].lower() == "speedtest":
        os.system("curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -")
        return

    elif splitInput[0].lower() == "cryptocurrency":
        try:
            os.system("curl rate.sx/"+splitInput[1])
        except:
            os.system("curl rate.sx")
        return

    elif splitInput[0].lower() == "weather":
        try:
            os.system("curl wttr.in/"+splitInput[1])
        except:
            os.system("curl wttr.in")
        return

    elif splitInput[0].lower() == "covid19":
        try:
            os.system("curl https://corona-stats.online/"+splitInput[1])
        except:
            os.system("curl https://corona-stats.online/")
        return

    elif userInput.lower() == "ip":
        os.system("curl api.ipify.org")
        print()
        return

    elif splitInput[0].lower() == "geoip":
        try:
            os.system("curl ipinfo.io/"+splitInput[1])
        except:
            os.system("curl ipinfo.io")
        print()
        return

    elif splitInput[0].lower() == "qrcode":
        try:
            os.system("curl qrenco.de/"+splitInput[1])
        except:
            print("Invalid argument")
        return

    elif splitInput[0].lower() == "stonks":
        try:
            os.system("curl stonks.icu/"+splitInput[1])
        except:
            print("Invalid argument: eg. stonks amd/intl/tsla")
        return

    elif userInput.lower() == "pagefile":
        os.system("wmic pagefile list")
        return

    elif splitInput[0].lower() == "bluetooth":
        if isadmin() == True:
            if splitInput[1].lower() == "off":
                os.system("net stop bthserv")
            elif splitInput[1].lower() == "on":
                os.system("net start bthserv")
        else: print("Run shell as administrator or use: admin")
        return

    elif splitInput[0].lower() == "wifi":
        if splitInput[1].lower() == "enable":
            os.system("wmic nic get name, index")
            index = input("Device index: ")
            if index == "": return
            os.system(f"wmic path win32_networkadapter where index={index} call enable")
        elif splitInput[1].lower() == "disable":
            os.system("wmic nic get name, index")
            index = input("Device index: ")
            if index == "": return
            os.system(f"wmic path win32_networkadapter where index={index} call disable")
        return

    elif splitInput[0].lower() == "online":
        urls = splitInput[1:]
        for url in urls:
            try:
                response = requests.get(url)
                print(f"{url} OK: {response.elapsed.total_seconds()}s" if response.ok == True else "SITE DOWN")
            except:
                print(url + " SITE DOWN")

    elif splitInput[0].lower() == "poweroff":
        os.system("shutdown /s /f /t 0")
        return

    elif splitInput[0].lower() == "reboot":
        os.system("shutdown /r /f /t 0")
        return

    elif userInput.lower() == "motherboard":
        os.system("wmic baseboard get product,Manufacturer,version,serialnumber")
        return

    elif userInput.lower() == "ram":
        utils.memory()
        return

    elif userInput.lower() == "cpu":
        utils.cpu()
        return

    elif userInput.lower() == "gpu":
        utils.gpu()
        return

    elif userInput.lower() == "network":
        utils.network()
        return

    elif userInput.lower() == "disk":
        utils.disk()
        return

    elif userInput.lower() == "bootinfo":
        utils.bootinfo()
        return

    elif userInput.lower() == "component":
        utils.sysinfo()
        utils.cpu()
        utils.gpu()
        utils.memory()
        utils.bootinfo()
        utils.disk()
        utils.network()
        return

    elif userInput.lower() == "firewall":
        os.system("WF.msc")
        return

    elif userInput.lower() == "services":
        os.system("services.msc")
        return

    elif userInput.lower() == "manager":
        os.system("compmgmt.msc")
        return

    elif userInput.lower() == "event":
        os.system("eventvwr.msc")
        return

    elif userInput.lower() == "power":
        power()
        return

    elif userInput.lower() == "godmode" and iswindows():
        os.system("mkdir GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")
        os.system("explorer GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")
        os.system("rmdir GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")

    # Hashing ----------------------------------------------------------

    elif splitInput[0].lower() == "sha1":
        text = argget(splitInput[1:])
        print(hashlib.sha1(bytes(text, "utf-8")).hexdigest(),text)
        return

    elif splitInput[0].lower() == "sha224":
        text = argget(splitInput[1:])
        print(hashlib.sha224(bytes(text, "utf-8")).hexdigest(),text)
        return

    elif splitInput[0].lower() == "sha256":
        text = argget(splitInput[1:])
        print(hashlib.sha256(bytes(text, "utf-8")).hexdigest(),text)
        return

    elif splitInput[0].lower() == "sha384":
        text = argget(splitInput[1:])
        print(hashlib.sha384(bytes(text, "utf-8")).hexdigest(),text)
        return

    elif splitInput[0].lower() == "sha512":
        text = argget(splitInput[1:])
        print(hashlib.sha512(bytes(text, "utf-8")).hexdigest(),text)
        return

    elif splitInput[0].lower() == "md5":
        text = argget(splitInput[1:])
        print(hashlib.md5(bytes(text, "utf-8")).hexdigest(),text)
        return

    # Hash sum -----------------------------------------------

    elif splitInput[0].lower() == "sha1sum":
        hashsum = hashlib.sha1()
        hashfilesum(splitInput,hashsum)
        print(hashsum.hexdigest())
        return

    elif splitInput[0].lower() == "sha224sum":
        hashsum = hashlib.sha224()
        hashfilesum(splitInput, hashsum)
        print(hashsum.hexdigest())
        return

    elif splitInput[0].lower() == "sha256sum":
        hashsum = hashlib.sha256()
        hashfilesum(splitInput, hashsum)
        print(hashsum.hexdigest())
        return

    elif splitInput[0].lower() == "sha384sum":
        hashsum = hashlib.sha384()
        hashfilesum(splitInput, hashsum)
        print(hashsum.hexdigest())
        return

    elif splitInput[0].lower() == "sha512sum":
        hashsum = hashlib.sha512()
        hashfilesum(splitInput, hashsum)
        print(hashsum.hexdigest())
        return

    elif splitInput[0].lower() == "md5sum":
        hashsum = hashlib.md5()
        hashfilesum(splitInput, hashsum)
        print(hashsum.hexdigest())
        return

    # --------------------------------------------------------------

    elif splitInput[0].lower() == "plain2string":
        print(utils.PlainToString(argget(splitInput[2:]), mode=splitInput[1]))
        return 

    elif userInput.lower() == "help": # Print cmd help and defined help at the same time
        if iswindows():
            os.system("help")
            print("\n" +

                "\n MATH: \n\n"
                    "       +   -    Addition\n"
                    "       -   -    Subtraction\n"
                    "       *   -    Multiplication\n"
                    "       /   -    Division\n"
                    "       %   -    Modulus\n"
                    "       **  -    Exponentiation\n"
                    "       //  -    floor division\n"
                    "   gcd - greatest common divisor: gcd [value],[value]\n"
                    "   lcm - least common multiple: lcm [value],[value]\n"
                    "   rng - random number generator: rng [min(included)],[max(excluded)]\n"

                "\n COMPUTER: \n\n"

                    "   component - info about workstation\n"
                    "   motherboard, cpu, gpu, ram, disk, network, bootinfo - info about your workstation´s component\n"

                "\n WINDOWS DEFINED: \n\n"

                    "   control - control panel\n"
                    "   diskpart - open diskpart\n"
                    "   msconfig - configure your system\n"
                    "   msinfo32 - show windows configuration\n"
                    "   regedit - tool for editing registers\n"
                    "   sysdm.cpl - system properties\n"
                    "   firewall - configure firewall settings\n"
                    "   services - configure services\n"
                    "   manager - computer management\n"
                    "   event - event viewer\n"
                    "   dxdiag - DirectX diagnostics tool\n"

                "\n MANAGEMENT: \n\n"

                    "   exit | quit - quit application\n"
                    "   os - show operating system\n"
                
                "\n ALIAS: \n\n"

                    "   alias - define your own function: alias [name | -list] [command(if name)]\n"
                    "   delalias - remove alias: delalias [name]\n"

                "\n OTHER FUNCTIONS \n\n"
                    "   downloadeta - calculate estimated time of arival: downloadeta [target(GB)] [speed(MB)]\n"
                    "   convert - function for converting temperatures, colors to hex, audio|files and merging them\n"
                    "   ping - never ending ping loop\n"
                    "   pagefile - show pagefile location and size\n"
                    "   read - read specified .txt file: read [target]\n"
                    "   power - change your Windows powerplan\n"
                    "   download - dictionary for downloading files: download [-list | target | URL]\n"
                    "   open - open file explorer in current directory\n"
                    "   plain2string - convert plain text to strings: plain2string mode[space,file, fileline] text/[filename]\n"
                    "   md5, sha1 , sha224, sha256, sha384, sha512 - hash string\n"
                    "   md5sum, sha1sum, sha224sum, sha256sum, sha384sum, sha512sum - hash file: (function) [target]\n"
                    "   elevate, admin - grant admin permission for shell\n"
                    "   cheat - programmer cheat sheet: cheat [querry]\n"
                    "   checklastvid - get last youtube video of specified channel: checklastvid [channel]\n"
                    "   checklasttweet - get last tweet of specified user: checklasttweet [channel]\n"
                    "   checktwitchonline - get information about specified twitch channel: checklastvid [channel]\n"
                    "   fileconverter - convert files to other types: fileconverter [input type] [output type] [target] [new file name]\n"
                    "   ping.gg - server monitoring utility\n"
                    "   guid - generate random GUID\n"
                    "   dns - get dns information\n"
                    "   shorten - make url shorter: shorten [target]\n"
                    "   transfer - temporarily upload a file to server: transfer [target]\n"
                    "   speedtest - check internet connection speed\n"
                    "   weather - check weather, if no location specified, check local weather: weather [location(optional) | moon(optional)]\n"
                    "   covid19 - display status of current covid19 situation in country: covid19 [location(optional)]\n"
                    "   ip - get your external IP address\n"
                    "   geoip - get your external IP address and location: geoip [target(optional)]\n"
                    "   qrcode - make qrcode out of user input: qrcode [text]\n"
                    "   stonks - get stock information: stonks [target]\n"
                    "   cryptocurrency - get cryptocurrency information: cryptocurrency [currency | currency@time | :help]\n"
                    "   ytdown - download youtube video (if you want both audio and video, download both and then combine them on youselves): ytdown [url]\n"

                "\n IN DEVELOPMENT \n\n"
            )
        else:
            call("help", shell=True)
            
        return

    elif userInput.lower() == "ping": # Never ending ping loop
        os.system("start ping google.com -t")
        return

    elif userInput.lower() == "welcome": # Show welcome screen
        welcome()
        return

    elif splitInput[0].lower() == "search":
        open_new_tab(url = "https://www.google.com/search?q=" + " ".join(splitInput[1:]))

    elif splitInput[0].lower() == "sizeof": # Show welcome screen
        def get_size(start_path = '.'):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # skip if it is symbolic link
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)

            return total_size
        print(get_size(splitInput[1]) / 1000000,"MB")

    elif splitInput[0].lower() == "currencyconverter": # Show welcome screen
        rate = utils.currencyconverter(splitInput[1].upper(), splitInput[2].upper())
        print(f"{(rate * float(splitInput[3])).__round__(2)} {splitInput[2]}")
        return

    elif userInput.lower() == "os": # Show os
        print(osBased.Os())
        return

    elif userInput.lower() == "clear" or userInput.lower() == "cls": # Clear terminal
        osBased.Clear()
        return
    
    elif splitInput[0].lower() == "read":
        read(splitInput)
        return
    
    elif splitInput[0].lower() == "void":
        void(splitInput)
        return

    elif splitInput[0].lower() == "compile":
        call('auto-py-to-exe', shell=True)
        return

    elif splitInput[0].lower() == "lcm":
        nums = str(splitInput[1]).split(",")
        num = [float(nums[0]),float(nums[1])]
        print(utils.lcm(num[0],num[1]))
        return

    elif splitInput[0].lower() == "gcd":
        nums = str(splitInput[1]).split(",")
        num = [float(nums[0]), float(nums[1])]
        print(utils.gcd(num[0], num[1]))
        return

    elif splitInput[0].lower() == "rng":
        nums = str(splitInput[1]).split(",")
        num = [float(nums[0]), float(nums[1])]
        print(utils.rng(num[0], num[1]))
        return

    elif splitInput[0].lower() == "open" and iswindows(): # Open file explorer in cwd
        target = argget(splitInput[1:])
        if target != "":
            os.system(f"explorer {target}")
        else:
            os.system("explorer .\\")
        return

    elif userInput.lower() == "settings" and iswindows():  # Open file explorer in cwd
        os.system("start ms-settings:")
        return

    elif userInput.lower() == "startup" and iswindows():
        os.system("explorer %AppData%\Microsoft\Windows\Start Menu\Programs\Startup")

    elif splitInput[0].lower() == "pwned": # Check if your password is in someones dictionary
        try:
            import pwned
            print(pwned.lookup_pwned_api(splitInput[1]))
        except:
            print("Error")
        
        return

    # Change directory based on input
    elif splitInput[0].lower() == "cd" and arg:
        if os.getcwd() != LASTDIR:
            LASTDIR = os.getcwd()
        if '"' in arg:
            path = argget(splitInput[1:]).split('"')[-2]
        else:
            path = argget(splitInput[1:])
        os.chdir(path)
        return

    elif userInput.lower() == "exit" or userInput.lower() == "quit": # Terminate application
        _exit()

    elif splitInput[0].lower() == "alias": # Define own function and save it
        if splitInput[1] == "-list":
            print(aliases)
        else:
            l = splitInput[2:]
            try:
                splitInput[2]
            except:
                print("No command specified")
                return
            complete = " ".join(l)
            aliases[splitInput[1]] = complete
            database.WriteAliases(aliases)
        return

        

    elif splitInput[0].lower() == "delalias": # Remove alias from dictionary and update save
        try:
            aliases.pop(splitInput[1])
            database.WriteAliases(aliases)
        except:
            print("Name is not in list ! \nUsage: delalias [name]")

    elif userInput.lower() == "eval": # Show alias dictionary
        while True:
            try:
                _eval = session.prompt(message=HTML(f"<user>{USER}</user> <path>eval</path>""<pointer> > </pointer>"), style=_style, complete_in_thread=config["multithreading"], set_exception_handler=True,color_depth=ColorDepth.TRUE_COLOR, completer=None)
                if _eval.lower() == "quit" or _eval.lower() == "exit":
                    break
                else:
                    eval(compile(_eval,"<string>","exec"))
            except Exception as e:
                print(e)
        return

    elif splitInput[0].lower() == "download": # Dictionary for downloading (direct link to website mirror) or download straight to active folder
        try:
            if splitInput[1].lower() == "-list":
                for i in DOWNLOAD:
                    try:
                        print(dict(yaml.safe_load(open(i))).keys())
                    except: pass
            else:
                raise
        except:
            try:
                for item in splitInput[1:]:
                    utils.download(item)
            except Exception as e:
                print(e)
                print("""
    Usage: download [-list] [target]

    Downloads files based on URL or dictionary

    optional arguments:       
        -list       Show dictionary of URLs
    positional arguments
        target      URL or key from 'download -list'
    """)

    else:
        try: # Calculator
            output = eval(userInput.lower())
            if type(output) in [float, int, list, tuple, str, bool]:
                print(output)
            else:
                raise
        except: # Try if input is alias
            try:
                os.chdir(userInput)
            except:
                if iswindows():
                    if MODE == "CMD":
                        os.system(userInput)
                    elif MODE == "POWERSHELL":
                        os.system(f"powershell -Command {userInput}")
                else:
                    os.system(f'bash -c "{userInput}"')

# --------------------------------------------

session = PromptSession(completer=combinedcompleter,
                        complete_while_typing=config.get("completeWhileTyping"),
                        mouse_support=config.get("mouseSupport"),
                        wrap_lines=config.get("wrapLines"),
                        auto_suggest=AutoSuggestFromHistory(),
                        search_ignore_case=config.get("searchIgnoreCase"),
                        enable_open_in_editor=True,
                        refresh_interval=0,
                        color_depth=ColorDepth.TRUE_COLOR,
                        editing_mode=EditingMode.VI
                        )

# ---------------------------------------------

def main() -> None:
    """
    Terminal main loop
    """
    if args.directory:
        try:
            os.chdir(args.directory)
        except:
            print("Directory not found or accessible")
            return

    if config.get("welcome") or args.welcome:
        welcome()
    while True:
        try:
            cd = os.getcwd() # Get current working directory
            privileges = "#" if isadmin() == True else "$"
            promptMessage = HTML(f"""
┌──(<user>{USER}</user> ⌨  <user>{USERDOMAIN}</user>)<pointer>-</pointer>[<path>{cd}</path>]\n└─{privileges} """)

            userInput = session.prompt(message=promptMessage,style=_style,complete_in_thread=config["multithreading"],set_exception_handler=True,color_depth=ColorDepth.TRUE_COLOR)  # Get user input (autocompetion allowed)
            
            userInput = envirotize(userInput)

            if args.echo:
                print(userInput)

            switch(userInput=userInput)

        except KeyboardInterrupt:
            print()
        except Exception as error:
            print(error.with_traceback(error.__traceback__))
            os.system("pause")

def envirotize(string) -> str:
    "Applies Environment variables and aliases"
    values = aliases.keys()
    if not "delalias" in string:
        for value in values:
            if string.find(value) != -1:
                string = string.replace(value,aliases.get(value))

    splitInput = string.split()

    for i in splitInput:
        if i.find("%") != -1:
            spl = i.split("%")[1]
            env = os.environ[spl]
            splitInput[splitInput.index(i)] = splitInput[splitInput.index(i)].replace(f"%{spl}%",env)
    
    rebuild = " ".join(splitInput)

    if string != rebuild:
        string = rebuild
    
    return string

if __name__ == "__main__":
    if args.command:
        userInput = envirotize(args.command)

        switch(userInput)
    
    main()
    

