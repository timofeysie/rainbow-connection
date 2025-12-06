# -*- coding:utf-8 -*-
# Emoji OS Zero v0.3.4 - Enhanced with BLE Controller functionality
import LCD_1in44
import time
import threading
import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

from PIL import Image,ImageDraw,ImageFont,ImageColor
from emojis_zero import *
from animations_zero import fireworks_animation as fw_anim_func, rain_animation as rain_anim_func
from emojis_zero import fireworks_animation, rain_animation

# === BLE Configuration ===
# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write characteristic
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify characteristic

# Device name preference (optional - script will scan by service UUID first)
# If device name doesn't match, the script will still find the Pico by service UUID
TARGET_DEVICE_NAME = "Pico-Client"  # Preferred name, but not required for connection

# BLE Controller class
class BLEController:
    """BLE Central controller that connects to Pico and sends emoji commands"""
    
    def __init__(self):
        self.client = None
        self.device_address = None
        self.connected = False
        
    async def scan_for_device(self, timeout=10):
        """Scan for the target Pico device by service UUID (more reliable than name)"""
        print(f"Scanning for Pico with Nordic UART Service for {timeout} seconds...")
        print("Make sure your Pico is running emoji-os-pico-0.2.0.py...")
        print(f"Looking for service UUID: {UART_SERVICE_UUID}")
        
        # First, try scanning by service UUID (most reliable)
        print("\nAttempting service-based scan...")
        try:
            devices_by_service = await BleakScanner.discover(
                timeout=timeout,
                service_uuids=[UART_SERVICE_UUID]
            )
            if devices_by_service and len(devices_by_service) > 0:
                print(f"✓ Found {len(devices_by_service)} device(s) advertising Nordic UART Service:")
                for device in devices_by_service:
                    name = device.name or "(No Name)"
                    print(f"  - {name} at {device.address}")
                self.device_address = devices_by_service[0].address
                print(f"\n✓ Using: {devices_by_service[0].name or '(No Name)'} at {self.device_address}")
                return True
            else:
                print("  No devices found with service UUID in advertisement")
        except Exception as e:
            print(f"  ⚠ Service-based scan failed: {e}")
        
        # Fall back to general scan and verify each device
        print("\nFalling back to general scan...")
        all_devices = await BleakScanner.discover(timeout=timeout)
        
        print(f"\nFound {len(all_devices)} total BLE devices:")
        print("-" * 50)
        
        # Look for exact name match first
        for i, device in enumerate(all_devices, 1):
            name = device.name or "(No Name)"
            print(f"{i:2d}. {name:<20} | {device.address}")
            
            if device.name == TARGET_DEVICE_NAME:
                print(f"    *** FOUND TARGET DEVICE BY NAME! ***")
                self.device_address = device.address
                return True
        
        print("-" * 50)
        
        # If no name match, try to verify devices by connecting and checking services
        print("\nNo exact name match. Verifying devices have Nordic UART Service...")
        candidates = [
            d for d in all_devices 
            if d.name is None or d.name == "(No Name)" or 
               "pico" in (d.name or "").lower() or 
               "client" in (d.name or "").lower() or
               "mpy" in (d.name or "").lower()
        ]
        
        if not candidates:
            print("  No candidate devices found (looking for devices with no name or 'pico'/'client'/'mpy' in name)")
        else:
            print(f"  Found {len(candidates)} candidate device(s) to verify...")
        
        for candidate in candidates:
            name = candidate.name or "(No Name)"
            print(f"\n  Testing: {name} at {candidate.address}")
            try:
                temp_client = BleakClient(candidate.address, timeout=5.0)
                await temp_client.connect()
                
                if temp_client.is_connected:
                    print(f"    ✓ Connected, checking services...")
                    services = await temp_client.get_services()
                    
                    # Check for Nordic UART Service
                    for service in services:
                        service_uuid = str(service.uuid).upper()
                        if service_uuid == UART_SERVICE_UUID.upper():
                            print(f"    ✓✓ FOUND NORDIC UART SERVICE! ✓✓")
                            await temp_client.disconnect()
                            self.device_address = candidate.address
                            print(f"\n✓ Successfully found Pico at: {candidate.address}")
                            return True
                    
                    print(f"    ✗ Device doesn't have Nordic UART Service (found {len(services)} other services)")
                    await temp_client.disconnect()
                else:
                    print(f"    ✗ Failed to connect")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                continue
        
        print(f"\n✗ Could not find Pico with Nordic UART Service")
        print("\nTroubleshooting tips:")
        print("1. Make sure Pico is running emoji-os-pico-0.2.0.py")
        print("2. Check that Pico shows 'Starting advertising as 'Pico-Client'...'")
        print("3. Verify Pico output shows 'BLE Device Name configured: Pico-Client'")
        print("4. Try moving devices closer together")
        print("5. Restart both devices (power cycle the Pico)")
        print("6. Check Pico output for BLE initialization errors")
        print("\nNote: The script now scans by service UUID, so device name is optional.")
        return False
    
    async def connect_to_device(self):
        """Connect to the discovered Pico device"""
        if not self.device_address:
            print("No device address available. Run scan_for_device() first.")
            return False
            
        try:
            print(f"Connecting to {self.device_address}...")
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            
            if self.client.is_connected:
                print("✓ Successfully connected!")
                # Verify we can discover services
                try:
                    print("Discovering services...")
                    services = await self.client.get_services()
                    uart_service = None
                    for service in services:
                        if str(service.uuid).upper() == UART_SERVICE_UUID.upper():
                            uart_service = service
                            print(f"✓ Found UART service: {service.uuid}")
                            break
                    
                    if not uart_service:
                        print("⚠ Warning: UART service not found, but connection established")
                    else:
                        print("✓ Service discovery successful")
                    
                    self.connected = True
                    return True
                except Exception as e:
                    print(f"⚠ Connected but service discovery failed: {e}")
                    print("This might indicate the device disconnected or doesn't have the expected services")
                    await self.client.disconnect()
                    return False
            else:
                print("✗ Failed to connect")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            if "disconnected" in str(e).lower() or "discover" in str(e).lower():
                print("   This usually means:")
                print("   1. The device disconnected during connection")
                print("   2. The device doesn't support the required BLE services")
                print("   3. There's a compatibility issue with the BLE stack")
            return False
    
    async def send_emoji_command(self, menu, pos, neg):
        """Send emoji selection command to the connected Pico"""
        if not self.client or not self.client.is_connected:
            print("Not connected to any device")
            return False
            
        try:
            # Create command string: "MENU:POS:NEG"
            command = f"{menu}:{pos}:{neg}"
            command_bytes = command.encode('utf-8')
            
            # Write to the RX characteristic
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, command_bytes)
            print(f"✓ Sent emoji command: '{command}'")
            return True
            
        except Exception as e:
            print(f"✗ Error sending emoji command '{command}': {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the device"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected from Pico")
            self.connected = False

# Global BLE controller instance
ble_controller = BLEController()
ble_connection_thread = None
ble_event_loop = None

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
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

def send_emoji_to_pico(menu_val, pos_val, neg_val):
    """Send emoji selection to Pico via BLE"""
    global ble_event_loop
    
    if not ble_event_loop:
        print("BLE not initialized yet")
        return
    
    def send_command():
        try:
            # Use the existing event loop
            future = asyncio.run_coroutine_threadsafe(
                ble_controller.send_emoji_command(menu_val, pos_val, neg_val),
                ble_event_loop
            )
            # Wait for completion with timeout
            future.result(timeout=5)
            
        except Exception as e:
            print(f"Error sending to Pico: {e}")
    
    # Send in a separate thread to avoid blocking the main loop
    send_thread = threading.Thread(target=send_command)
    send_thread.daemon = True
    send_thread.start()

def start_procedural_animation():
    """Start a procedural animation (fireworks or rain) with interruption support"""
    global animation_running, stop_animation, prev_menu, prev_pos, prev_neg, prev_state
    global state, menu, pos, neg
    
    if animation_running:
        return
    
    animation_running = True
    stop_animation = False
    
    # Save current selection
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    
    # Send emoji command to Pico
    send_emoji_to_pico(menu, pos, neg)
    
    # Clear the display for animation
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    
    # Calculate position for full-screen animation (bottom half like emojis)
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (disp.width - emoji_width) // 2
    start_y = 64 + (64 - emoji_height)
    
    interrupted = False
    
    # Run the appropriate animation
    if menu == 1 and pos == 1:
        # Fireworks animation
        interrupted = fw_anim_func(draw, image, disp, scale, start_x, start_y, 
                                   iters=10, interruption_check=check_animation_interruption)
    elif menu == 1 and neg == 1:
        # Rain animation
        interrupted = rain_anim_func(draw, image, disp, scale, start_x, start_y, 
                                    iters=200, density=1, interruption_check=check_animation_interruption)
    
    # Handle interruption - toggle to opposite animation
    if interrupted and stop_animation:
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
    state = "none"
    pos = 0
    neg = 0
    animation_running = False
    stop_animation = False
    draw_display()

def emoji_two_part_animation():
    """Function to handle two-part emoji animation: normal state then animation state"""
    global is_winking, is_animating, animation_running
    if animation_running:
        return
    animation_running = True
    
    # Send emoji command to Pico
    send_emoji_to_pico(menu, pos, neg)
    
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
    
    # === BLE Connection Status ===
    if ble_controller.connected:
        draw.text((200, 220), "BLE", font=font, fill="green")
    else:
        draw.text((200, 220), "BLE", font=font, fill="red")
    
    # Update display
    disp.LCD_ShowImage(image,0,0)

# === Load font ===
try:
    font = ImageFont.load_default()
except:
    font = ImageFont.load_default()

# === Initial display ===
draw_display()

print("Emoji OS Zero v0.3.4 started with BLE Controller functionality")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")
print("=" * 50)

# === Initialize BLE Connection ===
def init_ble_connection():
    """Initialize BLE connection in a separate thread"""
    global ble_event_loop, ble_connection_thread
    
    def connect():
        global ble_event_loop
        try:
            # Create a new event loop for this thread
            ble_event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(ble_event_loop)
            
            # Scan and connect
            if ble_event_loop.run_until_complete(ble_controller.scan_for_device(timeout=5)):
                ble_event_loop.run_until_complete(ble_controller.connect_to_device())
            
            # Keep the event loop running
            ble_event_loop.run_forever()
            
        except Exception as e:
            print(f"BLE initialization error: {e}")
    
    # Start BLE connection in background
    ble_connection_thread = threading.Thread(target=connect)
    ble_connection_thread.daemon = True
    ble_connection_thread.start()

# Start BLE connection
init_ble_connection()

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
                    continue
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
                    continue

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
                # Don't reset prev here! First record prev, then animate
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
                    # We do NOT reset prev_state here, so it doesn't fall through to other branches
                    draw_display()
                    time.sleep(0.2)
                    button_states['key3'] = key3_pressed
                    continue
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
                    continue

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
            time.sleep(0.2)
        button_states['key3'] = key3_pressed
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    # Clean up BLE connection
    if ble_event_loop:
        try:
            # Schedule disconnect and stop the loop
            ble_event_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(ble_controller.disconnect())
            )
            # Give it a moment to disconnect
            time.sleep(1)
            ble_event_loop.stop()
        except:
            pass
    disp.module_exit()
