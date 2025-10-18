# -*- coding:utf-8 -*-
# Emoji OS Zero v0.2.7
import time
import threading

# === Auto-detect environment ===
def is_raspberry_pi():
    """Detect if running on Raspberry Pi with LCD hardware"""
    try:
        # Check if we can import the LCD driver (only available on Pi with hardware)
        import LCD_1in44  # noqa: F401
        import LCD_Config  # noqa: F401
        import RPi.GPIO as GPIO  # noqa: F401
        import spidev  # noqa: F401
        return True
    except ImportError:
        return False

# === Import appropriate modules based on environment ===
if is_raspberry_pi():
    # Running on Raspberry Pi with actual LCD hardware
    from PIL import Image,ImageDraw,ImageFont,ImageColor
    import LCD_1in44
    import RPi.GPIO as GPIO  # noqa: F401
    print("Running on Raspberry Pi with LCD hardware")
else:
    # Running on laptop - use simulation
    from PIL import Image,ImageDraw,ImageFont,ImageColor
    import tkinter as tk
    from tkinter import ttk
    print("Running on laptop - using LCD simulation")

    class _DispStub:
        """Minimal stub to mimic Waveshare LCD API used by this script.
        Provides dimensions and no-op methods so the script can run on a PC.
        """
        # Pins (to satisfy attribute access in code if ever used)
        GPIO_KEY_UP_PIN = 6
        GPIO_KEY_DOWN_PIN = 19
        GPIO_KEY_LEFT_PIN = 5
        GPIO_KEY_RIGHT_PIN = 26
        GPIO_KEY_PRESS_PIN = 13
        GPIO_KEY1_PIN = 21
        GPIO_KEY2_PIN = 20
        GPIO_KEY3_PIN = 16

        def __init__(self):
            self.width = 128
            self.height = 128
            self.simulation_window = None
            self.simulation_label = None

        def LCD_Init(self, *_args, **_kwargs):
            return None

        def LCD_Clear(self):
            return None

        def LCD_ShowImage(self, image, *_args, **_kwargs):
            # Show image in tkinter window on laptop
            if not self.simulation_window:
                self._create_simulation_window()
            
            if self.simulation_label:
                # Scale image for better visibility
                scale_factor = 4
                scaled_image = image.resize((self.width * scale_factor, self.height * scale_factor), Image.NEAREST)
                
                # Convert PIL image to PhotoImage
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(scaled_image)
                self.simulation_label.config(image=photo)
                self.simulation_label.image = photo  # Keep a reference
            return None

        def digital_read(self, *_args, **_kwargs):
            # Always return not pressed on laptop
            return 1

        def module_exit(self):
            if self.simulation_window:
                self.simulation_window.destroy()
            return None

        def _create_simulation_window(self):
            """Create tkinter simulation window"""
            self.simulation_window = tk.Tk()
            self.simulation_window.title("Emoji OS Zero - LCD Simulation")
            
            # Create label to display image
            self.simulation_label = tk.Label(self.simulation_window)
            self.simulation_label.pack()
            
            # Add info text
            info_label = tk.Label(self.simulation_window, text=f"Simulated {self.width}x{self.height} LCD Display (scaled 4x)")
            info_label.pack()
            
            # Add control info
            control_label = tk.Label(self.simulation_window, text="Controls: Left=KEY1, Down=KEY2, Right=KEY3, Up/Down=Menu, Enter=Center")
            control_label.pack()
            
            # Add status label
            self.status_label = tk.Label(self.simulation_window, text="Menu: 0, State: none, Pos: 0, Neg: 0")
            self.status_label.pack()
            
            # Add close button
            close_button = tk.Button(self.simulation_window, text="Close", command=self.simulation_window.destroy)
            close_button.pack()
            
            # Bind keyboard events
            self.simulation_window.bind('<Key>', self._on_key_press)
            self.simulation_window.focus_set()  # Make sure window can receive key events

        def _on_key_press(self, event):
            """Handle keyboard input for simulation"""
            global menu, pos, neg, state, prev_menu, prev_pos, prev_neg, prev_state
            
            if event.keysym == 'Up':
                reset_prev()  # Clear previous state when navigating
                if state == "none":
                    state = "start"
                elif state == "start":
                    menu = (menu - 1) % 4
                    check_menu()
                elif state == "choosing":
                    # In choosing mode, UP/DOWN should cycle through left side emojis (positive)
                    pos = (pos - 1) % 5
                    if pos == 0:
                        pos = 4
                    neg = 0
                    check_pos()
                draw_display()
                print('Up - Menu:', menu, 'Pos:', pos, 'Neg:', neg, 'State:', state)
                
            elif event.keysym == 'Down':  # KEY2 (Menu/Confirm)
                reset_prev()  # Clear previous state when navigating menus
                if state == "start":
                    menu = (menu + 1) % 4
                    check_menu()
                elif state == "none":
                    state = "start"
                elif state == "choosing":
                    # Show selected emoji and trigger appropriate animation
                    print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                    # Start animation in a separate thread
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    # Don't reset state here - let animation handle it
                else:
                    draw_display()
                draw_display()
                print('KEY2 - Menu:', menu, 'State:', state)
                
            elif event.keysym == 'Left':  # KEY1 (Positive)
                print('debug KEY1 - menu:', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
                
                # Try toggle or replay previous if available
                if prev_state == "done":
                    if prev_neg > 0:
                        # Toggle from previous negative to positive
                        pos = prev_neg
                        neg = 0
                        menu = prev_menu
                        print('KEY1 - Toggle from neg to pos, menu:', menu, "pos", pos, "neg", neg)
                        animation_thread = threading.Thread(target=start_emoji_animation)
                        animation_thread.daemon = True
                        animation_thread.start()
                        draw_display()
                        # Update status label
                        if hasattr(self, 'status_label') and self.status_label:
                            self.status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")
                        return
                    elif prev_pos > 0:
                        # Replay previous positive
                        pos = prev_pos
                        neg = 0
                        menu = prev_menu
                        print('KEY1 - Replay prev pos, menu:', menu, "pos", pos, "neg", neg)
                        animation_thread = threading.Thread(target=start_emoji_animation)
                        animation_thread.daemon = True
                        animation_thread.start()
                        draw_display()
                        # Update status label
                        if hasattr(self, 'status_label') and self.status_label:
                            self.status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")
                        return

                # Fallback to regular logic
                if state == "choosing":
                    pos = (pos + 1) % 5
                    if pos == 0:
                        pos = 1
                    neg = 0
                    check_pos()
                elif state == "start":
                    state = "choosing"
                    pos = 1
                    neg = 0
                elif state == "none":
                    state = "choosing"
                    pos = 1
                    neg = 0
                draw_display()
                print('KEY1 - Positive:', pos, 'State:', state)
                
            elif event.keysym == 'Right':  # KEY3 (Negative)
                print('debug KEY3 - menu:', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
                
                # First, attempt the "toggle / replay previous" case if just after an animation
                if prev_state == "done":
                    if prev_pos > 0:
                        # Toggle from previous positive to negative
                        neg = prev_pos
                        pos = 0
                        menu = prev_menu
                        print('KEY3 - Toggle from pos to neg, menu:', menu, "pos", pos, "neg", neg)
                        animation_thread = threading.Thread(target=start_emoji_animation)
                        animation_thread.daemon = True
                        animation_thread.start()
                        draw_display()
                        # Update status label
                        if hasattr(self, 'status_label') and self.status_label:
                            self.status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")
                        return
                    elif prev_neg > 0:
                        # Replay previous negative
                        neg = prev_neg
                        pos = 0
                        menu = prev_menu
                        print('KEY3 - Replay prev neg, menu:', menu, "pos", pos, "neg", neg)
                        animation_thread = threading.Thread(target=start_emoji_animation)
                        animation_thread.daemon = True
                        animation_thread.start()
                        draw_display()
                        # Update status label
                        if hasattr(self, 'status_label') and self.status_label:
                            self.status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")
                        return

                # If we didn't take the toggle/replay branch, do the normal logic
                if state == "choosing":
                    neg = (neg + 1) % 5
                    if neg == 0:
                        neg = 1
                    pos = 0
                    check_neg()
                elif state == "start":
                    state = "choosing"
                    neg = 1
                    pos = 0
                elif state == "none":
                    state = "choosing"
                    neg = 1
                    pos = 0
                draw_display()
                print('KEY3 - Negative:', neg, 'State:', state)
                
            elif event.keysym == 'Return':  # Center button
                if state == "start":
                    state = "choosing"
                    pos = 1
                    neg = 0
                elif state == "choosing":
                    # Show selected emoji and trigger appropriate animation
                    print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                    # Start animation in a separate thread
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    # Don't reset state here - let animation handle it
                else:
                    draw_display()
                print('Center - State:', state)
            
            # Update status label
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")

from emojis_zero import *
from animations_zero import fireworks_animation as fw_anim_func, rain_animation as rain_anim_func
from emojis_zero import fireworks_animation, rain_animation

# 240x240 display with hardware SPI (or stub on laptop):
if is_raspberry_pi():
    # Initialize GPIO for button reading
    import RPi.GPIO as GPIO
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    disp = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
else:
    disp = _DispStub()
    Lcd_ScanDir = 0
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('RGB', (disp.width, disp.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# === State Machine Variables ===
menu = 0  # Main menu selection (0-3)
pos = 0   # Positive selection (left side emojis)
neg = 0   # Negative selection (right side emojis)
state = "none"  # State: "none", "start", "choosing"
is_winking = False  # Flag to control winking animation
is_animating = False  # Flag to control main emoji animation
animation_running = False  # Flag to prevent multiple animation threads
stop_animation = False  # Flag to interrupt procedural animations

# Previous state tracking for emoji toggling
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or "done"


# === Menu Items ===
menu_items = ["Emojis", "Animations", "Characters", "Other"]

# === Button State Tracking ===
button_states = {
    'up': True,
    'down': True,
    'left': True,
    'right': True,
    'center': True,
    'key1': True,
    'key2': True,
    'key3': True
}

# === Helper Functions ===

def draw_centered_text(draw, text, y_position, font, max_width, text_color="white"):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    x_position = (max_width - text_width) // 2
    draw.text((x_position, y_position), text, font=font, fill=text_color)

def draw_menu_row(draw, text, y_position, font, is_selected=False):
    row_height = 14
    row_y = y_position
    
    if is_selected:
        bg_width = 80  # Fixed width for selection background
        bg_x = 24
        draw.rectangle((bg_x, row_y, bg_x + bg_width, row_y + row_height), fill="white")
        draw_centered_text(draw, text, row_y + 2, font, 128, "black")
    else:
        draw_centered_text(draw, text, row_y + 2, font, 128, "white")

def get_main_emoji():
    """Get the main emoji matrix based on current menu, pos, and neg selection"""
    if menu == 0:  # Emojis menu
        # Show the currently selected emoji when in choosing state
        if state == "choosing":
            if pos == 1:
                return regular_matrix
            elif pos == 2:
                return happy_matrix
            elif pos == 3:
                return wry_matrix
            elif pos == 4:
                return heart_matrix
            elif neg == 1:
                return thick_lips_matrix
            elif neg == 2:
                return sad_matrix
            elif neg == 3:
                return angry_matrix
            elif neg == 4:
                return green_monster_matrix
        # Show default when not in choosing state
        elif pos == 1:
            return regular_matrix
        elif pos == 2:
            return happy_matrix
        elif pos == 3:
            return wry_matrix
        elif pos == 4:
            return heart_matrix
        elif neg == 1:
            return thick_lips_matrix
        elif neg == 2:
            return sad_matrix
        elif neg == 3:
            return angry_matrix
        elif neg == 4:
            return green_monster_matrix
    
    elif menu == 1:  # Animations menu
        # Return preview matrices for animations
        if state == "choosing":
            if pos == 1:
                return fireworks_animation.preview
            elif neg == 1:
                return rain_animation.preview
        elif pos == 1:
            return fireworks_animation.preview
        elif neg == 1:
            return rain_animation.preview
    
    # Default to regular smiley for other menus
    return smiley_matrix

def get_main_emoji_animation():
    """Get the animation state of the main emoji"""
    if menu == 0:  # Emojis menu
        # Show the animation for currently selected emoji when in choosing state
        if state == "choosing":
            if pos == 1:
                return regular_wink_matrix
            elif pos == 2:
                return happy_wink_matrix
            elif pos == 3:
                return wry_wink_matrix
            elif pos == 4:
                return heart_bounce_matrix
            elif neg == 1:
                return thick_lips_wink_matrix
            elif neg == 2:
                return sad_wink_matrix
            elif neg == 3:
                return angry_wink_matrix
            elif neg == 4:
                return green_monster_wink_matrix
        # Show animation for selected emoji when not in choosing state
        elif pos == 1:
            return regular_wink_matrix
        elif pos == 2:
            return happy_wink_matrix
        elif pos == 3:
            return wry_wink_matrix
        elif pos == 4:
            return heart_bounce_matrix
        elif neg == 1:
            return thick_lips_wink_matrix
        elif neg == 2:
            return sad_wink_matrix
        elif neg == 3:
            return angry_wink_matrix
        elif neg == 4:
            return green_monster_wink_matrix
    
    # Default to wink smiley for other menus
    return smiley_wink_matrix

def get_left_side_emojis():
    """Get the left side emoji matrices for menu 0 (Emojis) and menu 1 (Animations)"""
    if menu == 0:
        return [regular_matrix, happy_matrix, wry_matrix, heart_matrix]
    elif menu == 1:
        return [fireworks_animation.preview, smiley_matrix, smiley_matrix, smiley_matrix]
    else:
        return [smiley_matrix, smiley_matrix, smiley_matrix, smiley_matrix]

def get_right_side_emojis():
    """Get the right side emoji matrices for menu 0 (Emojis) and menu 1 (Animations)"""
    if menu == 0:
        return [thick_lips_matrix, sad_matrix, angry_matrix, green_monster_matrix]
    elif menu == 1:
        return [rain_animation.preview, smiley_matrix, smiley_matrix, smiley_matrix]
    else:
        return [smiley_matrix, smiley_matrix, smiley_matrix, smiley_matrix]

def check_menu():
    global menu
    if menu > 3:
        menu = 0
    if menu < 0:
        menu = 3

def check_pos():
    global pos
    if pos > 4:
        pos = 1
    if pos < 1:
        pos = 4

def check_neg():
    global neg
    if neg > 4:
        neg = 1
    if neg < 1:
        neg = 4

def reset_state():
    """Save current state as previous and reset to initial state"""
    global state, menu, pos, neg, prev_state, prev_menu, prev_pos, prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    """Clear previous state tracking"""
    global prev_state, prev_menu, prev_pos, prev_neg
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0

def check_animation_interruption():
    """Check if user wants to interrupt the current animation"""
    global stop_animation
    try:
        key1_pressed = disp.digital_read(disp.GPIO_KEY1_PIN) == 0
        key3_pressed = disp.digital_read(disp.GPIO_KEY3_PIN) == 0
        
        # If opposite button is pressed, signal interruption
        if (menu == 1 and pos > 0 and key3_pressed) or (menu == 1 and neg > 0 and key1_pressed):
            stop_animation = True
            return True
        return False
    except:
        # If GPIO read fails, don't interrupt
        return False

def start_procedural_animation():
    """Start a procedural animation (fireworks or rain) with interruption support"""
    global animation_running, stop_animation, prev_menu, prev_pos, prev_neg, prev_state
    global state, menu, pos, neg
    
    if animation_running:
        print("DEBUG: Animation already running, skipping")
        return
    
    # Memory monitoring
    try:
        import psutil
        memory_info = psutil.virtual_memory()
        print(f"DEBUG: Memory before animation - Used: {memory_info.used/1024/1024:.1f}MB, Available: {memory_info.available/1024/1024:.1f}MB")
    except ImportError:
        print("DEBUG: psutil not available for memory monitoring")
    
    print(f"DEBUG: Starting procedural animation - Menu: {menu}, Pos: {pos}, Neg: {neg}")
    animation_running = True
    stop_animation = False
    
    # Save current selection
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    
    print("DEBUG: Clearing display for animation")
    # Clear the display for animation
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    
    # Calculate position for full-screen animation (bottom half like emojis)
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (disp.width - emoji_width) // 2
    start_y = 64 + (64 - emoji_height)
    
    print(f"DEBUG: Animation position - start_x: {start_x}, start_y: {start_y}, scale: {scale}")
    interrupted = False
    
    # Run the appropriate animation
    try:
        if menu == 1 and pos == 1:
            # Fireworks animation - reduced iterations for Pi Zero
            print("DEBUG: Starting fireworks animation")
            iterations = 5 if is_raspberry_pi() else 10  # Reduce for Pi Zero
            interrupted = fw_anim_func(draw, image, disp, scale, start_x, start_y, 
                                       iters=iterations, interruption_check=check_animation_interruption)
            print(f"DEBUG: Fireworks animation completed, interrupted: {interrupted}")
        elif menu == 1 and neg == 1:
            # Rain animation - reduced iterations and density for Pi Zero
            print("DEBUG: Starting rain animation")
            iterations = 50 if is_raspberry_pi() else 200  # Reduce for Pi Zero
            density = 0.5 if is_raspberry_pi() else 1      # Reduce density for Pi Zero
            interrupted = rain_anim_func(draw, image, disp, scale, start_x, start_y, 
                                        iters=iterations, density=density, interruption_check=check_animation_interruption)
            print(f"DEBUG: Rain animation completed, interrupted: {interrupted}")
    except Exception as e:
        print(f"DEBUG: Animation failed with error: {e}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        interrupted = False
        # Try to recover by showing normal display
        print("DEBUG: Attempting to recover by showing normal display")
        draw_display()
    
    # Handle interruption - toggle to opposite animation
    if interrupted and stop_animation:
        print("DEBUG: Animation was interrupted, toggling to opposite")
        # User pressed opposite button - toggle pos/neg
        if prev_pos > 0:
            neg = prev_pos
            pos = 0
            menu = prev_menu
        elif prev_neg > 0:
            pos = prev_neg
            neg = 0
            menu = prev_menu
        
        # Reset flags
        animation_running = False
        stop_animation = False
        
        # Start the opposite animation in a new thread to avoid recursion
        animation_thread = threading.Thread(target=start_procedural_animation)
        animation_thread.daemon = True
        animation_thread.start()
        return
    
    # Animation completed normally - reset state
    print("DEBUG: Animation completed normally, resetting state")
    state = "none"
    pos = 0
    neg = 0
    animation_running = False
    stop_animation = False
    
    # Force garbage collection to free memory
    import gc
    gc.collect()
    print("DEBUG: Garbage collection completed")
    
    print("DEBUG: Calling draw_display() after animation")
    draw_display()

def emoji_two_part_animation():
    """Function to handle two-part emoji animation: normal state then animation state"""
    global is_winking, is_animating, animation_running
    if animation_running:
        return
    animation_running = True
    
    # First show the normal emoji state
    is_winking = False
    is_animating = False
    draw_display()
    time.sleep(0.5)  # Show normal state for 0.5 seconds
    
    # Then show the animation state
    if menu == 0 and pos == 4:  # Heart bounce
        is_animating = True
        is_winking = False
    else:  # Wink animation for other emojis
        is_winking = True
        is_animating = False
    
    draw_display()
    time.sleep(1.0)  # Show animation for 1 second
    
    # Return to normal state
    is_winking = False
    is_animating = False
    draw_display()
    animation_running = False

def start_emoji_animation():
    """Start the appropriate animation based on menu selection"""
    global prev_menu, prev_pos, prev_neg, prev_state, menu, pos, neg, state
    
    # Check if this is a procedural animation (menu 1)
    if menu == 1 and (pos == 1 or neg == 1):
        start_procedural_animation()
    else:
        # Regular two-part emoji animation
        prev_state = "done"
        prev_menu = menu
        prev_pos = pos
        prev_neg = neg
        
        # Run the animation
        emoji_two_part_animation()
        
        # Reset to none state after animation completes (no menu selection)
        state = "none"
        pos = 0
        neg = 0

def draw_display():
    """Draw the complete display"""
    # Clear screen
    draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
    
    # === Main Emoji (bottom half) ===
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (disp.width - emoji_width) // 2
    start_y = 64 + (64 - emoji_height)
    
    # Get the appropriate main emoji
    if is_winking or is_animating:
        current_emoji = get_main_emoji_animation()
    else:
        current_emoji = get_main_emoji()
    
    draw_emoji(draw, current_emoji, color_map, scale, start_x, start_y)
    
    # === Left Side Emojis (with selection) ===
    left_emoji_y = [1, 16, 31, 46]
    left_emojis = get_left_side_emojis()
    for i, y_pos in enumerate(left_emoji_y):
        show_selection = (state == "choosing" and pos == i + 1)
        draw_emoji(draw, left_emojis[i], color_map, 1.5, 5, y_pos, show_selection)
    
    # === Right Side Emojis (with selection) ===
    right_emoji_y = [1, 16, 31, 46]
    right_emojis = get_right_side_emojis()
    for i, y_pos in enumerate(right_emoji_y):
        show_selection = (state == "choosing" and neg == i + 1)
        draw_emoji(draw, right_emojis[i], color_map, 1.5, 110, y_pos, show_selection)
    
    # === Menu Text ===
    text_y_positions = [1, 16, 31, 46]
    for i, item in enumerate(menu_items):
        # Show main menu selection in both "start" and "choosing" states
        is_selected = (i == menu and (state == "start" or state == "choosing"))
        draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
    
    # Update display
    disp.LCD_ShowImage(image,0,0)

# === Load font ===
try:
    font = ImageFont.load_default()
except:
    font = ImageFont.load_default()

# === Initial display ===
draw_display()

print("Emoji OS Zero v0.1.2 started. Use the joystick and buttons to navigate.")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")
print("=" * 50)

# === Main execution ===
if is_raspberry_pi():
    try:
        while True:
            # === Read button states ===
            up_pressed = disp.digital_read(disp.GPIO_KEY_UP_PIN) == 0
            down_pressed = disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0
            left_pressed = disp.digital_read(disp.GPIO_KEY_LEFT_PIN) == 0
            right_pressed = disp.digital_read(disp.GPIO_KEY_RIGHT_PIN) == 0
            center_pressed = disp.digital_read(disp.GPIO_KEY_PRESS_PIN) == 0
            key1_pressed = disp.digital_read(disp.GPIO_KEY1_PIN) == 0
            key2_pressed = disp.digital_read(disp.GPIO_KEY2_PIN) == 0
            key3_pressed = disp.digital_read(disp.GPIO_KEY3_PIN) == 0
        
        # === Handle UP button ===
        if up_pressed and not button_states['up']:
            reset_prev()  # Clear previous state when navigating
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu - 1) % 4
                check_menu()
            elif state == "choosing":
                # In choosing mode, UP/DOWN should cycle through left side emojis (positive)
                pos = (pos - 1) % 5
                if pos == 0:
                    pos = 4
                neg = 0
                check_pos()
            draw_display()
            print('Up - Menu:', menu, 'Pos:', pos, 'Neg:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['up'] = up_pressed
        
        # === Handle DOWN button ===
        if down_pressed and not button_states['down']:
            reset_prev()  # Clear previous state when navigating
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu + 1) % 4
                check_menu()
            elif state == "choosing":
                # In choosing mode, UP/DOWN should cycle through left side emojis (positive)
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()
            draw_display()
            print('Down - Menu:', menu, 'Pos:', pos, 'Neg:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['down'] = down_pressed
        
        # === Handle LEFT button ===
        if left_pressed and not button_states['left']:
            reset_prev()  # Clear previous state when navigating
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()
            draw_display()
            print('Left - Negative:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['left'] = left_pressed
        
        # === Handle RIGHT button ===
        if right_pressed and not button_states['right']:
            reset_prev()  # Clear previous state when navigating
            if state == "choosing":
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()
            draw_display()
            print('Right - Positive:', pos, 'State:', state)
            time.sleep(0.2)
        button_states['right'] = right_pressed
        
        # === Handle CENTER button ===
        if center_pressed and not button_states['center']:
            if state == "start":
                state = "choosing"
                pos = 1
                neg = 0
            elif state == "choosing":
                # Show selected emoji and trigger appropriate animation
                print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                # Start animation in a separate thread
                animation_thread = threading.Thread(target=start_emoji_animation)
                animation_thread.daemon = True
                animation_thread.start()
                # Don't reset state here - let animation handle it
            draw_display()
            print('Center - State:', state)
            time.sleep(0.2)
        button_states['center'] = center_pressed
        
        # === Handle KEY1 button (Positive) ===
        if key1_pressed and not button_states['key1']:
            print('debug KEY1 - menu:', menu, "pos", pos, "neg", neg, 
                "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)

            # Try toggle or replay previous if available
            if prev_state == "done":
                if prev_neg > 0:
                    # Toggle from previous negative to positive
                    pos = prev_neg
                    neg = 0
                    menu = prev_menu
                    print('KEY1 - Toggle from neg to pos, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    draw_display()
                    time.sleep(0.2)
                    button_states['key1'] = key1_pressed
                elif prev_pos > 0:
                    # Replay previous positive
                    pos = prev_pos
                    neg = 0
                    menu = prev_menu
                    print('KEY1 - Replay prev pos, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    draw_display()
                    time.sleep(0.2)
                    button_states['key1'] = key1_pressed

            # Fallback to regular logic
            if state == "choosing":
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()

            elif state == "start":
                state = "choosing"
                pos = 1
                neg = 0

            elif state == "none":
                state = "choosing"
                pos = 1
                neg = 0

            draw_display()
            print('KEY1 - Positive:', pos, 'State:', state)
            time.sleep(0.2)
        button_states['key1'] = key1_pressed
        
        # === Handle KEY2 button (Menu/Confirm) ===
        if key2_pressed and not button_states['key2']:
            # Only clear prev when *not* confirming the current choosing
            if state != "choosing":
                reset_prev()

            if state == "start":
                menu = (menu + 1) % 4
                check_menu()
            elif state == "none":
                state = "start"
            elif state == "choosing":
                # Don’t reset prev here! First record prev, then animate
                print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                animation_thread = threading.Thread(target=start_emoji_animation)
                animation_thread.daemon = True
                animation_thread.start()
            draw_display()
            print('KEY2 - Menu:', menu, 'State:', state)
            time.sleep(0.2)
        button_states['key2'] = key2_pressed
        
        # === Handle KEY3 button (Negative) ===
        if key3_pressed and not button_states['key3']:
            print('debug KEY3 - menu:', menu, "pos", pos, "neg", neg, 
                  "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)

            # First, attempt the “toggle / replay previous” case if just after an animation
            if prev_state == "done":
                if prev_pos > 0:
                    # Toggle from previous positive to negative
                    neg = prev_pos
                    pos = 0
                    menu = prev_menu
                    print('KEY3 - Toggle from pos to neg, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    # We do NOT reset prev_state here, so it doesn’t fall through to other branches
                    draw_display()
                    time.sleep(0.2)
                    button_states['key3'] = key3_pressed
                elif prev_neg > 0:
                    # Replay previous negative
                    neg = prev_neg
                    pos = 0
                    menu = prev_menu
                    print('KEY3 - Replay prev neg, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    draw_display()
                    time.sleep(0.2)
                    button_states['key3'] = key3_pressed

            # If we didn’t take the toggle/replay branch, do the normal logic
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()

            elif state == "start":
                state = "choosing"
                neg = 1
                pos = 0

            elif state == "none":
                state = "choosing"
                neg = 1
                pos = 0

            draw_display()
            print('KEY3 - Negative:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['key3'] = key3_pressed
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
        disp.module_exit()
else:
    # Running on laptop - show simulation window
    print("Running on laptop - showing LCD simulation window")
    draw_display()  # Draw initial display
    if hasattr(disp, 'simulation_window') and disp.simulation_window:
        disp.simulation_window.mainloop()
