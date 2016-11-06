# Raspberry Pi Node API


The initial example using NodeJS to make the LED blink [can be found here](http://www.instructables.com/id/JavaScript-for-IoT-Blinking-LED-on-Raspberry-Pi-Wi/?ALLSTEPS)
The initial example for using a RESTful API to expose the pins to the internet [can be found here](http://www.robert-drummond.com/2013/05/08/how-to-build-a-restful-web-api-on-a-raspberry-pi-in-javascript-2/) 
The second example used Pi GPIO, and old library which no longer works with current Pi's, 
so the actual GPIO config will be done with WiringPi

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

To test the app on a non-Rapsberry Pi machine, run:
```
$ node dev-server.js
```

You can then point your browser at http://localhost:3000/


To build the project, run:
```
$ npm run build
```

To run the Karma tests, run:
```
$ npm test
```

To run the app using the regular Angular method, try this:
```
$ npm start
```

Then, the app will be availble at:
```
http://localhost:8080/
```

## Using Webpack with Angular 2

To create a webpage to control the lights we are going to extremes. 
To make it interesting, we will be using the code from [the officual Angular 2 Webpack tutorial](https://angular.io/docs/ts/latest/guide/webpack.html).

Since we need more experience with Webpack, this will be like killing two birds with one project (no actual birds will be harmed).

This line was removed from the scripts section of the package.json file:
```
"start": "webpack-dev-server --inline --progress --port 8080", // Webpack start script
```
We run our server.js instead.  Might need to change that later.

> rimraf dist && webpack --config config/webpack.prod.js --progress --profile --bail

The following command:
```
$ npm run build
```
fails with the following error:
```
  0% compileEntryModuleNotFoundError: Entry module not found: Error: Cannot resolve 'file' or 'directory' ./src/polyfills.ts in /Users/tim/pi/rainbow-connection
    at Compilation.<anonymous> (/Users/tim/pi/rainbow-connection/node_modules/webpack/lib/Compilation.js:358:28)
```

We took out our sever start script and re-instated the one above.
We will have to think of a better way of dealing with this Mac/Raspberry pi build differences.
```
    "start": "node server.js"
```



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

Also, if you build using npm install and you are not on the Raspberry Pi, 
you must remove this from the package.json file:
```
"wiring-pi": ">=2.1.1",
```
This will faile and break the install procress.
Not sure how to handle this yet.  Stay tuned.



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


