# Raspberry Pi Zero time lapse camera project

This document details how to setup a Raspberry Pi Zero in headless mode for taking time lapse images.

The "Workflow Commands" section is for reference after the project is setup.

For the full tutorial of how to set up the zero from the beginning, start at the "How to setup a Raspberry Pi Zero W with Headless setup" section.

## Workflow Commands

```bash
ping raspberrypi # confirm the zero is online and get the IP address
ssh tim@raspberrypi # login to the zero via secure shell
libcamera-jpeg -o /var/www/html/images/test4.jpg # take a test image
sudo nano /home/tim/python/capture_image.py # open the image capture script
sudo nano /var/www/html/script.js # open the image gallery script
```

### Restart nginx

```bash
sudo systemctl restart nginx.service
```

### Start the time-lapse script manually

```bash
sudo python3 /home/tim/python/capture_image.py
```

### Check syntax

```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
sudo service nginx reload
```

### Nano commands

```bash
Ctrl + Shift + 6 to start selecting
Ctrl + K to cut
Ctrl + U to paste the cut text
Shift + Insert paste text copied from computer
Ctrl + O then press Enter to save the file
Ctrl + X to exit nano
```

### Find the Zero's IP address on the local network

```bash
hostname -I
```

### Copy files from Zero to PC

```bash
scp tim@192.168.200.166:/var/www/html/images/*.jpg C:\Users\timof\OneDrive\Pictures\zero\
```

Remove the files on the zero:

```bash
rm /var/www/html/images/*
```

## How to setup a Raspberry Pi Zero W with Headless setup

[This article](https://www.techcoil.com/blog/how-to-host-a-static-website-on-your-raspberry-pi-zero-w-with-raspbian-stretch-lite-and-nginx-web-server/) links to other detail offshoot articles that drill down into the steps.

I will also add the steps to setup the nginx server and creation of a static website to host the images taken by the camera.

Notes for how to use the nano editor are also included.

## Setup a new SD card

- use Pi Imager to flash the OS.  Details [here](https://www.techcoil.com/blog/how-to-prepare-the-operating-system-to-run-your-raspberry-pi-with-your-windows-machine/)

- create an empty file named as "ssh" and copy it to the root directory of the SD card

- wpa_supplicant.conf file that contains your WiFi network configuration

Some sample files are in the python\utils directory of this repo, as well as available for download in the link above with a bit of searching.

## The wpa_supplicant.conf file

This is the format of the file from the video in the link above:

```conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
	ssid="your_wifi_network_name"
	psk="your_wifi_network_password"
	key_mgmt=WPA-PSK
}
```

### Setup a user

As shown in this [new login method](https://www.raspberrypi.com/news/raspberry-pi-bullseye-update-april-2022/), there are various ways to set up a user to use on first boot.

To set up a user on first boot and bypass the wizard completely, create a file called userconf.txt with a single line in the format name:password-hash

To create a password has, run this command:

```sh
echo 'password' | openssl passwd -6 -stdin
```

Then, after you boot up, you can ping the zero until you see a valid response.

```sh
ping raspberrypi
Pinging raspberrypi.modem [192.168.0.49] with 32 bytes of data:
Reply from 192.168.0.49: bytes=32 time=298ms TTL=64
...
```

Then you can login with the credentials you setup.

```sh
ssh name@raspberrypi
```

It was taking a long time for the zero to respond to the pings.  I think it was too far away from the wifi, as possibly it's as powerful as my laptop wifi which will connect immediately.  I moved the zero closer to where the wifi router is and then it would connect quickly.

## Setup Nginx

The article recommends Raspbian Stretch Lite OS, but I found Nginx works on a regular distro also.

```sh
sudo apt-get update
sudo apt-get install nginx -y
systemctl status nginx.service
```

```sh
tim@raspberrypi:~ $ systemctl status nginx.service
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2023-09-01 07:21:55 BST; 1min 8s ago
       Docs: man:nginx(8)
    Process: 1526 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 1527 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 1608 (nginx)
      Tasks: 2 (limit: 414)
        CPU: 397ms
     CGroup: /system.slice/nginx.service
             ├─1608 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             └─1611 nginx: worker process
Sep 01 07:21:55 raspberrypi systemd[1]: Starting A high performance web server and a reverse proxy server...
Sep 01 07:21:55 raspberrypi systemd[1]: nginx.service: Failed to parse PID from file /run/nginx.pid: Invalid argument
Sep 01 07:21:55 raspberrypi systemd[1]: Started A high performance web server and a reverse proxy server.
```

After the server starts, you can visit 192.168.0.49 and see the default site.

The article shows instructions on how to configure a domain name.

sudo nano /etc/nginx/sites-enabled/yourdomain.com.conf

```sh
server {
        server_name yourdomain.com www.yourdomain.com;
        listen 80;
        root /var/www/yourdomain.com;
        index index.html;
}
```

However, I want to create a static site to serve all the images in a directory on the device to the local network only for now.

I actually couldn't get it to configure my own site, so I ended up using the default site created by nginx.

That is in this location: /var/www/html/index.html

sudo nano /etc/nginx/sites-available/default

create your configuration file:

sudo nano /etc/nginx/sites-available/

sudo nano /etc/nginx/sites-enabled/default

```sh
    location /images/ {
        alias /var/www/html/images/;
        autoindex on;
    }
```

Save the file and then restart the server:

sudo systemctl restart nginx.service

or

sudo service nginx restart

There is a special command to determine if the file is valid:

sudo nginx -t

## The website code

I like to separate code by type, so will have separate javascript, css and html files.

Create a script.js file:

```bash
sudo nano /var/www/html/script.js
```

```js
document.addEventListener("DOMContentLoaded", function () {
    const imageContainer = document.getElementById("displayed-image");
    const imageSelect = document.getElementById("image-select");
    const playButton = document.getElementById("play-button");
    let imageList = [];

    // Function to fetch the list of images from the /images directory
    function fetchImagesList() {
        fetch("/images/") // Use the correct path to your images directory
            .then((response) => response.text())
            .then((data) => {
                console.log('data', data)
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, "text/html");
                const links = doc.querySelectorAll("a");

                imageList = Array.from(links)
                    .map((link) => link.getAttribute("href"))
                    .filter((href) => href.endsWith(".jpg") || href.endsWith(".jpeg"));

                // Populate the select element with image options
                populateImageSelect();

                // Set the default image to the last image in the list
                if (imageList.length > 0) {
                    updateDisplayedImage(imageList[imageList.length - 1]);
                }
            })
            .catch((error) => console.error("Error fetching images:", error));
    }

    // Function to populate the select element with image options
    function populateImageSelect() {
        imageList.forEach((image) => {
            const option = document.createElement("option");
            option.value = image;
            option.text = image;
            imageSelect.appendChild(option);
        });
        console.log('imageList', imageList)
    }

    // Function to update the displayed image
    function updateDisplayedImage(imagePath) {
        imageContainer.src = `/images/${imagePath}`;
        console.log('imageContainer.src', imageContainer.src)
    }

    // Event listener for the select element
    imageSelect.addEventListener("change", function () {
        const selectedImage = imageSelect.value;
        console.log('selectedImage', selectedImage)
        updateDisplayedImage(selectedImage);
    });

    // Event listener for the "Play" button
    playButton.addEventListener("click", function () {
        let currentIndex = 0;
        const playInterval = setInterval(function () {
            if (currentIndex >= imageList.length) {
                clearInterval(playInterval); // Stop playing when all images are displayed
            } else {
                const currentImage = imageList[currentIndex];
                updateDisplayedImage(currentImage);
                currentIndex++;
            }
            console.log('currentIndex', currentIndex)
        }, 1000); // Change images every 1 second
    });

    // Fetch the list of images when the page loads
    fetchImagesList();
});
```

### The css file

sudo nano /var/www/html/style.css

```css
.gallery-container {
    display: flex;
    flex-direction: column;
}

.image-container {
    max-width: 95vh;
}

img {
    max-width: 100%;
    max-height: 100%;
}

select {
    max-height: 90vh;
    overflow-y: auto;
}
#controls-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    position: absolute;
    top: 0;
    right: 0;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.7); /* Optional: Add a background color with transparency */
}

/* Style the "Play" button */
#play-button {
    margin-bottom: 10px;
}
```

If the changes don't show, restart nginx:

sudo service nginx reload

### The index.html file

sudo nano /var/www/html/index.html

Also could be: sudo nano /var/www/html/index.nginx-debian.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Gallery</title>
    <link rel="stylesheet" type="text/css" href="/style.css">
</head>
<body>
    <h3>Image Gallery</h3>
    
    <div id="image-display">
        <img id="displayed-image" src="" alt="Displayed Image" style="max-height: 90vh;">
    </div>
    
    <div id="controls-container">
        <button id="play-button">Play</button>
        <select id="image-select" size="10" style="max-height: 90vh;">
        </select>
    </div>
    
    <script src="/script.js"></script>
</body>
</html>
```

After editing the files, you need to restart nginx

## Taking pictures

The libcamera-jpeg command is one way to take pictures.  It is used like this:

libcamera-jpeg -o test-1.jpg

However, we want to put those pictures in the directory served by the html.

```sh
sudo mkdir -p /var/www/html/images
sudo chmod 755 /var/www/html/images
sudo libcamera-jpeg -o /var/www/html/images/image-1.jpg
```

## Taking time lapse pictures

Open the image capture script with the following command:

```sh
sudo nano /home/tim/python/capture_image.py
```

This is an early version:

```py
import os
import picamera
from time import sleep
from datetime import datetime

# Function to capture an image and save it with a timestamp-based filename
def capture_image():
    # Get the current date and time
    current_time = datetime.now().time()
    
    # Check if the current time is between 9 AM and 5 PM
    if current_time >= datetime.strptime("09:00:00", "%H:%M:%S").time() and current_time <= datetime.strptime("17:00:00", "%H:%M:%S").time():
        # Define the image file path
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = "/var/www/html/images/image_{}.jpg".format(timestamp)
        
        # Capture an image and save it
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)  # Set the resolution (adjust as needed)
            camera.capture(image_path)

# Main program loop
while True:
    capture_image()  # Capture an image if the time is between 9 AM and 5 PM
    sleep(60)  # Wait for 60 seconds before checking the time again, this will include the time it takes to take the picture which is about 8 seconds.
    # 30 minutes (1800 seconds)
```

Open the crontab configuration:

```bash
crontab -e
```

```bash
@reboot /usr/bin/python3 /path/to/your/python/script.py &
```

Save and exit the crontab editor.

Reboot the Raspberry Pi Zero:

```bash
sudo reboot
```

Check Script Execution:

```bash
ps aux | grep python
```

Check for Errors:

```bash
python3 /path/to/your/python/script.py
```

For me this is:

```bash
sudo python3 /home/tim/python/capture_image.py
```

Monitor the output:

```bash
tail -f /home/tim/python/capture_image.log
```

## Setting the time

```bash
sudo apt install ntp
sudo nano /etc/ntp.conf
```

Verify that the configuration file points to valid NTP servers like this:

```bash
server pool.ntp.org
server 0.debian.pool.ntp.org iburst

sudo systemctl restart ntp
```

Set Timezone (optional):

You can also set the timezone for your Raspberry Pi using the timedatectl command. Replace Your_Timezone with your desired timezone (e.g., America/New_York):

```bash
sudo timedatectl set-timezone Your_Timezone
```

```bash
timedatectl list-timezones
```

```bash
sudo timedatectl set-timezone Australia/Sydney
sudo timedatectl set-timezone Asia/Seoul
```

Enable NTP sync on boot

```bash
sudo systemctl enable ntp
```

## Copy images to the PC

Option one is to copy all the images to the boot dir, take out the memory card and copy the files onto the PC.  However, this will double the amount of files on the zero which maxed out the memory on my SD card the first time I tried it.

Option 2 was to do it all from the command line first from the PC (which requires login):

```bash
scp tim@192.168.45.194:/var/www/html/images/*.jpg C:\Users\timof\OneDrive\Pictures\zero\
```

Remove the files on the zero after logging in to the zero:

```bash
rm /var/www/html/images/*
```

## Ping raspberry pi

Data slayer tutorial: [The New Method to Setup Raspberry Pi Zero (2023 Tutorial)](https://www.youtube.com/watch?v=yn59qX-Td3E&ab_channel=DataSlayer)

## Second time failure

After having the image serving website working on my local network at home, I took the pi to a meetup, and trying to set it up.

This failed as the library had a login screen for its wifi and the zero wasn't able to connect to the network automatically as it had at home.
However, the pi was never able to connect to anything any more.  I could see the light coming on, but got nothing but this:

```sh
PS C:\Users\timof> ping raspberrypi
Ping request could not find host raspberrypi. Please check the name and try again.
```

Eventually I re-wrote the sd card and started over, but it was never able to connect on first boot.

I noticed that the ssh, userconf and wpa_supplicant.conf always seemed to be deleted after putting the sd card into the zero, and trying, then taking it out and back into the PC.  Are those files being deleted?  Is the zero broken somehow?

Then I read [here](https://raspberrypi.stackexchange.com/questions/68808/raspberry-pi-zero-w-keeps-deleting-wpa-supplicant-conf-and-ssh-file#:~:text=The%20removal%20of%20the%20ssh,ssh%20available%20on%20subsequent%20boots.): *The removal of the ssh and wpa_supplicant.conf files on boot is normal. Once the RPi boots, everything should be persistent and the network and ssh available on subsequent boots.*

## USB connection

To investigate, I will try a different method to connect to the pi.

[This article](https://www.instructables.com/Connect-to-a-Raspberry-Pi-Zero-W-Via-USB-No-Mini-H/) has an alternate method uses a usb cable.

Open the "config.txt" file with Notepad++
Scroll all the way down to the bottom.
Type "dtoverlay=dwc2" in the last line and then add an extra line after that.
Save and close the file.
Open "cmdline.txt" file with Notepad++
Find a section after "rootwait"
Paste "modules-load=dwc2,g_ether" in said section.
Save and close the file.
Create a new file called "ssh"
Eject the MicroSD Card and place it on your Raspberry Pi

This connection process uses the inner micro USB input.  Also required some print service app named Bonjour, and also Putty.  But trying to connect to pi@raspberrypi.local failed.  I got the message: Unable to open connection to raspberrypi.local.  Host does not exist.

## What else can I try?

When I insert the SD card into the laptop, it says it has a problem and wants to scan and fix it.  At this point, I really disappointed and am ready to purchase another zero this time with the connects to use a keyboard and monitor for the device, and also get soldered headers for expansion projects.

[This article](https://learn.sparkfun.com/tutorials/getting-started-with-the-raspberry-pi-zero-wireless/all) shows using a USB On-the-Go (OTG) connection.

Might also need a micro-b adapter to access the USB port on the Pi Zero for keyboards and mice: *it is recommended that you use a powered USB hub. Wireless keyboard and mouse combos work best as they have one USB dongle for both devices.*

Great, more things to buy.  My equipment all have cables and are un-powered.  I do think I have a wireless mac keyboard somewhere.

I did some more googling, and found [this](https://social.technet.microsoft.com/wiki/contents/articles/861.clearing-name-and-web-caches-host-dns-and-netbios-wins-and-ie-caches.aspx): *When you are having trouble connecting to a network resource, your local computer will often cache the error condition in one or more places. Common troubleshooting steps to resolve cached error conditions include clearing your NetBIOS and host name caches.*

```sh
ipconfig /flushdns
nbtstat –R
```

The second command just shows options.  I don't think it did anything.

Anyhow, now we are back in business!

```sh
> ping raspberrypi

Pinging raspberrypi.modem [192.168.0.49] with 32 bytes of data:
Reply from 192.168.0.164: Destination host unreachable.
Reply from 192.168.0.164: Destination host unreachable.
Reply from 192.168.0.164: Destination host unreachable.
Reply from 192.168.0.164: Destination host unreachable.
Ping statistics for 192.168.0.49:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
```

That's slightly better than the "Ping request could not find host raspberrypi. Please check the name and try again." message.  I remember I would get this first, and then it would start responding after a little while.

Still however, can't ssh into it.

```sh
ssh tim@raspberrypi
ssh: connect to host raspberrypi port 22: Connection timed out
```

So it's not over yet.

I leave it on all night and check in the morning, and viola!

```sh
ping raspberrypi

Pinging raspberrypi.modem [192.168.0.49] with 32 bytes of data:
Reply from 192.168.0.49: bytes=32 time=692ms TTL=64
Reply from 192.168.0.49: bytes=32 time=10ms TTL=64
Reply from 192.168.0.49: bytes=32 time=7ms TTL=64
Reply from 192.168.0.49: bytes=32 time=8ms TTL=64

Ping statistics for 192.168.0.49:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 7ms, Maximum = 692ms, Average = 179ms
```

When I try to log in, it's a strange message:

```sh
 ssh tim@raspberrypi
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ED25519 key sent by the remote host is
SHA256:wf ... 4.
Please contact your system administrator.
Add correct host key in C:\\Users\\timof/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in C:\\Users\\timof/.ssh/known_hosts:22
Host key for raspberrypi has changed and you have requested strict checking.
Host key verification failed.
```

How to add correct host key in user/.ssh/known_hosts to get rid of this message?

ChatGPT: *This error message typically appears when the SSH client detects a change in the host key of the server you’re trying to connect to. This could happen if you’ve reinstalled the operating system on your Raspberry Pi or made some other significant change.*

ChatGPT gave me two methods for resolving this issue.

### Method 1

1. Open the known_hosts file: The file is located at C:\\Users\\timof/.ssh/known_hosts. You can open it with any text editor.
2. Remove the offending key: Look for the line in the file that corresponds to your Raspberry Pi’s IP address or hostname and delete it. Be careful not to change any other lines.

Save and close the file: After deleting the line, save and close the file.

Reconnect to your Raspberry Pi: When you try to connect again, you should be prompted to add the new host key1.

### Method 2

Alternatively, you can use this command in PowerShell to remove the old key and update it in one go:

ssh-keygen -R your.pi.hostname && ssh -o StrictHostKeyChecking=no your.pi.hostname

Replace your.pi.hostname with the hostname or IP address of your Raspberry Pi1. This command will remove the old key for your Raspberry Pi from the known_hosts file and then attempt to connect to your Raspberry Pi, which will add the new host key.

raspberrypi ssh-ed25519 AAA...v9c

Following the first method, the line I removed to fix the issue was something like this:

```txt
raspberrypi ssh-rsa AAAAB3Nz ... ABDyWXVjuTuq+1mM=
```

## Multiple devices

The above solution enabled me to login to my old raspberry pi with it's touch screen

However, now when I try to login to the time-lapse camera zero, I see the above message.

```txt
The fingerprint for the ED25519 key sent by the remote host is
SHA256:wfaGos2CpuZ8ZEXqxTGF/4LcqT6xR9uQCoWCrfuciH4.
Please contact your system administrator.
Add correct host key in C:\\Users\\timof/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in C:\\Users\\timof/.ssh/known_hosts:26
```

### Method 3: Use host aliases

Instead of connecting to the Raspberry Pi using its hostname (raspberrypi in your case), you can create host aliases in your SSH configuration file (~/.ssh/config on Linux/macOS or C:\Users\your_username\.ssh\config on Windows). This allows you to assign a unique alias to each Raspberry Pi device and specify the corresponding hostname, IP address, user, and other connection parameters.

```sh
Host pi1
    Hostname 192.168.45.240
    User tim
```

Then instead of the normal login method, use the alias:

```sh
ssh pi1
```

If when you do this:

```sh
ping raspberrypi
Pinging raspberrypi.local [fe80::70cb:83de:f42b:d8c%11] with 32 bytes of data:
Reply from fe80::70cb:83de:f42b:d8c%11: time=6ms
```

In this case it's a link-local IPv6 address.

You may need to get the IPv4 address by logging in to the pi using the interface and then running this:

```sh
hostname -I
```

## Deleting files

To delete a range of images within a certain date, this could be useful:

```sh
Navigate to the Trash directory: For the current user:
cd ~/.local/share/Trash/files
For the root user:
sudo rm -rf /root/.local/share/Trash/files

Delete all files in the Trash directory:
rm -rf ~/.local/share/Trash/files/*
```

After saving the file, run it like this:

```sh
sudo chmod +x delete_images.sh
./delete_images.sh
```

In the end I actually just connect the zero to my monitor and deleted them with the mouse.  I forgot to empty the waste basket however, so to do this the next login, do this:

Navigate to the Trash directory: For the current user:

```sh
cd ~/.local/share/Trash/files
or
sudo rm -rf /root/.local/share/Trash/files
rm -rf ~/.local/share/Trash/files/*
```
