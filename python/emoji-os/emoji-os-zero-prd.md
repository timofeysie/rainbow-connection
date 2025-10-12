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

### Navigation Controls

- **Joystick Up/Down**: Navigate between menu categories (0-3)
- **Joystick Left/Right**: Select negative/positive options within a category
- **Joystick Center Press**: Confirm selection and display emoji
- **KEY1**: Quick positive selection
- **KEY2**: Menu navigation and confirmation
- **KEY3**: Quick negative selection
