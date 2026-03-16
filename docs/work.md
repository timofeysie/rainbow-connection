# Work log

## Complete Controller Emoji

In `python\emoji-os\emoji-os-zero-0.3.0.py` (zero controller script) which relies on `python\emoji-os\emojis_zero.py`
we use the smiley_matrix as the default emoji.

However, in `python\emoji-os\emoji-os-pico-0.2.4.py` (pico emoji script) which relies on `python\emoji-os\emojis.py`,

There are specific emojis which are used that we can implement in `emoji-os-zero-0.3.0.py` to keep parity with the `emoji-os-pico-0.2.4.py`.

We need to plan to implement each emoji that exists in the pico emoji script that does not exist in the zero controller script.

These emojis are detailed in the "Complete Menu Options Chart" of the `python\emoji-os\emoji-os-zero-prd.md` document. They appear as "(None)" values in this chart.

Here is a list of the currently missing emojis in the zero controller script so that we can plan to replace the `smiley_matrix` default occurrences with the actual emojis from the pico script, one by one.

For each item below, the general implementation steps will be:

- **Step 1**: Pick an existing Pico emoji function from `python\emoji-os\emojis.py` that should occupy this slot (or design a new one if needed).
- **Step 2**: Create a corresponding 8×8 matrix (or matrices, if it has an animated state) in `python\emoji-os\emojis_zero.py`.
- **Step 3**: Wire that matrix into `python\emoji-os\emoji-os-zero-0.3.0.py`:
  - **Main display**: update `get_main_emoji()` for the appropriate `menu`, `pos`/`neg`.
  - **Animated state** (if needed): update `get_main_emoji_animation()`.
  - **Side previews**: update `get_left_side_emojis()` / `get_right_side_emojis()` so the mini icons match.
- **Step 4**: Update the "Complete Menu Options Chart" in `python\emoji-os\emoji-os-zero-prd.md` to replace `(None)` with the chosen emoji name.

### Missing entries from the Complete Menu Options Chart

- **Menu 1 – Animations (menu == 1)**
  - **Negative 2**: pos/neg mapping `menu == 1`, `neg == 2` → currently `(None)` in the chart and effectively uses `smiley_matrix` as a placeholder.
  - **Negative 3**: `menu == 1`, `neg == 3` → `(None)` / `smiley_matrix` placeholder.
  - **Negative 4**: `menu == 1`, `neg == 4` → `(None)` / `smiley_matrix` placeholder.

- **Menu 2 – Characters (menu == 2)**
  - **Negative 3**: `menu == 2`, `neg == 3` → `(None)` in the chart (no negative character yet).
  - **Negative 4**: `menu == 2`, `neg == 4` → `(None)` in the chart (no negative character yet).

- **Menu 3 – Symbols (menu == 3)**
  - **Negative 3**: `menu == 3`, `neg == 3` → `(None)` in the chart (no third negative symbol yet).

When we implement each of these, we will:

- Decide which Pico emoji (or new design) fits the emotional meaning for that slot.
- Derive its 8×8 matrix for the Zero display.
- Replace any `smiley_matrix` placeholder usage for that `menu`/`pos`/`neg` combination with the new matrix references.
