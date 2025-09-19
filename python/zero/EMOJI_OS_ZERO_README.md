# Emoji OS Zero v0.1.3

    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║    ╔═══════════════════════════════╗  ║
    ║    ║  ╔═════════════════════════╗  ║  ║
    ║    ║  ║  ╔═══════════════════╗  ║  ║  ║
    ║    ║  ║  ║  ╔═════════════╗  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ╔═══════╗  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ╔═╗  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ║B║  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ╚═╝  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ╔═╗  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ║B║  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ║  ╚═╝  ║  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ║  ╚═══════╝  ║  ║  ║  ║  ║
    ║    ║  ║  ║  ╚═════════════╝  ║  ║  ║  ║
    ║    ║  ║  ╚═══════════════════╝  ║  ║  ║
    ║    ║  ╚═════════════════════════╝  ║  ║
    ║    ╚═══════════════════════════════╝  ║
    ║                                       ║
    ╚═══════════════════════════════════════╝

A Raspberry Pi Zero W emoji display system with interactive menu navigation and animations.

## How It Works

### Core Components

- **State Machine**: 3 states (none → start → choosing)
- **Display System**: 240x240 LCD with real-time emoji preview
- **Menu Navigation**: 4 main categories with sub-menu emoji selection
- **Animation System**: Wink animations + special heart bounce

### Key Functions

**Display Management:**

- `draw_display()` - Main rendering loop
- `get_main_emoji()` - Returns current emoji based on selection
- `draw_emoji()` - Renders individual 8x8 emoji matrices

**State Management:**

- `check_menu()`, `check_pos()`, `check_neg()` - Validate selections
- Button handlers update menu/pos/neg variables
- State transitions: none → start → choosing → start

**Animation System:**

- `wink_animation()` - Standard eye-closing animation
- `heart_bounce_animation()` - Special heart movement
- `start_emoji_animation()` - Smart animation selection

### Control Flow

1. **Start**: Shows main menu with 4 categories
2. **Navigate**: Joystick moves between categories
3. **Enter Choosing**: CENTER button enters emoji selection
4. **Select Emoji**: UP/DOWN (left) or LEFT/RIGHT (right) sides
5. **Real-time Preview**: Main emoji updates as you navigate
6. **Confirm**: CENTER/KEY2 triggers animation and resets

### Current Implementation

- ✅ Menu 0 (Emojis): 8 emojis with animations
- ⏳ Menus 1-3: Basic structure, needs content
- ✅ Real-time emoji preview during selection
- ✅ Threaded animations (1-second duration)

### Data Structure

Each emoji = 8x8 matrix using symbols (Y=yellow, B=black, R=red, etc.)
Two states per emoji: normal and animation version
