# Home Assistant notes

## Add a Raspberry Pi 5 with camera

### Overview

- The **Pi 5 with camera** runs **Raspberry Pi OS** and exposes a video stream (e.g. RTSP).
- **Home Assistant** (on another device) adds a camera entity that points at that stream.

### Step 1: Set up the camera Pi (Raspberry Pi 5)

1. Install **Raspberry Pi OS** on the Pi 5 (e.g. Raspberry Pi Imager → Raspberry Pi OS 64-bit, Bookworm).
2. **Enable the camera**
   - Run: `sudo raspi-config`
   - **Interface Options** → **Legacy Camera** or **Camera** (enable the option your OS shows).
   - Reboot if prompted.
3. **Verify the camera**
   - With **libcamera** (default on Pi 5 / Bookworm):

     ```bash
     rpicam-hello -t 2000
     ```

   - Or with the legacy stack:

     ```bash
     libcamera-still -o test.jpg
     ```

   If one of these runs without errors, the camera is working.

### Step 2: Run an RTSP stream on the Pi 5

Home Assistant can consume an **RTSP** URL. On Pi 5 with **libcamera**, a practical approach is **rpicam-vid** piped to **VLC**.

1. **Install VLC**

   ```bash
   sudo apt update
   sudo apt install -y vlc
   ```

2. **Start the stream** (H.264 over RTSP on port 8554)

   ```bash
   rpicam-vid -t 0 --width 1280 --height 720 --framerate 15 --inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream}' :demux=h264
   ```

   Leave this running and note the Pi’s IP (e.g. `hostname -I`).

3. **Test the stream** on another machine (e.g. Mac) with VLC: **Media → Open Network** →

   ```text
   rtsp://<PI_5_IP>:8554/stream
   ```

   Replace `<PI_5_IP>` with the Pi’s IP address.

4. **Run the stream on boot** with systemd

   Create the service file:

   ```bash
   sudo nano /etc/systemd/system/pi5-rtsp.service
   ```

   Contents (adjust resolution/framerate if needed):

   ```ini
   [Unit]
   Description=Pi 5 camera RTSP stream
   After=network.target

   [Service]
   Type=simple
   ExecStart=/bin/bash -c 'rpicam-vid -t 0 --width 1280 --height 720 --framerate 15 --inline -o - | cvlc stream:///dev/stdin --sout "#rtp{sdp=rtsp://:8554/stream}" :demux=h264'
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pi5-rtsp
   sudo systemctl start pi5-rtsp
   ```

   After reboot, the stream should be at `rtsp://<PI_5_IP>:8554/stream`.

**Alternative:** Run **pi-libcamera-rtsp** (Docker) on the Pi 5 and use the RTSP URL it prints in Home Assistant the same way.

### Step 3: Add the camera in Home Assistant

1. Open **Settings → Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **Generic** or **FFmpeg** and add it.
4. For the stream URL, use:

   ```text
   rtsp://<PI_5_IP>:8554/stream
   ```

   Replace `<PI_5_IP>` with the camera Pi’s IP (e.g. `192.168.1.20`).
5. Name the camera (e.g. “Kitchen Pi Camera”) and finish.

You should get an entity such as `camera.kitchen_pi_camera`.

### Step 4: Dashboard

1. Edit the dashboard (or add a card).
2. Add a **Picture** or **Picture Glance** card.
3. Set **Camera entity** to the new camera.
4. Save.

### Summary

| Step | Action |
|------|--------|
| 1 | Raspberry Pi OS on Pi 5, enable camera in `raspi-config`, test with `rpicam-hello` or `libcamera-still`. |
| 2 | Install VLC, run `rpicam-vid \| cvlc` RTSP, add `pi5-rtsp.service` for boot. |
| 3 | HA: **Settings → Devices & Services → Add Integration** → Generic/FFmpeg → `rtsp://<PI_5_IP>:8554/stream`. |
| 4 | Add a Picture / Picture Glance card for the camera entity. |

### Tips

- Give the camera Pi a **static IP** (DHCP reservation on the router or static config on the Pi) so the RTSP URL stays stable.
- If the stream is slow or unstable, lower resolution (e.g. `--width 640 --height 480`) in both the manual command and the systemd `ExecStart` line.
