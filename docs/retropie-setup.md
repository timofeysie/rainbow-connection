# RetroPie Setup: Raspberry Pi 4 + DFRobot Case + 8BitDo Zero 2

**Hardware:** [DFRobot FIT0820](https://wiki.dfrobot.com/fit0820/) — Raspberry Pi 4 Metal Case with 3.5" 480x320 TFT Touch Screen

## Hardware

- Raspberry Pi 4
- DFRobot FIT0820 Metal Case with 3.5" 480x320 TFT Touch Screen (GPIO/SPI, GoodTFT chipset)
- 8BitDo Zero 2 Bluetooth gamepad
- SD card (32GB+ recommended)
- Official Pi 4 USB-C power supply (5V/3A)
- USB keyboard (for initial setup only)

---

## 1. Flash RetroPie

1. Download the [RetroPie image for Pi 4](https://retropie.org.uk/download/)
2. Flash to SD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or [Balena Etcher](https://etcher.balena.io/)
3. Insert SD card into the Pi before assembling the case

---

## 2. Assemble the DFRobot Case

1. Align the TFT screen's GPIO receptacle with the Pi 4's 40-pin header — the screen slots in from the right side of the header
2. Press the screen firmly onto the GPIO pins until fully seated
3. Insert the MicroSD card into the Pi
4. Connect the network cable and power supply

> The screen connects directly via GPIO — no ribbon cable or separate power needed.

---

## 3. Install the TFT Screen Driver

The DFRobot FIT0820 uses the **GoodTFT MHS35** driver. Run these commands after booting (Pi must be connected to the internet):

```bash
sudo rm -rf LCD-show
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/
sudo ./MHS35-show
```

The Pi will reboot automatically. After restart, the screen should display and touch normally.

### If the screen is installed but showing wrong orientation

```bash
cd LCD-show/
sudo ./rotate.sh 90
```

Accepted values: `0`, `90`, `180`, `270`. The Pi will reboot to apply.

### Pi 4 HDMI note

If you ever use HDMI output on the Pi 4, you must comment out this line in `/boot/config.txt`:

```
# dtoverlay=vc4-fkms-V3D
```

Remove the `#` to re-enable HDMI later.

### Resolution note

480x320 is small. RetroPie's EmulationStation UI works fine, but some emulators may need resolution tweaks in their configs.

---

## 3. Connect to WiFi

On first boot, go to **RetroPie menu → WiFi** and connect. Required for installing packages and Bluetooth setup.

---

## 4. Pair the 8BitDo Zero 2

1. Put the controller into pairing mode: hold **Start** until the LED flashes rapidly
2. In RetroPie: **RetroPie menu → Bluetooth → Pair and Connect to Bluetooth Device**
3. Select the controller from the list
4. Once paired, configure buttons when prompted by EmulationStation

> The Zero 2 stays paired across reboots. If it disconnects, press **Start** to reconnect.

---

## 5. Add ROMs

ROMs are digital copies of game data. Place them in the appropriate system folder:

```
/home/pi/RetroPie/roms/<system>/
```

Examples:
| System | Folder |
|--------|--------|
| NES | `nes/` |
| SNES | `snes/` |
| Game Boy | `gb/` |
| Game Boy Advance | `gba/` |
| Sega Genesis | `megadrive/` |

Transfer files via:
- **USB drive** — copy ROMs to a USB stick, plug into Pi, RetroPie auto-copies them
- **Network (Samba)** — RetroPie shares a network drive; connect from your computer and drag files over
- **SFTP** — use FileZilla or similar, connect to the Pi's IP address

Restart EmulationStation after adding ROMs for them to appear.

---

## 6. Optional: Boot from USB SSD

Booting from an SSD is faster and more reliable than SD card long-term.

1. Boot from SD card first and update the bootloader:
   ```bash
   sudo raspi-config
   # Advanced Options → Bootloader Version → Latest
   sudo reboot
   ```
2. Clone SD card to SSD using `rpi-clone` or `dd`
3. Remove SD card and boot from SSD

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| TFT screen blank after driver install | Check chipset — try alternate driver script |
| Controller not pairing | Re-enter pairing mode (hold Start), retry Bluetooth scan |
| ROMs not showing | Check file extension matches expected format; restart EmulationStation |
| Pi underpowering (lightning bolt icon) | Use official 5V/3A USB-C PSU |
| Poor performance on emulator | Lower resolution in emulator config; check CPU isn't throttling |
