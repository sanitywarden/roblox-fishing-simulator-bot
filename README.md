#### README in other languages
[Polski](https://github.com/sanitywarden/roblox-fishing-simulator-bot/pl_README.md)

# roblox-fishing-simulator-bot
This is the repository for a simple Windows/MacOS Python bot/script which automates the fishing process in a Roblox game called Fishing Simulator.

>This is a project developed out of my own curiosity and for educational purposes only. Using bots and/or automation scripts makes the experience worse for the gaming community and should be avoided.

>Using this script is most likely against Roblox guideliness and could get you banned if caught. Use at your own risk and always respect the terms of service of the game and platform.

## Features

* Works on Windows (`windows.py`) and MacOS (`macos.py`)
* Detects game features using pixel color recognition
* Randomized LMB press timings to mimick human interaction 
* Pauses when inventory is full
* Ability to stop (default `q`) or pause (default `p`) the script
* Ability to manually restart the bot if it seems to malfunction (default `r`)
* Ability to print information about current fishing session in the terminal (default `i`)

## Rates and efficiency
I measured that the bot averages at about a fish per 10 to 12 seconds. That makes it catch about 300 to 360 fish per hour.


## Prerequisites
- Roblox
- Python

## How to install it
### Using `git`

1. Clone/download this repository
```
git clone https://github.com/sanitywarden/roblox-fishing-simulator-bot
```

2. Open the `roblox-fishing-simulator-bot` folder in your terminal and depending on your OS install appropriate packages.

#### Windows
```
pip install -r windows_requirements.txt
```

Once the packages install, prepare your Roblox, join the Fishing Simulator game and run either `python windows.py` or `python3 windows.py`. If none of those work it means you don't have a `python` interpreter installed on your system. Install it, and come back to this step later.


#### MacOS
```
pip install -r macos_requirements.txt
```

Once the packages install, your Mac will most likely not let you run this script yet. You have to first give it some permissions, as the OS is more restrictive of what it lets you run.

Go to `Settings > Privacy & Security > Accessibility` and add the `Terminal` app to the list. Do the same in `Screen & System Audio Recording`.

Now prepare your Roblox, join the Fishing Simulator game and run either `python macos.py` or `python3 macos.py`. If none of those work it means you don't have a `python` interpreter installed on your system. Install it, and come back to this step later.