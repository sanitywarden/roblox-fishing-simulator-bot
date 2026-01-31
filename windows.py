from pydoc import cli
from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api, win32con
import pydirectinput
import yaml
import mss
import ctypes
import numpy as np

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
sell_fish_hotkey             = config['sell_fish_hotkey']
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

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x / width * 65535.0), int(y / height * 65535.0))
    time.sleep(0.05)

    time.sleep(random.uniform(min_time, max_time))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(random.uniform(min_time, max_time))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# Simulate a click at X/Y coords
def click(x, y):
    click_timed(x, y, 0.1, 0.25)

def click_random(min_time, max_time):
    x = int(middle_screen_x + random.uniform(-16, 16))
    y = int(middle_screen_y + random.uniform(-16, 16))
    click_timed(x, y, min_time, max_time)

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

def press_e():
    # Pressing enter has to be very low level for Roblox to recognise it as legit
    MapVirtualKey      = ctypes.windll.user32.MapVirtualKeyW
    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_KEYUP    = 0x0002
    scancode           = 0x12 # E

    ctypes.windll.user32.keybd_event(0, scancode, KEYEVENTF_SCANCODE, 0)
    time.sleep(random.uniform(fishing_minigame_click_min_s, fishing_minigame_click_max_s))
    ctypes.windll.user32.keybd_event(0, scancode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

def find_color_in_roi(r_bounds, g_bounds, b_bounds, x_ratio, y_ratio, box_ratio=0.1):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        
        sct_img = sct.grab(monitor)
        full_img = np.array(sct_img)
        
        f_h, f_w = full_img.shape[:2]

        center_x, center_y = int(f_w * x_ratio), int(f_h * y_ratio)
        
        offset_x, offset_y = int(f_w * box_ratio), int(f_h * box_ratio)

        x1, x2 = max(0, center_x - offset_x), min(f_w, center_x + offset_x)
        y1, y2 = max(0, center_y - offset_y), min(f_h, center_y + offset_y)

        roi = full_img[y1:y2, x1:x2]

        mask = (
            (roi[:, :, 2] >= r_bounds[0]) & (roi[:, :, 2] <= r_bounds[1]) &
            (roi[:, :, 1] >= g_bounds[0]) & (roi[:, :, 1] <= g_bounds[1]) &
            (roi[:, :, 0] >= b_bounds[0]) & (roi[:, :, 0] <= b_bounds[1])
        )

        coords = np.where(mask)

        if len(coords[0]) > 0:
            avg_y = int(np.mean(coords[0]))
            avg_x = int(np.mean(coords[1]))
            
            phys_x = avg_x + x1
            phys_y = avg_y + y1

            return int(phys_x), int(phys_y)
            
    return None

def find_sell_button_coords():
    r_range = (0, 0)
    g_range = (180, 220)
    b_range = (200, 255)
    return find_color_in_roi(r_range, g_range, b_range, 0.72, 0.45, box_ratio=0.1)

def find_sell_everything_button_coords():
    r_range = (75, 90)
    g_range = (210, 255)
    b_range = (30, 70)
    return find_color_in_roi(r_range, g_range, b_range, 0.60, 0.405, box_ratio=0.05)

# Flags
time_till_reset_state  = reset_state_cooldown_s
is_in_fishing_minigame = False
thrown_hook            = False
paused_script          = False
in_shop                = False
force_sell_fish        = False
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
print_with_time(f"Press and hold '{show_info_hotkey}' to show fishing info")
print_with_time(f"Press and hold '{sell_fish_hotkey}' to force sell fish\n")
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

    if keyboard.is_pressed(sell_fish_hotkey):
        force_sell_fish = True
        if force_sell_fish:
            print_with_time_debug("Force sell fish")

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
        click_random(0.1, 0.2)
        
        if check_fishing_minigame_arc_is_on_screen():
            print_with_time_debug("Start fishing minigame")
            is_in_fishing_minigame = True

    # If there is no bubbles on the screen then throw the fishing rod's hook
    if not check_bubbles_on_screen() and not is_in_fishing_minigame and not thrown_hook:
        click_random(0.1, 0.2)

        backpack_full = check_backpack_is_full()
        if force_sell_fish or backpack_full:
            # Try opening the shop a few times to see if it's nearby
            press_e()

            # Wait for menu to open
            time.sleep(1)

            # If the menu opened, it should be visible by now
            # Check if there is the blue/cyan sell button on the screen
            button_coords = find_sell_button_coords()
            if (not in_shop and button_coords is not None):
                in_shop = True

                # Might be fishing, click to stop fishing
                click(middle_screen_x, middle_screen_y)

                x1 = button_coords[0]
                y1 = button_coords[1]
                
                click(x1, y1)
                time.sleep(1)

                sell_everything_button_coords = find_sell_everything_button_coords()
                if (sell_everything_button_coords is not None):
                    in_sell_everything = True
                    
                    x2 = sell_everything_button_coords[0]
                    y2 = sell_everything_button_coords[1]
                    
                    # Click button to sell everything
                    click(x2, y2)
                    time.sleep(0.1)

                    # Click button to confirm the sale
                    click(x2, y2)
                    time.sleep(0.1)

                    in_sell_everything = False
                
                current_fish = 0

                thrown_hook = False
                is_in_fishing_minigame = False

                in_shop = False
                force_sell_fish = False
            
            else:
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
        click_random(fishing_minigame_click_min_s, fishing_minigame_click_max_s)

    if is_in_fishing_minigame and thrown_hook and not check_fishing_minigame_arc_is_on_screen():
        print_with_time_debug("End fishing minigame")

        is_in_fishing_minigame = False
        thrown_hook = False
        time_till_reset_state = reset_state_cooldown_s
        script_caught_fish += 1