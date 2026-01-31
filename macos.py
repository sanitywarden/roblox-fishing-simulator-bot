import time
import random
import yaml
import mss
import numpy as np
import pyautogui
import Quartz.CoreGraphics as CG
from pynput import keyboard

# After selling fish there is issue with continuing
# Automatic reset

# Native Mac click
def mac_click(x, y, duration):
    point = CG.CGPointMake(x, y)
    
    move = CG.CGEventCreateMouseEvent(None, CG.kCGEventMouseMoved, point, CG.kCGMouseButtonLeft)
    CG.CGEventPost(CG.kCGHIDEventTap, move)

    time.sleep(0.05)
    
    down = CG.CGEventCreateMouseEvent(None, CG.kCGEventLeftMouseDown, point, CG.kCGMouseButtonLeft)
    up = CG.CGEventCreateMouseEvent(None, CG.kCGEventLeftMouseUp, point, CG.kCGMouseButtonLeft)

    CG.CGEventPost(CG.kCGHIDEventTap, down)
    time.sleep(duration)
    CG.CGEventPost(CG.kCGHIDEventTap, up)
    time.sleep(0.1)

# Code for E on macOS keyboard
MAC_keyboard_E = 14

def mac_keypress(key_code, duration):
    push = CG.CGEventCreateKeyboardEvent(None, key_code, True)
    release = CG.CGEventCreateKeyboardEvent(None, key_code, False)
    
    CG.CGEventPost(CG.kCGHIDEventTap, push)
    time.sleep(duration)
    CG.CGEventPost(CG.kCGHIDEventTap, release)

class KeyTracker:
    def __init__(self):
        self.pressed_keys = set()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try: k = key.char
        except AttributeError: k = str(key)
        if k: self.pressed_keys.add(k)

    def on_release(self, key):
        try: k = key.char
        except AttributeError: k = str(key)
        if k in self.pressed_keys: self.pressed_keys.remove(k)

    def is_pressed(self, key_name):
        return key_name in self.pressed_keys

tracker = KeyTracker()

# Retina on Mac has weird shit going on with it's pixel density
# This makes sure to find correct scale at which to detect game features
with mss.mss() as sct:
    monitor = sct.monitors[1]
    phys_width = monitor['width']
    logic_width, logic_height = pyautogui.size()
    scale = phys_width / logic_width

middle_screen_x = int(logic_width / 2)
middle_screen_y = int(logic_height / 2)

def load_yaml_settings():
    try:
        with open('./config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except: 
        return None

def load_version():
    try:
        with open('./version.txt', 'r') as file: 
            version = file.read()
            return version
    except: 
        return "version.txt file not found"

config = load_yaml_settings()
if config is None:
    print("Roblox fishing bot requires the 'config.yaml' file but it doesn't exist")
    exit(1)

# From config
debug_mode                   = int(config['debug_mode'])
start_script_countdown_s     = int(config['start_script_countdown_s'])
reset_state_cooldown_s       = int(config['reset_state_cooldown_s'])
quit_script_hotkey           = config['quit_script_hotkey']
pause_script_hotkey          = config['pause_script_hotkey']
reset_script_hotkey          = config['reset_script_hotkey']
show_info_hotkey             = config['show_info_hotkey']
force_sell_fish_hotkey       = config['sell_fish_hotkey']
fishing_minigame_click_min_s = float(config['fishing_minigame_click_min_s'])
fishing_minigame_click_max_s = float(config['fishing_minigame_click_max_s'])
detect_range_bubble_x        = int(config['detect_range_bubble_x'])
detect_range_bubble_y        = int(config['detect_range_bubble_y'])
detect_range_arc_x           = int(config['detect_range_arc_x'])
detect_range_arc_y           = int(config['detect_range_arc_y'])
detect_range_backpack_full_x = int(config['detect_range_backpack_full_x'])
detect_range_backpack_full_y = int(config['detect_range_backpack_full_y'])

def get_screenshot():
    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))

def compare_color_range(R, G, B, min_r, max_r, min_g, max_g, min_b, max_b):
    return (min_r <= R <= max_r and min_g <= G <= max_g and min_b <= B <= max_b)

def check_area(screenshot, center_x, center_y, range_x, range_y, r_bounds, g_bounds, b_bounds):
    # Adjust the size with correct scale due to Retina pixel density
    f_x = int(center_x * scale)
    f_y = int(center_y * scale)
    f_rx = int(range_x * scale)
    f_ry = int(range_y * scale)

    region = screenshot[max(0, f_y-f_ry):f_y+f_ry, max(0, f_x-f_rx):f_x+f_rx]
    if region.size == 0: return False
    
    # MSS format to BGRA: B=0, G=1, R=2
    r_mask = (region[:,:,2] >= r_bounds[0]) & (region[:,:,2] <= r_bounds[1])
    g_mask = (region[:,:,1] >= g_bounds[0]) & (region[:,:,1] <= g_bounds[1])
    b_mask = (region[:,:,0] >= b_bounds[0]) & (region[:,:,0] <= b_bounds[1])
    return np.any(r_mask & g_mask & b_mask)

def click(x, y):
    mac_click(x, y, duration=random.uniform(0.1, 0.2))

def click_random(x, y, min_time = 0.1, max_time = 0.2):
    mac_click(x + random.uniform(-8, 8), y + random.uniform(-8, 8), random.uniform(min_time, max_time))

def click_timed(x, y, min_time, max_time):
    mac_click(x, y, duration=random.uniform(min_time, max_time))

def check_bubbles_on_screen():
    screenshot = get_screenshot()
    return check_area(screenshot, middle_screen_x, middle_screen_y, detect_range_bubble_x, detect_range_bubble_y,
                      (120, 135), (245, 255), (230, 240))

def check_fishing_minigame_arc_is_on_screen():
    screenshot = get_screenshot()
    arc_y = 3 * int(logic_height / 4)
    return check_area(screenshot, middle_screen_x, arc_y, detect_range_arc_x, detect_range_arc_y,
                      (130, 140), (240, 255), (90, 110))

def check_backpack_is_full():
    screenshot = get_screenshot()
    y_pos = int(0.6 * logic_height)
    return check_area(screenshot, middle_screen_x, y_pos, detect_range_backpack_full_x, detect_range_backpack_full_y,
                      (230, 245), (40, 55), (95, 105))

def find_color_in_roi(r_bounds, g_bounds, b_bounds, x_ratio, y_ratio, box_ratio=0.1):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        full_img = np.array(sct.grab(monitor))
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
            
            phys_y = avg_y + y1
            phys_x = avg_x + x1

            return int(phys_x / scale), int(phys_y / scale)
            
    return None

def find_sell_button_coords():
    r_range = (80, 120)
    g_range = (140, 200)
    b_range = (200, 255)
    return find_color_in_roi(r_range, g_range, b_range, 0.735, 0.44, box_ratio=0.1)

def find_sell_everything_button_coords():
    r_range = (110, 140)
    g_range = (210, 255)
    b_range = (70, 130)
    return find_color_in_roi(r_range, g_range, b_range, 0.60, 0.405, box_ratio=0.05)

def print_with_time(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def print_with_time_debug(message):
    if debug_mode: 
        print_with_time(f"[debug] {message}")

time_till_reset_state  = reset_state_cooldown_s 
is_in_fishing_minigame = False
thrown_hook            = False
paused_script          = False
force_sell_fish        = False
in_shop                = False
in_sell_screen         = False
in_sell_everything     = False
script_caught_fish     = 0
current_fish           = 0
start_timestamp        = 0

if debug_mode:
    print_with_time_debug(f"roblox-fishing-simulator-macos debug automation script {load_version()} by Vivit")
else:
    print_with_time(f"roblox-fishing-simulator-macos automation script {load_version()} by Vivit")

print_with_time(f"Depending on your fishing rod upgrades, this script averages at about 300-360 fish/hour or 1 fish/10-12s")
print_with_time(f"Press and hold '{quit_script_hotkey}' to stop the script")
print_with_time(f"Press and hold '{pause_script_hotkey}' to pause the script")
print_with_time(f"Press and hold '{reset_script_hotkey}' to reset the script")
print_with_time(f"Press and hold '{show_info_hotkey}' to show fishing info")
print_with_time(f"Press and hold '{force_sell_fish_hotkey}' to force sell fish\n")
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

while not tracker.is_pressed(quit_script_hotkey):
    # 1. Info
    if tracker.is_pressed(show_info_hotkey):
        print("===== Current fishing session info =====")
        elapsed = time.time() - start_timestamp
        if script_caught_fish > 0:
            sec_per_fish = int(elapsed / script_caught_fish)
            fish_per_hr = int(script_caught_fish * 3600 / elapsed)
            print_with_time(f"Caught {script_caught_fish} fish. Avg pace: 1 fish/{sec_per_fish}s | {fish_per_hr}/h")
        print("===== Current fishing session info =====")
        time.sleep(1)

    # 2. Manual Reset
    if tracker.is_pressed(reset_script_hotkey):
        print_with_time("Manual reset state")
        time_till_reset_state = reset_state_cooldown_s
        paused_script          = False
        thrown_hook            = check_bubbles_on_screen()
        is_in_fishing_minigame = check_fishing_minigame_arc_is_on_screen()
        in_shop                = find_sell_button_coords()
        in_sell_everything     = find_sell_everything_button_coords() is not None
        force_sell_fish        = False
        time.sleep(1)
        continue

    # 2.1 Periodic reset
    if time_till_reset_state == 0:
        time_till_reset_state = reset_state_cooldown_s
        
        thrown_hook            = check_bubbles_on_screen()
        is_in_fishing_minigame = check_fishing_minigame_arc_is_on_screen()
        in_shop                = find_sell_button_coords()
        in_sell_everything     = find_sell_everything_button_coords() is not None
        force_sell_fish        = False


        print_with_time_debug(f"===== Performing automatic reset done every {reset_state_cooldown_s} seconds =====")
        print_with_time_debug(f"thrown_hook: {thrown_hook}")
        print_with_time_debug(f"is_in_fishing_minigame: {is_in_fishing_minigame}")
        print_with_time_debug(f"in_shop: {in_shop}")
        print_with_time_debug(f"in_sell_everything: {in_sell_everything}")
        print_with_time_debug("==========")

        time.sleep(1)

    # 3. Pause Script
    if tracker.is_pressed(pause_script_hotkey):
        paused_script = not paused_script
        print_with_time("Paused the script" if paused_script else "Unpaused the script")
        time.sleep(1)

    if paused_script:
        time.sleep(1)
        continue

    if tracker.is_pressed(force_sell_fish_hotkey):
        force_sell_fish = True
        if force_sell_fish:
            print_with_time_debug("Force sell fish")

    # =============================================
    # Throw hook or start fishing minigame
    # =============================================

    # Start fishing minigame
    bubbles_visible = check_bubbles_on_screen()
    if bubbles_visible and not is_in_fishing_minigame:
        click_random(middle_screen_x, middle_screen_y)
    
        if check_fishing_minigame_arc_is_on_screen():
            print_with_time_debug("Start fishing minigame")
            is_in_fishing_minigame = True

    # Throw hook
    elif not bubbles_visible and not is_in_fishing_minigame and not thrown_hook:
        click_random(middle_screen_x, middle_screen_y)

        backpack_full = check_backpack_is_full()
        if force_sell_fish or check_backpack_is_full():
            # Try opening the shop a few times to see if it's nearby
            mac_keypress(MAC_keyboard_E, 0.1)

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
                
                mac_click(x1, y1, 0.1)
                time.sleep(1)

                sell_everything_button_coords = find_sell_everything_button_coords()
                if (sell_everything_button_coords is not None):
                    in_sell_everything = True
                    x2 = sell_everything_button_coords[0]
                    y2 = sell_everything_button_coords[1]
                    
                    # Click button to sell everything
                    mac_click(x2, y2, 0.1)
                    time.sleep(0.1)

                    # Click button to confirm the sale
                    mac_click(x2, y2, 0.1)
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
            if time_till_reset_state < reset_state_cooldown_s:
                time_till_reset_state += reset_state_cooldown_s

    else:
        time_till_reset_state -= 1
        time.sleep(1)

    # Play minigame
    while is_in_fishing_minigame and thrown_hook and check_fishing_minigame_arc_is_on_screen():
        click_random(middle_screen_x, middle_screen_y, fishing_minigame_click_min_s, fishing_minigame_click_max_s)

    if is_in_fishing_minigame and thrown_hook and not check_fishing_minigame_arc_is_on_screen():
        print_with_time_debug("End fishing minigame")
        is_in_fishing_minigame = False
        thrown_hook = False
        time_till_reset_state = reset_state_cooldown_s
        script_caught_fish += 1
        current_fish += 1

    time.sleep(0.1)
