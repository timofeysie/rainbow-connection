# Work log

## Complete Controller Emoji

In `python\emoji-os\emoji-os-zero-0.3.0.py` (zero controller script) which relies on `python\emoji-os\emojis_zero.py`
we use the smiley_matrix as the default emoji.

However, in `python\emoji-os\emoji-os-pico-0.2.4.py` (pico emoji script) which relies on `python\emoji-os\emojis.py`,

There are specific emojis which are used that we can implement in `emoji-os-zero-0.3.0.py` to keep parity with the `emoji-os-pico-0.2.4.py`.

We need to plan to implement each emoji that exists in the pico emoji script that does not exist in the zero controller script.

These emojis are detailed in the "Complete Menu Options Chart" of the `python\emoji-os\emoji-os-zero-prd.md` document.  They appear as "(None)" values in this chart.

Lets make a list of the currently missing emojis in the zero controller script so that we can plan to replace the smiley_matrix default occurrences with the actual emojis from the pico script.
