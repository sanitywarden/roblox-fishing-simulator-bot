import time
import random
import yaml
import mss
import numpy as np
import pyautogui
from pynput import keyboard
import Quartz.CoreGraphics as CG

# Native Mac click
def mac_click(x, y, duration):
    point = CG.CGPointMake(x, y)
    down = CG.CGEventCreateMouseEvent(None, CG.kCGEventLeftMouseDown, point, CG.kCGMouseButtonLeft)
    up = CG.CGEventCreateMouseEvent(None, CG.kCGEventLeftMouseUp, point, CG.kCGMouseButtonLeft)
    
    CG.CGEventPost(CG.kCGHIDEventTap, down)
    time.sleep(duration)
    CG.CGEventPost(CG.kCGHIDEventTap, up)
    time.sleep(duration)

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
                      (245, 255), (0, 10), (95, 105))

def print_with_time(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def print_with_time_debug(message):
    if debug_mode: 
        print_with_time(f"[debug] {message}")

time_till_reset_state  = reset_state_cooldown_s
is_in_fishing_minigame = False
thrown_hook            = False
paused_script          = False
script_caught_fish     = 0
start_timestamp        = 0

if debug_mode:
    print_with_time_debug(f"roblox-fishing-simulator-macos debug automation script {load_version()} by Vivit")
else:
    print_with_time(f"roblox-fishing-simulator-macos automation script {load_version()} by Vivit")

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
        thrown_hook = False
        is_in_fishing_minigame = False
        paused_script = False
        time.sleep(1)
        continue

    # 3. Pause Script
    if tracker.is_pressed(pause_script_hotkey):
        paused_script = not paused_script
        print_with_time("Paused the script" if paused_script else "Unpaused the script")
        time.sleep(1)

    if paused_script:
        time.sleep(1)
        continue

    # =============================================
    # Throw hook or start fishing minigame
    # =============================================

    bubbles_visible = check_bubbles_on_screen()
    if bubbles_visible and not is_in_fishing_minigame:
        click(middle_screen_x, middle_screen_y)
    
        if check_fishing_minigame_arc_is_on_screen():
            print_with_time_debug("Start fishing minigame")
            is_in_fishing_minigame = True

    if not bubbles_visible and not is_in_fishing_minigame and not thrown_hook:
        click(middle_screen_x, middle_screen_y)
        
        if check_backpack_is_full():
            print_with_time("Pausing the script - backpack is full")
            paused_script = True
        else:
            print_with_time_debug("Throw hook")
            thrown_hook = True

    # 5. Automatic reset state
    if not thrown_hook and not bubbles_visible and not is_in_fishing_minigame and not check_fishing_minigame_arc_is_on_screen():
        time_till_reset_state -= 1
        if time_till_reset_state <= 0:
            print_with_time_debug(f"Automatic reset every {reset_state_cooldown_s}")
            time_till_reset_state = reset_state_cooldown_s
            thrown_hook = False
            is_in_fishing_minigame = False
            paused_script = False
        time.sleep(1)
        continue

    # 6. Play minigame
    while is_in_fishing_minigame and thrown_hook and check_fishing_minigame_arc_is_on_screen():
        click_timed(middle_screen_x, middle_screen_y, fishing_minigame_click_min_s, fishing_minigame_click_max_s)
        if tracker.is_pressed(quit_script_hotkey): break

    if is_in_fishing_minigame and thrown_hook and not check_fishing_minigame_arc_is_on_screen():
        print_with_time_debug("End fishing minigame")
        is_in_fishing_minigame = False
        thrown_hook = False
        time_till_reset_state = reset_state_cooldown_s
        script_caught_fish += 1

    time.sleep(0.1)