# Emoji OS Zero Product Requirements

Emoji OS is a simple menu system that allows you to switch between emojis.

The first version was built for a Raspberry Pi Pico with a GlowBit 8x8 matrix LED and three connected buttons.

The Emoji OS Zero will be designed for a Raspberry Pi Zero 2 W with a Waveshare 1.44inch LCD display HAT.

The demo code from Waveshare demonstrates the joystick, button and display features of the LCD HAT.

This is the [key_demo.py](https://github.com/Kudesnick/1.44inch-LCD-HAT-Code/blob/main/python/key_demo.py) code which was used as the starting point for Emoji OS Zero.

## The menu

The emoji-os-pico.py version relies on three buttons to control a menu and select an emoji.

In this version, the middle button is the menu.  The top and bottom buttons are the positive and negative emojis.

- key1 button = pos (positive emojis)
- key2 button = menu (menu position)
- key3 button = neg (negative emojis)

The middle menu button2 moves the selected emoji category represented by four positions.  If the user goes past the end of the list it starts from the beginning again.

The categories are

1. Emojis
2. Animations
3. Characters
4. Symbols

Each category has a range of images to draw.  The first category, emojis, has four positive emojis like a smiley face, and the negative emojis has four negative emojis like a frowning face.

The new emoji-os-zero.py file will use a similar setup, but the menu can go up or down with the joystick instead of just one direction.

## Menu Structure and Options

The Emoji OS Zero provides a hierarchical menu system with 4 main categories, each containing multiple positive and negative options:

### Menu Categories

1. **Emojis** - Basic facial expressions and emotions
2. **Animations** - Dynamic patterns and visual effects  
3. **Characters** - Character-based designs and creatures
4. **Symbols** - Simple geometric shapes and text

### Complete Menu Options Chart:

| Menu | Category | Positive Options | Negative Options |
|------|----------|------------------|------------------|
| 0 | **Emojis** | 1. Regular (smiley) | 1. Thick Lips |
| | | 2. Happy | 2. Sad |
| | | 3. Wry | 3. Angry |
| | | 4. Heart Bounce | 4. Green Monster |
| 1 | **Animations** | 1. Fireworks | 1. Rain |
| | | 2. Circular Rainbow | 2. (None) |
| | | 3. Scroll Large Image | 3. (None) |
| | | 4. Chakana | 4. (None) |
| 2 | **Characters** | 1. Finn | 1. Bald |
| | | 2. Pikachu | 2. Surprise |
| | | 3. Crab | 3. (None) |
| | | 4. Frog | 4. (None) |
| 3 | **Symbols** | 1. Circle | 1. X |
| | | 2. YES | 2. NO |
| | | 3. Somi | 3. (None) |

### About the implementation

- Main menu (menu) is zero-based
  - Valid range: 0–3 (Emojis, Animations, Characters, Other).

- Sub-menu items (pos and neg) are one-based
  - Valid selection range: 1–4 (e.g. pos == 1 … pos == 4, same for neg).

### Navigation Controls

- **Joystick Up/Down**: Navigate between menu categories (0-3)
- **Joystick Left/Right**: Select negative/positive options within a category
- **Joystick Center Press**: Confirm selection and display emoji
- **KEY1**: Quick positive selection
- **KEY2**: Menu navigation and confirmation
- **KEY3**: Quick negative selection

## Adding a New Emoji for the Display

To show a new emoji in both the sub-menu (mini form) and the main menu (full-sized), do the following.

### 1. Define the matrix in `emojis_zero.py`

- Add an 8×8 matrix: a list of 8 rows, each row a list of 8 single-character color codes.
- Row/column order is `matrix[row][col]` (row index = y, column index = x).
- Use the same color codes as in `color_map`: `' '` (off/black), `'Y'` (yellow), `'R'` (red), `'G'` (green), `'W'` (white), `'B'` (black), `'P'` (purple), `'O'` (orange), `'C'` (cyan), `'M'` (magenta).
- For a static emoji, define one matrix (e.g. `my_emoji_matrix`). For a simple two-frame animation, define a base matrix and a second matrix (e.g. wink or bounce) and use both in the main script.

You can derive the 8×8 from GlowBit Pico code by mapping `drawRectangleFill(x1, y1, x2, y2, color)` to filling `matrix[y][x]` for `x` in `x1..x2`, `y` in `y1..y2` with the corresponding letter (`'W'`, `'Y'`, etc.).

### 2. Wire it in `emoji-os-zero-0.3.0.py`

- **Main emoji (full size):** In `get_main_emoji()`, add a branch for the correct `menu` and `pos` or `neg` (menu is 0-based, pos/neg are 1-based) and return your matrix.
- **Animated state (if used):** In `get_main_emoji_animation()`, return the animation frame (or the same matrix if non-animated).
- **Sub-menu mini form:** In `get_left_side_emojis()` and/or `get_right_side_emojis()`, for the right menu, put your matrix in the list at the index that matches the sub-menu item (index 0 = pos/neg 1, index 1 = pos/neg 2, etc.).

After that, the new emoji will appear in the side strip when that sub-menu item is selected and in the main area when that option is chosen.
