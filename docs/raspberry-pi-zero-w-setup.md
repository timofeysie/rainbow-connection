# How to setup a Raspberry Pi Zero W

[This article](https://www.techcoil.com/blog/how-to-host-a-static-website-on-your-raspberry-pi-zero-w-with-raspbian-stretch-lite-and-nginx-web-server/) links to other detail offshoot articles that drill down into the steps.

I will also add the steps to setup the nginx server and creation of a static website to host the images taken by the camera.

Notes for how to use the nano editor are also included.

## Setup a new SD card

- use Pi Imager to flash the OS.  Details [here](https://www.techcoil.com/blog/how-to-prepare-the-operating-system-to-run-your-raspberry-pi-with-your-windows-machine/)

- create an empty file named as "ssh" and copy it to the root directory of the SD card

- wpa_supplicant.conf file that contains your WiFi network configuration

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

The address: 192.168.0.49

Configure dns

sudo nano /etc/nginx/sites-enabled/yourdomain.com.conf

```sh
server {
        server_name yourdomain.com www.yourdomain.com;
        listen 80;
        root /var/www/yourdomain.com;
        index index.html;
}
```

Ctrl-X followed by Y to save the configuration file.

```sh
sudo systemctl restart nginx.service
```

I have a raspberry pi zero W and I want to create a static site to serve all the images in a directory on the device.
I have nginx running already.  I can configure a domain in a file like this:
/etc/nginx/sites-enabled/yourdomain.com.conf
server {
        server_name yourdomain.com www.yourdomain.com;
        listen 80;
        root /var/www/yourdomain.com;
        index index.html;
}
Can you please show me the code for an index page that will include all the images in a directory  /var/www/yourdomain.com/images

sudo mkdir /var/www/timelapse.local
sudo nano /var/www/timelapse.local/index.html

server {
    listen 80;
    server_name timelapse.local;
    root /var/www/timelapse.local;
    index index.html;
}

sudo mkdir -p /var/www/timelapse.local/images
sudo chmod 755 /var/www/timelapse.local/images

libcamera-jpeg -o /var/www/timelapse.local/images/test-1.jpg

sudo libcamera-jpeg -o /var/www/timelapse.local/images/image-1.jpg

I actually couldn't get it to configure my own site, so I ended up using the default site created by nginx.  That is in this location: /var/www/html/index.html

sudo nano /etc/nginx/sites-available/default

http://192.168.0.49/

http://192.168.0.49/images/image-1.jpg

http://192.168.0.49/images/test-2.jpg

## The website code

I like to separate code by type, so will have separate javascript, css and html files.

script.js

sudo nano /var/www/html/script.js

```js
// JavaScript to list and display images in the gallery
document.addEventListener("DOMContentLoaded", function() {
    const imageList = document.getElementById("image-list");

    fetch("/images/") // Use the correct path to your images directory
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, "text/html");
            const links = doc.querySelectorAll("a");

            links.forEach(link => {
                const href = link.getAttribute("href");
                if (href.endsWith(".jpg") || href.endsWith(".jpeg")) {
                    const listItem = document.createElement("li");
                    const imageLink = document.createElement("a"); // Create an anchor element
                    imageLink.href = `/images/${href}`; // Set the href attribute to the image path

                    // Create the thumbnail image element
                    const imageElement = document.createElement("img");
                    imageElement.src = `/images/${href}`;
                    imageElement.alt = href;

                    // Set max width and max height for the thumbnail image
                    imageElement.style.maxWidth = "200px";
                    imageElement.style.maxHeight = "200px";

                    imageLink.appendChild(imageElement); // Append the image to the anchor element
                    listItem.appendChild(imageLink); // Append the anchor element to the list item
                    listItem.appendChild(document.createElement("br")); // Add a line break
                    listItem.appendChild(document.createTextNode(href)); // Add the filename as text
                    imageList.appendChild(listItem);
                }
            });
        })
        .catch(error => console.error("Error fetching images:", error));
});
```

### The css file

sudo nano /var/www/html/style.css

```css
/* Add your CSS styles here */
ul {
    list-style-type: none;
    padding: 0;
}

li {
    display: inline-block;
    margin: 10px;
    text-align: center;
}

img {
    max-width: 200px;
    max-height: 200px;
}
```


### The index.html file

nano /var/www/html/index.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Gallery</title>
    <link rel="stylesheet" type="text/css" href="/path/to/style.css">
</head>
<body>
    <h1>Image Gallery</h1>
    <ul id="image-list">
        <!-- Images will be listed here -->
    </ul>
    <button id="capture-button">Capture</button>
    <script src="/path/to/script.js"></script>
    <script src="/capture.js"></script>
</body>
</html>
```

### Capture button

```sh
sudo apt-get update
sudo apt-get install raspistill
```

nano /var/www/html/capture.js

```js
const { exec } = require("child_process");

// Function to capture an image with a timestamp-based filename
function captureImage() {
    const timestamp = new Date().toISOString().replace(/[-:.]/g, "");
    const fileName = `/var/www/html/images/image_${timestamp}.jpg`; // Modify the path as needed

    const captureCommand = `raspistill -o ${fileName}`;

    exec(captureCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error capturing image: ${error.message}`);
            return;
        }
        console.log(`Image captured: ${fileName}`);
    });
}

// Capture button click event handler
document.addEventListener("DOMContentLoaded", function() {
    const captureButton = document.getElementById("capture-button");

    captureButton.addEventListener("click", function() {
        // Call the captureImage function when the button is clicked
        captureImage();
    });
});

```

## Commands

ping raspberrypi
Pinging raspberrypi.modem [192.168.0.49] with 32 bytes of data:
Reply from 192.168.0.49: bytes=32 time=14ms TTL=64

ssh tim@raspberrypi

enter a password

### The site

sudo nano /var/www/html/index.nginx-debian.html

sudo nano /var/www/html/images.json

### Restart nginx

sudo systemctl restart nginx.service

### Check syntax

sudo nginx -t
sudo tail -f /var/log/nginx/error.log
sudo service nginx reload

## Nano commands

Ctrl + Shift + 6 to start selecting and  
Ctrl + K to cut), press  
Ctrl + U to paste the cut text. This will paste the previously cut text back into the file. 
Shift + Insert keyboard shortcut in nano. This should paste the text you copied from your To save the changes, press  
Ctrl + O then press Enter
Ctrl + X to exit nano

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
