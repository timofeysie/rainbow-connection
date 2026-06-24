# Time lapse project

This project follows on from the [Raspberry Pi Zero time lapse camera project](docs\raspberry-pi-zero-w-setup.md) which describes how to start from scratch the the Raspberry Pi Zero.

This document has some overlap, as it describes how to work with the zero for various tasks once it is setup.

## Workflow

```bash
ping raspberrypi # confirm the zero is online and get the IP address
ssh tim@raspberrypi # login to the zero via secure shell
libcamera-jpeg -o /var/www/html/images/test4.jpg # take a test image
sudo nano /home/tim/python/capture_image.py # open the image capture script
sudo nano /var/www/html/script.js # open the image gallery script
scp tim@192.168.200.166:/var/www/html/images/*.jpg C:\Users\timof\OneDrive\Pictures\zero\ # copy files from zero to pc
rm /var/www/html/images/* # remove the files on the zero (must be shh logged in)
systemctl status nginx.service # check the image gallery site is running
ps aux | grep python # check all running scripts
ps aux | grep capture_image.py # check a particular script
tail -f /home/tim/python/capture_image.py # check the time lapse script log
kill 265 # stop a script at a certain PIN
sudo pkill -f capture_image.py # Stop all running script
rm /home/tim/capture_image.log # delete the log file as it might grow too large
/usr/bin/python3 /home/tim/python/capture_image.py # run the time lapse script manually
sudo reboot
```

## Zero as projector

Use VideoLAN app to play a video on boot.

Install and configure vlc:

```sh
sudo apt-get install vlc
```

Create a new shell script, for example, playvideo.sh, using the following command:

```sh
nano playvideo.sh
```

Add the following lines to the script:

```sh
#!/bin/bash
while true; do
    vlc --fullscreen --loop /home/tim/Videos/human-as-nature-scale.mp4
    # Check for a specific key press to interrupt video and launch desktop
    read -rsn1 -t 1 key
    if [[ $key == "q" ]]; then
        break
    fi
done
```

Replace /home/tim/Videos/filename.ext with the actual path and filename of your video.

Make the script executable:

```sh
chmod +x playvideo.sh
```

Configure autostart on boot (You may need to create this file first if it doesn't exist):

```sh
mkdir -p ~/.config/lxsession/LXDE-pi/
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add the following line at the end of the file:

```sh
@lxterminal -e /home/tim/playvideo.sh
```

Replace /home/tim/playvideo.sh with the actual path to your shell script.

Save the file and exit the text editor.

Reboot the Raspberry Pi:

```sh
sudo reboot
```

Make sure the audio is working:

```sh
sudo raspi-config
```

Test the speaker:

```sh
speaker-test -t wav -c 2
```
## Deleting images

To remove all the images, I use this command:

```
rm /home/tim/capture_image.log 
```

Sometimes, you may not want to delete all the images.

To delete a range of images by date, we can do the following:

Confirm exactly what will be deleted:

```
for f in image_*.jpg; do
  if [[ "$f" > "image_2026-05-09_15-29-25.jpg" && "$f" < "image_2026-05-11_12-47-15.jpg" ]]; then
    echo "$f"
  fi
done
```

Actually delete them with:

```
for f in image_*.jpg; do
  if [[ "$f" > "image_2026-05-09_15-29-25.jpg" && "$f" < "image_2026-05-11_12-47-15.jpg" ]]; then
    rm "$f"
  fi
done
```

You probably actually need to use sudo:

```
sudo rm "$f"
```

This one asks before each delete:

```
rm -i "$f"
```
