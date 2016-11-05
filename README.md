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
opening GPIO port 23 on pin 16 as input
/home/pi/rainbo-connection/server.js:19
gpio.op(inputs[i].pin, "input", function (err) {
    ReferenceError: gpio is not defined
})



## External Access
Allowing inbound requests can expose your LAN to external attack, 
so its safer to use a service like weaved.com. 
You’ll need to sign up for an account, and install the weaved 
package on your RPi. Follow the instructions on their RPi page 
[here](https://developer.weaved.com/portal/members/betapi.php).


