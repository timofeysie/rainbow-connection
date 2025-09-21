# Emoji Badge Controller Setup

Setting up an emoji badge controller on a Raspberry Pi Zero W with a [Waveshare 1.44inch LCD display HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT) involves a number of steps such as libraries, getting the script on the device and running it on startup.

Since this project is still ongoing, currently I have a lot of notes of how I got to this point.  I will be refining these by removing unnecessary steps as well as how to copy a ssd card with everything already setup.

Some of these notes are prompts from using ChatGPT while working on the device.

python emoji_key_basic.py <- this menu works but no lcd display

python smiley-matrix-4.py <- emoji, menu emojis and menu text
needs menu navigation and emoji select  and update options

python smiley-matrix-controller.py

https://stackblitz.com/github/timofeysie/rainbow-connection/blob/master/python/emoji-os/emoji-os-zero.py

I have a Waveshare 1.44inch LCD display HAT for Raspberry Pi.
It is connected to my Raspberry pi 5 B.

I have followed the instruction in this wiki to set it up:
https://www.waveshare.com/wiki/1.44inch_LCD_HAT

In this wiki it says:
'If you use bookworm system, only the lgpio library is available, 
bcm2835 and wiringPi libarary cannot be installed or used. 
Please note that the python library does not need to be installed, 
you can directly run the demo'

$ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"

I run these instructions from the wiki:
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev

sudo apt-get install p7zip-full -y
wget https://files.waveshare.com/upload/f/fa/1.44inch-LCD-HAT-Code.7z
7z x 1.44inch-LCD-HAT-Code.7z
sudo chmod 777 -R 1.44inch-LCD-HAT-Code
cd 1.44inch-LCD-HAT-Code/RaspberryPi/

cd python
sudo python main.py
sudo python key_demo.py

I want this script to run on Raspberry pi startup so that I can test that it will run on a Raspberry pi Zero W also with a Waveshare 1.44inch LCD display HAT.

In this way, I want to take the SSD card out of the Raspberry Pi 5 B and put it in the Zero and test that it will also work there.

/home/tim/1.44inch-LCD-HAT-Code/RaspberryPi/python/key_demo.py


## Running a script on startup

I use an old fashioned rc.local method to run a script on the raspberry pi startup.

My python instance is here: ```/usr/bin/python```

The script I want to run is here: ```/home/tim/emoji-os/emoji_os_zero_1.py```

I can run the script in either of these two ways as they both run it:

From the emoji-os directory: ```python emoji_os_zero_1.py```

From anywhere: ```/usr/bin/python /home/tim/emoji-os/emoji_os_zero_1.py```

To run this script on startup On my raspberry pi I run:

```sudo nano /etc/rc.local```

And enter this:

```sh
#!/bin/sh -e

# Wait for the system to settle (network, devices, etc.)
#sleep 15

# Run your Python script and log output
/usr/bin/python /home/tim/emoji_os/emoji_os_zero_1.py >> /tmp/key_demo.log 2>&1 &

#exit 0
```

I reboot, but the script doesn't run.

I do this:

```sh
tim@raspberrypi:~ $ ps aux | grep emoji_os_zero_1.py
tim         1961  0.0  0.0   6384  1584 pts/2    S+   09:57   0:00 grep --color=auto emoji_os_zero_1.py
```

What is wrong?

sudo chmod +x /etc/rc.local

chmod +x /home/tim/emoji-os/emoji_os_zero_1.py

I tried this:

```sh
tim@raspberrypi:~ $ sudo chmod +x /etc/rc.local
tim@raspberrypi:~ $ chmod +x /home/tim/emoji-os/emoji_os_zero_1.py
tim@raspberrypi:~ $ sudo systemctl status rc-local.service
● rc-local.service - /etc/rc.local Compatibility
     Loaded: loaded (/lib/systemd/system/rc-local.service; enabled-runtime; preset: enabled)
    Drop-In: /usr/lib/systemd/system/rc-local.service.d
             └─debian.conf
     Active: active (exited) since Fri 2025-09-12 09:54:20 BST; 26min ago
       Docs: man:systemd-rc-local-generator(8)
    Process: 1401 ExecStart=/etc/rc.local start (code=exited, status=0/SUCCESS)
        CPU: 1ms

Sep 12 09:54:20 raspberrypi systemd[1]: Starting rc-local.service - /etc/rc.local Compatibility...
Sep 12 09:54:20 raspberrypi systemd[1]: Started rc-local.service - /etc/rc.local Compatibility.
```

```sh
#!/bin/sh -e

sleep 10

/usr/bin/python3 /home/tim/emoji-os/emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1 &

exit 0

```

After reboot, I don't see that file:

```sh
tim@raspberrypi:~ $ cat /home/tim/rc.local.log
cat: /home/tim/rc.local.log: No such file or directory
```

I check files and permissions like this:

```sh
tim@raspberrypi:~ $ ls -l /usr/bin/python
lrwxrwxrwx 1 root root 7 Jun 17  2024 /usr/bin/python -> python3
tim@raspberrypi:~ $ ls -l /home/tim/emoji-os/emoji_os_zero_1.py
-rwxr-xr-x 1 tim tim 17151 Sep 12 09:27 /home/tim/emoji-os/emoji_os_zero_1.py
tim@raspberrypi:~ $ sudo touch /home/tim/rc.local.log
sudo chown tim:tim /home/tim/rc.local.log
```

I create a new version of the file like this:

```sh
#!/bin/sh -e

sleep 10

echo "=== rc.local starting ===" >> /home/tim/rc.local.log
echo "Running emoji_os_zero_1.py..." >> /home/tim/rc.local.log

/usr/bin/python /home/tim/emoji-os/emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1

echo "=== rc.local done ===" >> /home/tim/rc.local.log

exit 0
```

I check the file is executable again:

```sh
sudo chmod +x /etc/rc.local
```

## Create the .img backup (Win32 Disk Imager)

Download Win32 Disk Imager

Plug in your Raspberry Pi SSD via USB.

Find its drive letter in File Explorer (e.g. E:).

Open Win32 Disk Imager (as Administrator).

Choose a file path for the backup, e.g. C:\raspi_backup.img.

Select the SSD drive letter.

Click Read → this makes a full .img backup of your SSD.

🔹 Step 2: Restore with Raspberry Pi Imager

Download Raspberry Pi Imager
 if you don’t have it already.

Insert the new SSD.

In Pi Imager:

Click Choose OS → Use custom → select your raspi_backup.img.

Click Choose Storage → select the target SSD.

Click Write.

✅ Result: You now have a full clone. The new SSD will boot with all packages, configs, and settings intact.

Would you like me to also show you how to shrink the .img file (so it’s not huge if your SSD is 128 GB but only 8 GB is used)? That way it’s faster to back up and restore.

You said:
In the disk imagewr, I see F: drive, but I cannot select it, I must instead select 'overlays'.  Is this correct?  
ChatGPT said:

Good catch — that screen explains the confusion.

In Win32 Disk Imager, you do not select files or folders on the Pi’s SSD (like overlays, kernel.img, etc). Those are just the contents of one of the Pi’s partitions that Windows can see (the small FAT32 “boot” partition).

What you actually need to do is:

Ignore the file browser window showing overlays and kernel.img.

That window is asking you to choose where to save the .img backup file, not to pick things from the Pi SSD.

Instead:

In the Image File field, type a filename for your backup, e.g.:

C:\Users\<yourname>\raspi_backup.img


In the Device dropdown (to the right), select the whole drive letter of your Pi SSD (e.g. F:).

Then click Read.

Win32 Disk Imager will read the entire SSD device (all partitions, not just bootfs) and dump it into raspi_backup.img.

That .img file is your complete backup.

⚠️ Important distinction:

The F:\ you’re seeing is only the boot partition.

The actual Pi OS and all your installed packages live on the Linux partition, which Windows doesn’t show in File Explorer (because it’s ext4 and Windows doesn’t natively read ext4).

That’s why we use Win32 Disk Imager: it clones the raw disk, including those hidden partitions, not just the visible files.