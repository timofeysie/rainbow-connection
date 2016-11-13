# Raspberry Pi Node API

Simple project to make an LED toggle on and off via a web page.

Added the [xAPI wrapper](https://github.com/adlnet/xAPIWrapper) library for 
communication of the [learning objects](https://en.wikipedia.org/wiki/Learning_object) 
between the server and the client.

Currently implementing button input to emulate RFID tag contact.

## Toggle

Using the [example here](http://www.instructables.com/id/JavaScript-for-IoT-Blinking-LED-on-Raspberry-Pi-Wi/?ALLSTEPS) 
by Leon-anavi's instructable, we use pin 7 in the J8 Pin numbering scheme.

This requires pin 6 (0v ground) and the above mentioned pin 7 (GPIO4) to create a circute with an LED.

The api to use is <pi-IP-addr>/toggle

## Toggle 2

Using the example from the Adventures in Rapberry Pi book by Carrie Anne Philpin.
Her example uses the GPI pin numbering.
GPIO Pin 24 (J8 Pin 18), as well as the same ground pin as togle 1.

In the diagram, the ground pin goes to the negative (blue) row on the breadboard.
The GPIO Pin 24 goes straight to the board at the same end of the LED longer leg 
(ie: the lower end of the circuit).

Since we are using the J8 Pin numbering, in the server.js file, it is set as pin 18.
The number scheme is set like this:
```
wpi.setup('wpi');
```


## Physical pin numbering

In pin charts for the Rapsberry Pi, there are often two numbering systems shown.
The GPIO/Function numbering, and the J8 Pin numbering.
The J8 Pine count goes across and down from pin 1 at the top left of header P1 
(nearest to the SD card).
Example: GPIO port 23 is found on P1 header pin 16.


## Set up

The initial example using NodeJS to make the LED blink [can be found here](http://www.instructables.com/id/JavaScript-for-IoT-Blinking-LED-on-Raspberry-Pi-Wi/?ALLSTEPS)
The initial example for using a RESTful API to expose the pins to the internet [can be found here](http://www.robert-drummond.com/2013/05/08/how-to-build-a-restful-web-api-on-a-raspberry-pi-in-javascript-2/) 
The first example used Pi GPIO, and old library which no longer works with current Pi's, 
so the actual GPIO config will be done with WiringPi

The app depends on NodeJS, and other Node libraries.
The first time you run this app, you will need to install the libs.
In the project directory, run the following command in a terminal:
```
$ npm install
```

Run the application using the following command again from the project directory:
```
$ sudo node server.js
```

You can then point your browser at http://localhost:3000/

There is a dev-server.js file which removes the wiring-pi stuff for testing on a non-raspi machine.
Run this command to test:
```
$ node dev-server.js
```

The best thing to do duing development is run the server first, then run:
```
$ npm start
```
This will start the Angular style dev mode with file watch on post 3001 (since the dev-server will be using 3000).
Then, make sure you are looking at port 3000 in the browser.
This way you will have live compile, and the working API at the same time.

To build the Angular 2 app, we must removed the following from package.json:
```
"dependencies": {
    ...
    "wiring-pi": ">=2.1.1"

This lib can only be set up on the Raspberry pi.
So to work on a non raspi device, we have to remeber this lib.

## Npm unable to find angular

That's right, running npm i on the Raspberry Pi failed saying it could not find the registry.
Specifying the registry did not help the situation.  
After a while, I simply got rid of the git ignore for the node-modules and commeted them.
This took a while.  Then the git pull took even longer.
Then however, we were able to run Angular 2 on the device!

The button on the website works to toggle the light.
The input sends data to the pi.

We're in business.

Next up, 
multiple lights, using input (ie. a button) and a RESTful service using the xAPI telling the pi which light to turn on when the button is pressed.


## Using the Angular 2 Quickstart

As a simpler approach, we are using the official quick start seed.

The http calls are coming from [this module](https://angular.io/docs/ts/latest/guide/server-communication.html) for now.

There are a lot of questions that need to be asnwered regarding using Angular as a front end for the raspi, so the quickest way to a working demo is in right now.

Currently, some of the calls are getting thru, but there is some delay, and we are getting this error:
```
zone.js:1382 POST http://localhost:3000/toggle 404 (Not Found)
```

Also, we need to run ```$ npm start``` to develop the client, then stop that and run ```$node dev-server.js``` to test the app. 
This is not ideal.

See above for how to handle dev mode.

## Using Webpack with Angular 2

To create a webpage to control the lights we are going to extremes. 
To make it interesting, we will be using the code from [the officual Angular 2 Webpack tutorial](https://angular.io/docs/ts/latest/guide/webpack.html).

Since we need more experience with Webpack, this will be like killing two birds with one project (no actual birds will be harmed).

Maybe it was a bit ambitious.  Building the project this way created all kinds of issues, and the observable http calls were not working for some reason.
So this experiment lives in a separate branch.
It is certainly the way to go, and nice not to have the js files in the project, but to get on with this app, we will try a simpler Anulgar 2 approach.

## Wiring-pi

Trying to install wiring-pi on the mac resulted in the following error:
```
FATAL: Making libWiringPi failed.
Please check install.log and fix any problems. If you're still stuck,
```

On the pi, npm i comnpletes.  This is becuase wiring-pi is meant to be installed on a rapsberry pi.

To test the API calls on the Mac before tyring it out on the pi we have a demo server app.
This is called dev-server.js 
It is the same as the server.js but without wiring-pi.



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


zone.js:388 Unhandled Promise rejection: Failed to load app.component.html