# Emoji Badge Controller Setup

I want to use a rc.local method to run a script on the raspberry pi startup.

My python instance is here: /usr/bin/python

The script I want to run is here: /home/tim/emoji-os/emoji_os_zero_1.py

I can run the script in either of these two wasy as they both run it:

From the emoji-os directory: ```python emoji_os_zero_1.py```

From anywhere: ```/usr/bin/python /home/tim/emoji-os/emoji_os_zero_1.py```

To run this script on startup On my rasbperry pi I run:

```sudo nano /etc/rc.local```

And enter this:

```
#!/bin/sh -e

# Wait for the system to settle (network, devices, etc.)
#sleep 15

# Run your Python script and log output
#/usr/bin/python /home/tim/emoji_os/emoji_os_zero_1.py >> /tmp/key_demo.log 2>&1 &

#exit 0
```

I reboot, but the script doesn't run.

I do this:
```
tim@raspberrypi:~ $ ps aux | grep emoji_os_zero_1.py
tim         1961  0.0  0.0   6384  1584 pts/2    S+   09:57   0:00 grep --color=auto emoji_os_zero_1.py
```

What is wrong?

sudo chmod +x /etc/rc.local

chmod +x /home/tim/emoji-os/emoji_os_zero_1.py

I tried this:
```
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


```
#!/bin/sh -e

sleep 10

/usr/bin/python3 /home/tim/emoji-os/emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1 &

exit 0

```

After reboot, I don't see that file:

```
tim@raspberrypi:~ $ cat /home/tim/rc.local.log
cat: /home/tim/rc.local.log: No such file or directory
```

I check files and permissions like this:

```
tim@raspberrypi:~ $ ls -l /usr/bin/python
lrwxrwxrwx 1 root root 7 Jun 17  2024 /usr/bin/python -> python3
tim@raspberrypi:~ $ ls -l /home/tim/emoji-os/emoji_os_zero_1.py
-rwxr-xr-x 1 tim tim 17151 Sep 12 09:27 /home/tim/emoji-os/emoji_os_zero_1.py
tim@raspberrypi:~ $ sudo touch /home/tim/rc.local.log
sudo chown tim:tim /home/tim/rc.local.log
```


I create a new version of the file like this:

```
#!/bin/sh -e

sleep 10

echo "=== rc.local starting ===" >> /home/tim/rc.local.log
echo "Running emoji_os_zero_1.py..." >> /home/tim/rc.local.log

/usr/bin/python /home/tim/emoji-os/emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1

echo "=== rc.local done ===" >> /home/tim/rc.local.log

exit 0
```

I check the file is executable again:

```
sudo chmod +x /etc/rc.local
```
