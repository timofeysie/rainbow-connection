# HQ Camera Setup

This document describes the setup of the following:

- Raspberry Pi High Quality (HQ) Camera
- Raspberry Pi 16mm Telephoto Camera Lens (C-Mount)
- Raspberry pi 5

[Raspberry Pi 6mm Wide Angle Camera Lens](https://core-electronics.com.au/raspberry-pi-6mm-wide-angle-lens.html)
[Raspberry Pi 16mm Telephoto Camera Lens](https://core-electronics.com.au/raspberry-pi-16mm-telephoto-lens.html)

[Raspberry Pi HQ Camera Guide](https://core-electronics.com.au/attachments/Raspberry-Pi-HQ-Camera-Guide.pdf)

## Workflow

To take a picture:

```sh
rpicam-still -o test.jpg
```

Show the current image live to allow focusing:

```sh
rpicam-hello -t 0 --qt-preview
```

## Setup

I have done these steps so far to try and setup a Raspberry Pi High Quality (HQ) Camera on a Rasbperry pi 5 using an OS more recent than bookwork.:

```sh
tim@raspberrypi:~ $ rpicam-hello
[0:01:03.559500652] [1432]  INFO Camera camera_manager.cpp:330 libcamera v0.5.2+99-bfd68f78
Made X/EGL preview window
ERROR: *** no cameras available ***


tim@raspberrypi:~ $ raspistill -o test.jpg
bash: raspistill: command not found
tim@raspberrypi:~ $ libcamera-hello
bash: libcamera-hello: command not found
tim@raspberrypi:~ $ libcamera-hello --camera 0
bash: libcamera-hello: command not found
```

I have ensured the camera is properly connected to the Raspberry Pi via the Camera Serial Interface (CSI) port, and the ribbon cable is securely attached.

I read: "the official camera module, the Raspberry Pi OS should automatically detect it after booting up. So, unlike previous boards, you don’t need to enable the camera option via the Raspberry Pi Configuration tool. The raspistill package has been deprecated in the Bullseye variant of the Raspberry Pi OS, so you'll have to use the libcamera library instead. To check whether the cable is working properly,"
Is 

the OS has now been updated from Bookworm to Trixie 

sudo raspi-config

the correct command then for this setup?

I do not see a camera option in interfaces.  I see these options:
I1 SSH
I2 RPi Connect
I3 VNC
I4 SPI
I5 I2C
I6 Serial Port
I7 1-Wire

If the On newer OS versions Correct tools are rpicam then why do i see this?
```
tim@raspberrypi:~ $ rpicam-still -o test.jpg
[0:18:38.739644926] [3808]  INFO Camera camera_manager.cpp:330 libcamera v0.5.2+99-bfd68f78
WARNING: Capture will not make use of temporal denoise
         Consider using the --zsl option for best results, for example:
         rpicam-still --zsl -o test.jpg
Made X/EGL preview window
ERROR: *** no cameras available ***
```

I have done:
```
sudo apt update
sudo apt install -y rpicam-apps
```

Then this:
```
tim@raspberrypi:~ $ which rpicam-hello
/usr/bin/rpicam-hello
tim@raspberrypi:~ $ libcamera-list-cameras
bash: libcamera-list-cameras: command not found
```

And this:
```
tim@raspberrypi:~ $ dmesg | grep -i imx
[    0.029029] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.029053] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.029166] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.029190] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.378158] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.378449] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.378463] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.678221] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.678265] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    3.629111] rp1-cfe 1f00110000.csi: found subdevice /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    3.975657] imx477 10-001a: failed to read chip id 477, with error -5
[    3.976491] imx477 10-001a: probe with driver imx477 failed with error -5

```

And this:
```
tim@raspberrypi:~ $ grep camera /boot/firmware/config.txt
# Automatically load overlays for detected cameras
camera_auto_detect=0
```

Next...

sudo nano /boot/firmware/config.txt

camera_auto_detect=1

rudo reboot

But:

```
tim@raspberrypi:~ $ libcamera-list-cameras
bash: libcamera-list-cameras: command not found
tim@raspberrypi:~ $ which rpicam-hello
/usr/bin/rpicam-hello
tim@raspberrypi:~ $ rpicam-still -o test.jpg
[0:00:57.570702926] [1540]  INFO Camera camera_manager.cpp:340 libcamera v0.6.0+rpt20251202
WARNING: Capture will not make use of temporal denoise
         Consider using the --zsl option for best results, for example:
         rpicam-still --zsl -o test.jpg
Made X/EGL preview window
ERROR: *** no cameras available ***
```

Next, leaving the cam on

rpicam-hello



      

i am on the new trixie os.
this works but disappears:
```
rpicam-still -o test.jpg
```

Only shows the first image, but not a stream so i cant focus the camera.
rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:8888

this works:

rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:8888

Find the Zero's IP address on the local network
hostname -I

GOTO
http:192.168.68.59
This site can’t be reached

Next, using http://192.168.68.59:8888/ i see this:

rpicam-vid -t 0 --codec mjpeg --inline --listen -o tcp://0.0.0.0:8888

When i do 
 rpicam-vid -t 0 --codec mjpeg --inline --listen -o tcp://0.0.0.0:8888
and open 
http://192.168.68.59:8888
The camera windows opens briefly then closes and i see this error in the terminal:

```
[0:59:09.685537352] [2770]  INFO RPI pisp.cpp:720 libpisp version 1.3.0
[0:59:09.689845098] [2770]  INFO IPAProxy ipa_proxy.cpp:180 Using tuning file /usr/share/libcamera/ipa/rpi/pisp/imx477.json
[0:59:09.698958850] [2770]  INFO Camera camera_manager.cpp:223 Adding camera '/base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a' for pipeline handler rpi/pisp
[0:59:09.699057165] [2770]  INFO RPI pisp.cpp:1181 Registered camera /base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a to CFE device /dev/media1 and ISP device /dev/media2 using PiSP variant BCM2712_D0
Made X/EGL preview window
Mode selection for 640:480:12:P
    SRGGB10_CSI2P,1332x990/0 - Score: 1305.05
    SRGGB12_CSI2P,2028x1080/0 - Score: 701.167
    SRGGB12_CSI2P,2028x1520/0 - Score: 607.329
    SRGGB12_CSI2P,4056x3040/0 - Score: 1494.33
Stream configuration adjusted
[0:59:13.693486258] [2767]  INFO Camera camera.cpp:1215 configuring streams: (0) 640x480-YUV420/sYCC (1) 2028x1520-BGGR_PISP_COMP1/RAW
[0:59:13.693634518] [2770]  INFO RPI pisp.cpp:1485 Sensor: /base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a - Selected sensor format: 2028x1520-SBGGR12_1X12/RAW - Selected CFE format: 2028x1520-PC1B/RAW
terminate called after throwing an instance of 'std::runtime_error'
  what():  failed to send data on socket
Aborted
```

Next...
I try:
```
rpicam-vid -t 0 \
  --codec mjpeg \
  --roi 0.4,0.4,0.2,0.2 \
  --inline -o - | \
mjpg_streamer -i "input_file.so -f /dev/stdin" \
              -o "output_http.so -p 8888 -w /usr/share/mjpg-streamer/www"

```

But see this output:
```
...
[1:05:47.262564862] [2873]  INFO IPAProxy ipa_proxy.cpp:180 Using tuning file /usr/share/libcamera/ipa/rpi/pisp/imx477.json
[1:05:47.271251339] [2873]  INFO Camera camera_manager.cpp:223 Adding camera '/base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a' for pipeline handler rpi/pisp
[1:05:47.271293339] [2873]  INFO RPI pisp.cpp:1181 Registered camera /base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a to CFE device /dev/media1 and ISP device /dev/media2 using PiSP variant BCM2712_D0
Made X/EGL preview window
Mode selection for 640:480:12:P
    SRGGB10_CSI2P,1332x990/0 - Score: 1305.05
    SRGGB12_CSI2P,2028x1080/0 - Score: 701.167
    SRGGB12_CSI2P,2028x1520/0 - Score: 607.329
    SRGGB12_CSI2P,4056x3040/0 - Score: 1494.33
Stream configuration adjusted
[1:05:47.353704616] [2869]  INFO Camera camera.cpp:1215 configuring streams: (0) 640x480-YUV420/sYCC (1) 2028x1520-BGGR_PISP_COMP1/RAW
[1:05:47.353810727] [2873]  INFO RPI pisp.cpp:1485 Sensor: /base/axi/pcie@1000120000/rp1/i2c@80000/imx477@1a - Selected sensor format: 2028x1520-SBGGR12_1X12/RAW - Selected CFE format: 2028x1520-PC1B/RAW
Received signal 13
Received signal 13
terminate called after throwing an instance of 'std::runtime_error'
  what():  failed to write output bytes

```

-----------------------------

Cams --------------------

To enable the camera in Raspbian: 
Menu / Preferences / Raspberry Pi Configuration / Interfaces tab / Camera / select Enabled / Click OK reboot Raspberry Pi when prompted.


Raspberry Pi High Quality (HQ) Camera
$85.00
https://core-electronics.com.au/raspberry-pi-hq-camera.html

Raspberry Pi 6mm Wide Angle Camera Lens (CS-Mount)
$42.00
https://core-electronics.com.au/raspberry-pi-6mm-wide-angle-lens.html

https://core-electronics.com.au/attachments/Typical_CS-Mount_Lens_Guide.pdf
https://core-electronics.com.au/attachments/Raspberry-Pi-HQ-Camera-Guide.pdf
https://core-electronics.com.au/attachments/20200408_PT361060M3MP12.pdf

Plate for High Quality Camera
$5.45
https://core-electronics.com.au/the-pi-hut-raspberry-pi-zero-basic-mounting-plate-for-high-quality-camera.html

https://thepihut.com/blogs/raspberry-pi-tutorials/zero-mounting-plate-for-high-quality-camera-assembly-guide

Example fitting instructions for a typical CS-mount lens


setip ====

I have done these steps so far to try and setup a Raspberry Pi High Quality (HQ) Camera on a Rasbperry pi 5 using an OS more recent than bookwork.:

tim@raspberrypi:~ $ which libcamera-hello
tim@raspberrypi:~ $ which rpicam-vid
/usr/bin/rpicam-vid
tim@raspberrypi:~ $ which libcamera-hello
tim@raspberrypi:~ $ which libcamera-hello
tim@raspberrypi:~ $ which rpicam-still
/usr/bin/rpicam-still
tim@raspberrypi:~ $ which rpicam-still
/usr/bin/rpicam-still

tim@raspberrypi:~ $ rpicam-hello [0:14:47.970551641] [3341] INFO Camera camera_manager.cpp:330 libcamera v0.5.2+99-bfd68f78 Made X/EGL preview window ERROR: *** no cameras available ***

dtoverlay=imx477,cam0


Then        

tim@raspberrypi:~ $ rpicam-hello
[0:02:32.114928469] [1919]  INFO Camera camera_manager.cpp:330 libcamera v0.5.2+99-bfd68f78
Made X/EGL preview window
ERROR: *** no cameras available ***

tim@raspberrypi:~ $ dmesg | grep imx477
[    0.029031] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.029056] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.029168] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.029192] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.534081] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.534377] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    0.534391] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.823501] /axi/pcie@1000120000/rp1/csi@110000: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    0.823536] /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a: Fixed dependency cycle(s) with /axi/pcie@1000120000/rp1/csi@110000
[    8.270132] rp1-cfe 1f00110000.csi: found subdevice /axi/pcie@1000120000/rp1/i2c@88000/imx477@1a
[    8.648486] imx477 10-001a: failed to read chip id 477, with error -5
[    8.648642] imx477 10-001a: probe with driver imx477 failed with error -5

Then i edit:

sudo nano /boot/config.txt

camera_auto_detect=0
dtoverlay=imx477,cam0

sudo reboot

## Old notes

Find the Zero's IP address on the local network
hostname -I

http://192.168.68.59:8888/
