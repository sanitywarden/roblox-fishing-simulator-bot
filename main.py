from pydoc import cli
from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api, win32con
import pydirectinput
import yaml

width, height = pyautogui.size()
middle_screen_x = int(width / 2)
middle_screen_y = int(height / 2)

# Load and get the .yaml config or None
def load_yaml_settings():
    with open('./config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        return config 
    return None

def load_version(): 
    with open('./version.txt', 'r') as file:
        version = file.read()
        return version
    return "version.txt file not found"

config = load_yaml_settings()
if config is None:
    print_with_time("Roblox fishing bot requires the 'config.yaml' file but it doesn't exist")
    exit(1)

# From config
debug_mode                   = int(config['debug_mode'])
start_script_countdown_s     = int(config['start_script_countdown_s'])
reset_state_cooldown_s       = int(config['reset_state_cooldown_s'])
quit_script_hotkey           = config['quit_script_hotkey']
pause_script_hotkey          = config['pause_script_hotkey']
reset_script_hotkey          = config['reset_script_hotkey']
show_info_hotkey             = config['show_info_hotkey']
fishing_minigame_click_min_s = float(config['fishing_minigame_click_min_s'])
fishing_minigame_click_max_s = float(config['fishing_minigame_click_max_s'])
detect_range_bubble_x        = int(config['detect_range_bubble_x'])
detect_range_bubble_y        = int(config['detect_range_bubble_y'])
detect_range_arc_x           = int(config['detect_range_arc_x'])
detect_range_arc_y           = int(config['detect_range_arc_y'])
detect_range_backpack_full_x = int(config['detect_range_backpack_full_x'])
detect_range_backpack_full_y = int(config['detect_range_backpack_full_y'])

# Function to simulate a timed mouse click at given coords
def click_timed(x, y, min_time, max_time):
    win32api.SetCursorPos((x, y))
    time.sleep(random.uniform(min_time, max_time))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(random.uniform(min_time, max_time))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# Simulate a click at X/Y coords
def click(x, y):
    click_timed(x, y, 0.1, 0.25)

# In Fishing Simulator, the indicator of the hook being in the water is a blue bubble column
def check_bubbles_on_screen():
    screenshot = pyautogui.screenshot()
    
    L_corner = middle_screen_x - detect_range_bubble_x
    R_corner = middle_screen_x + detect_range_bubble_x
    T_corner = middle_screen_y - detect_range_bubble_y
    B_corner = middle_screen_y + detect_range_bubble_y

    # This is naively taken from a in-game screenshot
    # These are approximation bounds for the green
    lower_red_bound = 60
    upper_red_bound = 70
    lower_green_bound = 245
    upper_green_bound = 255
    lower_blue_bound = 230
    upper_blue_bound = 240
 
    # Fast check if the bubble mark is in the middle of the screen
    pixel = screenshot.getpixel((middle_screen_x, middle_screen_y));
    expected_R = pixel[0] 
    expected_G = pixel[1] 
    expected_B = pixel[2]
    if compare_color_range(expected_R, expected_G, expected_B, lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
        return True
    
    # If not the bubble mark can still be there,
    # but is offset because of suboptimal camera placement
    # We scan a square range to check for it's existence 
    for x in range(L_corner, R_corner):
        for y in range(T_corner, B_corner):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
                return True

    # If it's not found by now, there probably isn't one
    return False

# Approximate if the color given by R/G/B matches the colors of the clickable fishing arc
def compare_color_range(R, G, B, min_r, max_r, min_g, max_g, min_b, max_b):
    return ((R >= min_r and R <= max_r) and # Check if red component is in bounds 
            (G >= min_g and G <= max_g) and # Check if blue component is in bounds
            (B >= min_b and B <= max_b))    # Check if green component is in bounds

# In Fishing Simulator, the red-green fishing arc is in the middle 
# and means that we are in a minigame
def check_fishing_minigame_arc_is_on_screen():
    minigame_arc_x = int(width / 2)
    minigame_arc_y = 3 * int(height / 4)
    
    screenshot = pyautogui.screenshot()

    L_corner = minigame_arc_x - detect_range_arc_x
    R_corner = minigame_arc_x + detect_range_arc_x 
    T_corner = minigame_arc_y - detect_range_arc_y
    B_corner = minigame_arc_y + detect_range_arc_y

    possible_arc_pixel = screenshot.getpixel((minigame_arc_x, minigame_arc_y))
    expected_R = possible_arc_pixel[0] 
    expected_G = possible_arc_pixel[1] 
    expected_B = possible_arc_pixel[2]
 
     # This is naively taken from a in-game screenshot
    # These are approximation bounds for the green
    lower_green_RB_bound = 80
    upper_green_RB_bound = 90
    lower_green_bound = 240
    upper_green_bound = 255

    # Fast check if the arc is in the expected screenspace
    if compare_color_range(expected_R, expected_G, expected_B, lower_green_RB_bound, upper_green_RB_bound, lower_green_bound, upper_green_bound, lower_green_RB_bound, upper_green_RB_bound):    
        return True
    
    # If not the fishing arc mark can still be there,
    # but is offset because of suboptimal camera placement
    # We scan a square range to check for it's existence 
    for x in range(L_corner, R_corner):
        for y in range(T_corner, B_corner):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_green_RB_bound, upper_green_RB_bound, lower_green_bound, upper_green_bound, lower_green_RB_bound, upper_green_RB_bound):    
                return True

    # If it's not found by now, there probably isn't one
    return False

# In Fishing Simulator, a indication that the backpack is full is a purple/pink text
# in the middle of the screen
def check_backpack_is_full():
    screenshot = pyautogui.screenshot()

    screen_60_percent_down = int(0.6 * height)

    L_corner = middle_screen_x - detect_range_backpack_full_x
    R_corner = middle_screen_x + detect_range_backpack_full_x
    T_corner = screen_60_percent_down - detect_range_backpack_full_y
    B_corner = screen_60_percent_down + detect_range_backpack_full_y

    # This is naively taken from a in-game screenshot
    # These are approximation bounds for the green
    lower_red_bound = 245
    upper_red_bound = 255
    lower_green_bound = 0
    upper_green_bound = 10
    lower_blue_bound = 95
    upper_blue_bound = 105
 
    # Fast check if the pink/purple text is in the middle of the screen
    pixel = screenshot.getpixel((middle_screen_x, middle_screen_y));
    expected_R = pixel[0] 
    expected_G = pixel[1] 
    expected_B = pixel[2]
    if compare_color_range(expected_R, expected_G, expected_B, lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
        return True
    
    # If not the pink/purple text can still be there,
    # but is offset because of suboptimal camera placement
    # We scan a square range to check for it's existence 
    for x in range(L_corner, R_corner):
        for y in range(T_corner, B_corner):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
                return True

    # If it's not found by now, there probably isn't one
    return False

def print_with_time(message):
    timestamp = time.strftime("%H:%M:%S", time.gmtime())
    print("[" + timestamp + "]", message)

def print_with_time_debug(message):
    if debug_mode:
        print_with_time(f"[debug] {message}")

# Flags
time_till_reset_state  = reset_state_cooldown_s
is_in_fishing_minigame = False
thrown_hook            = False
paused_script          = False
script_caught_fish     = 0
start_timestamp        = 0
stop_timestamp         = 0

if debug_mode:
    print_with_time_debug(f"roblox-fishing-simulator debug automation script {load_version()} by Vivit")
else:
    print_with_time(f"roblox-fishing-simulator automation script {load_version()} by Vivit")

print_with_time(f"Depending on your fishing rod upgrades, this script averages at about 300-360 fish/hour or 1 fish/10-12s")
print_with_time(f"Press and hold '{quit_script_hotkey}' to stop the script")
print_with_time(f"Press and hold '{pause_script_hotkey}' to pause the script")
print_with_time(f"Press and hold '{reset_script_hotkey}' to reset the script")
print_with_time(f"Press and hold '{show_info_hotkey}' to show fishing info\n")
print_with_time(f"You have {start_script_countdown_s} seconds to prepare the Roblox Fishing Simulator game\n")
time.sleep(3)

# Countdown to start
for second in range(0, start_script_countdown_s):
    time_left = start_script_countdown_s - second
    if time_left <= 5:
        print_with_time(f"Starting script in {time_left} seconds")
    time.sleep(1)

start_timestamp = time.time()

# For pretty terminal formatting
print("")

while not keyboard.is_pressed(quit_script_hotkey): 
    # =============================================
    # Print fishing info
    # =============================================

    if keyboard.is_pressed(show_info_hotkey):
        print("===== Current fishing session info =====")
        # Some info after fishing
        stop_timestamp   = time.time()
        elapsed_time_s   = stop_timestamp - start_timestamp
        seconds_per_fish = int(elapsed_time_s / script_caught_fish)
        fish_per_hour    = int(script_caught_fish * 60 * 60 / elapsed_time_s)
        print_with_time(f"Caught {script_caught_fish} fish since script began fishing")
        print_with_time(f"Average pace 1 fish/{seconds_per_fish} second(s) | {fish_per_hour} fish/hour")
        print("===== Current fishing session info =====")

    # =============================================
    # Handle broken state
    # 
    # Every now and then the state may break
    # We fix this by resetting it every now and then
    # when the player is idle
    # =============================================
    
    # Manual reset state
    if keyboard.is_pressed(reset_script_hotkey):
        print_with_time("Manual reset state")
        time_till_reset_state = reset_state_cooldown_s
        thrown_hook = False
        is_in_fishing_minigame = False
        paused_script = False
        time.sleep(1)
        continue

    # =============================================
    # Check for script pause
    # =============================================

    # Check if user wants to pause
    if not paused_script and keyboard.is_pressed(pause_script_hotkey):
        print_with_time("Paused the script")
        paused_script = True
        time.sleep(1)

    # Check if user wants to unpause
    elif paused_script and keyboard.is_pressed(pause_script_hotkey):
        print_with_time("Unpaused the script")
        paused_script = False
        time.sleep(1) 

    if paused_script:
        sleep(1)
        continue

    # =============================================
    # Throw hook or start fishing minigame
    # =============================================        

    # Visible bubbles and not in minigame means that we haven't yet started a minigame
    if check_bubbles_on_screen() and not is_in_fishing_minigame:
        click(middle_screen_x, middle_screen_y)
        
        if check_fishing_minigame_arc_is_on_screen():
            print_with_time_debug("Start fishing minigame")
            is_in_fishing_minigame = True

    # If there is no bubbles on the screen then throw the fishing rod's hook
    if not check_bubbles_on_screen() and not is_in_fishing_minigame and not thrown_hook:
        click(middle_screen_x, middle_screen_y)

        if check_backpack_is_full():
            print_with_time("Pausing the script - backpack is full")
            paused_script = True
        else:
            print_with_time_debug("Throw hook")
            thrown_hook = True
    
    # If not in fishing minigame despite some time then reset state because it's probably broken
    if not thrown_hook and not check_bubbles_on_screen() and not is_in_fishing_minigame and not check_fishing_minigame_arc_is_on_screen():
        time_till_reset_state -= 1
        if time_till_reset_state == 0:
            print_with_time_debug(f"Automatic reset every {reset_state_cooldown_s}")
            time_till_reset_state = reset_state_cooldown_s
            thrown_hook = False
            is_in_fishing_minigame = False
            paused_script = False
        
        time.sleep(1)
        continue

    # =============================================
    # Play minigame 
    # Here the user is playing
    # =============================================

    while is_in_fishing_minigame and thrown_hook and check_fishing_minigame_arc_is_on_screen():
        click_timed(middle_screen_x, middle_screen_y, fishing_minigame_click_min_s, fishing_minigame_click_max_s)

    if is_in_fishing_minigame and thrown_hook and not check_fishing_minigame_arc_is_on_screen():
        print_with_time_debug("End fishing minigame")

        is_in_fishing_minigame = False
        thrown_hook = False
        time_till_reset_state = reset_state_cooldown_s
        script_caught_fish += 1