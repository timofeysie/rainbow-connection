# Time lapse project

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
    vlc --fullscreen --loop /home/tim/Videos/filename.ext
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

