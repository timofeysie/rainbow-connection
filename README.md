# Raspberry Pi Node API

Using [this tutorial](http://www.robert-drummond.com/2013/05/08/how-to-build-a-restful-web-api-on-a-raspberry-pi-in-javascript-2/) 
as the starting point for a client server app for Raspberry Pi interaction.

The app depends on NodeJS, and other Node libraries.
The first time you run this app, you will need to install the libs.
In the project directory, run the following command in a terminal:
```
$ npm install
```

Run the application using the following command again from the project directory:
```
$ node server.js
```

You can then point your browser at http://localhost:3000/


## Wiring-pi

Trying to install wiring-pi on the mac resulted in the following error:
```
FATAL: Making libWiringPi failed.
Please check install.log and fix any problems. If you're still stuck,
```

This may be the fact that it is meant to be installed on a rapsberry pi.

But still, we would like to test the API calls on the Mac before tyring it out on the pi.
So we will create a dev-server without wiring-pi just for testing purposes.


## Pi GPO package

On the mac, this line in the server.js file:
```
var wpi = require('pi-gpio');
```

causes the following error when running 'node server.js':
```
Error: ENOENT: no such file or directory, open '/proc/cpuinfo'
```

On ths pi, this works fine, but there is another error:
```
Error when trying to open pin 22
/bin/sh 1: gpio-admin: not found
/home/pi/rainbow-connection/server.js:21
Error: Command failed: /bin/sh: 1: gpio-admin: not found
```

After searching a bit, I [followed these instructions](https://www.npmjs.com/package/pi-gpio#installation) 
by building pi-gpio by hand.  Now, I am getting the following error:
```
Error when trying to open pin 22
gpio-admin: failed to change group permissions of /sys/devices/virtual/gpio25/direction: 
No such file or directory

The [very next search result](https://github.com/mirceageorgescu/raspi-tank-2/issues/1) 
shows another user having the same problem after making pi-gpio.

That answer points to [this answer](http://raspberrypi.stackexchange.com/questions/27953/how-to-change-gpio-directory-for-node-js-pi-gpio)
Here there three solutions:

### Solution 1

chmod -R +x /sys/devices/soc/20200000.gpio

### Solution 2

Update the pi-gpio.js so that

sysFsPath = "/sys/devices/virtual/gpio";
points to the new path:

sysFsPath = "/sys/class/gpio";

### Solution 3

Add line device_tree= in /boot/config.txt. 
That will revert the links to be in the old path. 
Make sure you reboot after changing the config.txt.

Since pi-gpio is an old package, infact the tutorial is from 2013, 
and the repo aparently hasn't been maintained for two years, 
the solution that changes pi-gpio, not the system would be prudent.

But even after changing that path, things are not working. 
So will switch to wiring-pi.
We will also create an Angular 2 app to replace the jQuery page which exposed the pins 
in the original example.  Should have just started with wiring-pi and Angular from the start.
Anyhow, live and learn.


## External Access
Allowing inbound requests can expose your LAN to external attack, 
so its safer to use a service like weaved.com. 
You’ll need to sign up for an account, and install the weaved 
package on your RPi. Follow the instructions on their RPi page 
[here](https://developer.weaved.com/portal/members/betapi.php).


