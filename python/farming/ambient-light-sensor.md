# Ambient Light Sensor

We want to use a PiicoDev Ambient Light Sensor VEML6030 with a Raspberry Pi Pico to calculate the amount of hours of direct sunlight per day a spot in a garden gets

## Measuring Direct Sunlight Hours Using a PiicoDev VEML6030 (Raspberry Pi Pico)

This guide shows how to use a **PiicoDev Ambient Light Sensor (VEML6030)** with a **Raspberry Pi Pico** to estimate how many **hours of direct sunlight per day** a specific spot in your garden receives. This is ideal for deciding whether a location is suitable for sun-loving plants like zucchini.

The basic idea is:

1. Measure **ambient light (lux)** at regular intervals
2. Decide a **lux threshold** that represents *direct sunlight*
3. Count how long readings stay above that threshold
4. Convert that accumulated time into **sun-hours per day**

## What the VEML6030 Measures

The VEML6030 measures **illuminance in lux** (how bright light appears to the human eye).

Typical outdoor values:

| Lighting condition        | Approx. lux |
|---------------------------|-------------|
| Full direct sunlight      | 60,000–100,000 |
| Bright shade / thin cloud | 10,000–30,000 |
| Overcast sky              | 1,000–5,000 |

Note the sensor does **not** know the direction of light. It cannot distinguish direct sun from reflections, so thresholds are used.

## Choosing a Direct Sunlight Threshold

For garden planning, this rule works well:

```text
DIRECT_SUN_LUX = 40,000
```
