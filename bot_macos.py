import pyautogui
import time
import random
import yaml
import os
from pynput import keyboard, mouse

mouse_ctrl = mouse.Controller()
keys_pressed = {}

def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key).replace("Key.", "")
    keys_pressed[k] = True

def on_release(key):
    try:
        k = key.char
    except AttributeError:
        k = str(key).replace("Key.", "")
    keys_pressed[k] = False

def is_pressed(k):
    return keys_pressed.get(k, False)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

width, height = pyautogui.size()
middle_screen_x = int(width / 2)
middle_screen_y = int(height / 2)

def load_yaml_settings():
    with open('./config.yaml', 'r') as file:
        return yaml.safe_load(file)

def load_version(): 
    try:
        with open('./version.txt', 'r') as file:
            return file.read()
    except:
        return "version not found"

config = load_yaml_settings()
if config is None:
    exit(1)

debug_mode                   = int(config['debug_mode'])
start_script_countdown_s     = int(config['start_script_countdown_s'])
reset_state_cooldown_s       = int(config['reset_state_cooldown_s'])
quit_script_hotkey           = str(config['quit_script_hotkey'])
pause_script_hotkey          = str(config['pause_script_hotkey'])
reset_script_hotkey          = str(config['reset_script_hotkey'])
show_info_hotkey             = str(config['show_info_hotkey'])
fishing_minigame_click_min_s = float(config['fishing_minigame_click_min_s'])
fishing_minigame_click_max_s = float(config['fishing_minigame_click_max_s'])
detect_range_bubble_x        = int(config['detect_range_bubble_x'])
detect_range_bubble_y        = int(config['detect_range_bubble_y'])
detect_range_arc_x           = int(config['detect_range_arc_x'])
detect_range_arc_y           = int(config['detect_range_arc_y'])
detect_range_backpack_full_x = int(config['detect_range_backpack_full_x'])
detect_range_backpack_full_y = int(config['detect_range_backpack_full_y'])

def click_timed(x, y, min_time, max_time):
    mouse_ctrl.position = (x, y)
    time.sleep(random.uniform(min_time, max_time))
    mouse_ctrl.press(mouse.Button.left)
    time.sleep(0.05)
    mouse_ctrl.release(mouse.Button.left)
    time.sleep(random.uniform(min_time, max_time))

def click(x, y):
    click_timed(x, y, 0.1, 0.25)

def compare_color_range(R, G, B, min_r, max_r, min_g, max_g, min_b, max_b):
    return ((R >= min_r and R <= max_r) and 
            (G >= min_g and G <= max_g) and 
            (B >= min_b and B <= max_b))

def check_bubbles_on_screen():
    screenshot = pyautogui.screenshot()
    L_corner = middle_screen_x - detect_range_bubble_x
    R_corner = middle_screen_x + detect_range_bubble_x
    T_corner = middle_screen_y - detect_range_bubble_y
    B_corner = middle_screen_y + detect_range_bubble_y
    
    lower_red_bound, upper_red_bound = 60, 70
    lower_green_bound, upper_green_bound = 245, 255
    lower_blue_bound, upper_blue_bound = 230, 240
 
    pixel = screenshot.getpixel((middle_screen_x, middle_screen_y))
    if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
        return True
    
    for x in range(L_corner, R_corner, 2):
        for y in range(T_corner, B_corner, 2):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
                return True
    return False

def check_fishing_minigame_arc_is_on_screen():
    minigame_arc_x = int(width / 2)
    minigame_arc_y = 3 * int(height / 4)
    screenshot = pyautogui.screenshot()
    L_corner = minigame_arc_x - detect_range_arc_x
    R_corner = minigame_arc_x + detect_range_arc_x 
    T_corner = minigame_arc_y - detect_range_arc_y
    B_corner = minigame_arc_y + detect_range_arc_y

    lower_green_RB_bound, upper_green_RB_bound = 80, 90
    lower_green_bound, upper_green_bound = 240, 255

    pixel = screenshot.getpixel((minigame_arc_x, minigame_arc_y))
    if compare_color_range(pixel[0], pixel[1], pixel[2], lower_green_RB_bound, upper_green_RB_bound, lower_green_bound, upper_green_bound, lower_green_RB_bound, upper_green_RB_bound):    
        return True
    
    for x in range(L_corner, R_corner, 2):
        for y in range(T_corner, B_corner, 2):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_green_RB_bound, upper_green_RB_bound, lower_green_bound, upper_green_bound, lower_green_RB_bound, upper_green_RB_bound):    
                return True
    return False

def check_backpack_is_full():
    screenshot = pyautogui.screenshot()
    screen_60_percent_down = int(0.6 * height)
    L_corner = middle_screen_x - detect_range_backpack_full_x
    R_corner = middle_screen_x + detect_range_backpack_full_x
    T_corner = screen_60_percent_down - detect_range_backpack_full_y
    B_corner = screen_60_percent_down + detect_range_backpack_full_y

    lower_red_bound, upper_red_bound = 245, 255
    lower_green_bound, upper_green_bound = 0, 10
    lower_blue_bound, upper_blue_bound = 95, 105
 
    pixel = screenshot.getpixel((middle_screen_x, middle_screen_y))
    if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
        return True
    
    for x in range(L_corner, R_corner, 2):
        for y in range(T_corner, B_corner, 2):
            pixel = screenshot.getpixel((x, y))
            if compare_color_range(pixel[0], pixel[1], pixel[2], lower_red_bound, upper_red_bound, lower_green_bound, upper_green_bound, lower_blue_bound, upper_blue_bound):
                return True
    return False

def print_with_time(message):
    timestamp = time.strftime("%H:%M:%S", time.gmtime())
    print("[" + timestamp + "]", message)

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
    print_with_time_debug(f"roblox-fishing-simulator debug automation script {load_version()} by Vivit")
else:
    print_with_time(f"roblox-fishing-simulator automation script {load_version()} by Vivit")

print_with_time(f"Press and hold '{quit_script_hotkey}' to stop the script")
time.sleep(3)

for second in range(0, start_script_countdown_s):
    time_left = start_script_countdown_s - second
    if time_left <= 5:
        print_with_time(f"Starting script in {time_left} seconds")
    time.sleep(1)

start_timestamp = time.time()
print("")

while not is_pressed(quit_script_hotkey): 
    if is_pressed(show_info_hotkey):
        print("===== Current fishing session info =====")
        elapsed_time_s = time.time() - start_timestamp
        if script_caught_fish > 0:
            seconds_per_fish = int(elapsed_time_s / script_caught_fish)
            fish_per_hour = int(script_caught_fish * 3600 / elapsed_time_s)
            print_with_time(f"Caught {script_caught_fish} fish")
            print_with_time(f"Average pace 1 fish/{seconds_per_fish}s | {fish_per_hour} fish/h")
        print("===== Current fishing session info =====")
        time.sleep(0.5)

    if is_pressed(reset_script_hotkey):
        print_with_time("Manual reset state")
        time_till_reset_state = reset_state_cooldown_s
        thrown_hook, is_in_fishing_minigame, paused_script = False, False, False
        time.sleep(1)
        continue

    if is_pressed(pause_script_hotkey):
        paused_script = not paused_script
        print_with_time("Paused" if paused_script else "Unpaused")
        time.sleep(1)

    if paused_script:
        time.sleep(1)
        continue

    if check_bubbles_on_screen() and not is_in_fishing_minigame:
        click(middle_screen_x, middle_screen_y)
        if check_fishing_minigame_arc_is_on_screen():
            print_with_time_debug("Start fishing minigame")
            is_in_fishing_minigame = True

    if not check_bubbles_on_screen() and not is_in_fishing_minigame and not thrown_hook:
        click(middle_screen_x, middle_screen_y)
        if check_backpack_is_full():
            print_with_time("Pausing the script - backpack is full")
            paused_script = True
        else:
            print_with_time_debug("Throw hook")
            thrown_hook = True
    
    if not thrown_hook and not check_bubbles_on_screen() and not is_in_fishing_minigame and not check_fishing_minigame_arc_is_on_screen():
        time_till_reset_state -= 1
        if time_till_reset_state <= 0:
            print_with_time_debug(f"Automatic reset every {reset_state_cooldown_s}")
            time_till_reset_state = reset_state_cooldown_s
            thrown_hook, is_in_fishing_minigame, paused_script = False, False, False
        time.sleep(1)
        continue

    while is_in_fishing_minigame and thrown_hook and check_fishing_minigame_arc_is_on_screen():
        click_timed(middle_screen_x, middle_screen_y, fishing_minigame_click_min_s, fishing_minigame_click_max_s)

    if is_in_fishing_minigame and thrown_hook and not check_fishing_minigame_arc_is_on_screen():
        print_with_time_debug("End fishing minigame")
        is_in_fishing_minigame, thrown_hook = False, False
        time_till_reset_state = reset_state_cooldown_s
        script_caught_fish += 1
    
    time.sleep(0.1)

listener.stop()