# Controller Display Layout

The 128×128 display:

```txt
┌─────────────────────────────────┐  y=0
│ [Emj]       menu        [Emj]   │
│ [Emj]       menu        [Emj]   │
│ [Emj]       menu        [Emj]   │  y=58 ← right mini-emojis end here
│                                 │
│                                 │
│          ┌─────────┐            │  y=72 ← main emoji starts
│          │  main   │            │
│          │  emoji  │         87%│  y≈108 ← % text (right-aligned)
│          │  56×56  │    ▓▓▓░░░█ │  y=118 ← battery icon (right-aligned)
│[BLE]     └─────────┘            │  y=126
└─────────────────────────────────┘  y=128
```

- Percentage text — right-aligned at x≈104..126, y=108..116. Sits above the battery icon and clear of the emoji (emoji right edge is x=92).
- Battery icon — body at x=104..124, nub at x=124..126, y=118..126. Flush to the right edge, 2 px margin.
- Fill colour — green (>50 %), amber (20–50 %), red (<20 %).
- BLE indicator stays undisturbed in the bottom-left (x=2..18, y=110..126).
