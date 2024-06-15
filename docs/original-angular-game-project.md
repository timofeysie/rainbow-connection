# Original Angular Game documentation

This file is from the original README begun November 5th, 2016 5:32 AM.

## Raspberry Pi Node API

Simple project to make an LED toggle on and off via a web page.

Added the [xAPI wrapper](https://github.com/adlnet/xAPIWrapper) library for communication of the [learning objects](https://en.wikipedia.org/wiki/Learning_object) between the server and the client.

The event emmitter class was added to facilitate communication from different components in the app.
When a new question is added, we emit the new list so that the question-list.component can update it'self.
However, currently there is a problem with the question-list.component.
Adding it to the declarations array in the app.module.ts file cases this error:

```err
zone.js:1382 GET http://localhost:3000/question-list.component 404 (Not Found)scheduleTask @ zone.js:1382ZoneDelegate.scheduleTask @ zone.js:245Zone.scheduleMacroTask @ zone.js:171(anonymous function) @ zone.js:1405send @ VM33908:3ResourceLoaderImpl.get @ platform-browser-dynamic.umd.js:55DirectiveNormalizer._fetch @ compiler.umd.js:13661DirectiveNormalizer.normalizeTemplateAsync @ compiler.umd.js:13704DirectiveNormalizer.normalizeDirective @ compiler.umd.js:13679RuntimeCompiler._createCompiledTemplate @ compiler.umd.js:17142(anonymous function) @ compiler.umd.js:17070(anonymous function) @ compiler.umd.js:17066RuntimeCompiler._compileComponents @ compiler.umd.js:17065RuntimeCompiler._compileModuleAndComponents @ compiler.umd.js:17001RuntimeCompiler.compileModuleAsync @ compiler.umd.js:16992PlatformRef_._bootstrapModuleWithZone @ core.umd.js:6684PlatformRef_.bootstrapModule @ core.umd.js:6666(anonymous function) @ main.ts:5(anonymous function) @ main.ts:5(anonymous function) @ main.ts:5__exec @ system.src.js:1555entry.execute @ system.src.js:4035linkDynamicModule @ system.src.js:3300link @ system.src.js:3135execute @ system.src.js:3510doDynamicExecute @ system.src.js:766link @ system.src.js:964doLink @ system.src.js:623updateLinkSetOnLoad @ system.src.js:669(anonymous function) @ system.src.js:485ZoneDelegate.invoke @ zone.js:232Zone.run @ zone.js:114(anonymous function) @ zone.js:502ZoneDelegate.invokeTask @ zone.js:265Zone.runTask @ zone.js:154drainMicroTaskQueue @ zone.js:401ZoneTask.invoke @ zone.js:339
zone.js:388 Unhandled Promise rejection: Failed to load question-list.component ; Zone: <root> ; Task: Promise.then ; Value: Failed to load question-list.component undefinedconsoleError @ zone.js:388_loop_1 @ zone.js:417drainMicroTaskQueue @ zone.js:421ZoneTask.invoke @ zone.js:339
zone.js:390 Error: Uncaught (in promise): Failed to load question-list.component(…)
```

Everything seems wired up correctly.  There appears to be no typo in the config.
We are able to import it into the app.module.  Not sure what's wrong.

Will look in to it next time.

## xAPI in Angular 2

Using the same paths to the libs that we used in xAPI in NodeJS, like this:

```js
import { xAPIWrapper } from '../node_modules/xAPIWrapper/src/xapiwrapper';
```

We get the following hint over the red squigglies that appear under the paths in [VSCode](https://code.visualstudio.com):

```js
[ts] Cannot find module '../node_modules/xAPIWrapper/src/xapiwrapper'.
```

Since we are using the [npm branch of the xAPI Wrapper](https://github.com/adlnet/xAPIWrapper/issues/67) 
by Zac Petterd means is should be a commonjs compatible bundle, no?

Someone suggested using pure JavaScript to include the lib, so we tried this:

```js
var xAPIWrapper = require('../node_modules/xAPIWrapper/src/xapiwrapper');
```

The red squiggly is then gone, but it's not time to party. 
When running the app via npm start, we get a broken app with this in the console:

```js
http://localhost:3000/node_modules/xAPIWrapper/src/xapiwrapper 
Failed to load resource: the server responded with a status of 404 (Not Found)
```

Trying this:

```js
var xAPIWrapper = require('../../node_modules/xAPIWrapper/src/xapiwrapper');
```

Changes the error slightly:

```js
zone.js:1382 
GET http://localhost:3000/node_modules/xAPIWrapper/src/xapiwrapper 404 (Not Found)
```

And indeed if we look in the sources tab of the Chrome inspector, we see only a small list of libs in the node_modules directory.
Such as @angular, core-js/client, reflect-metadata, systemjs/dist, zone.js/dist.

Well, since we are not using Webpack (remember, we tried that in the webpack branch) 
because this app will be served from a Raspberry Pi, so should be as lightweight as possible, 
what do we need to do to insure that our required libs get packaged and sent off to the client?

Trying this in the system.config.js file does not work:
 'xAPIWrapper': './node_modules/xAPIWrapper/src/xapiwrapper',

So what's next?  We could include it by hand in a vendor directory.
But that's not managable as a npm module.  Maybe it doesn't matter,
as this is not an official distribution anyhow.
We could link them by hand in the index.html file.

If we put the files in the index.html file like this:

```html
<script src="node_modules/xAPIWrapper/src/xapiwrapper.js"></script>
```

Then we get errors like this in the console:

```err
xapiwrapper.js:3 Uncaught ReferenceError: require is not defined(…)
...
zone.js:1382 GET http://localhost:3000/node_modules/xAPIWrapper/src/xapiwrapper 404 (Not Found)
...
(index):25 Error: (SystemJS) XHR error (404 Not Found) loading http://localhost:3000/node_modules/xAPIWrapper/src/xapiwrapper(…)
```

And this is repeated for most of these libs: 
xapiwrapper, xapistatement, verbs, xapi-launch, and xapi-util

There are six in the sources folder under the xAPIWrapper/src directory, including the index.js file.

Looking at other people who experienced the require is not defined error, someone said this:
module set as "commonjs" in my tsconfig.json file, changing it to system fixed it

Making that suggested change shows less errors in the console, 
but the one we tried to fix is still there, as well as this:

```err
(index):25 Error: (SystemJS) require is not a function(…)
```

I just noticed that we still have this in the index file and the deployed sources:

```html
<script src="vendor/xapiwrapper.min.js"></script>  
```

So really we should have ignored all those attempts before to load the files from the node modules.
If we try and use the vendor/xapiwrapper.min.js, which should have all we need except for crypto.

Trying just to use this import, we get two errors:

```err
zone.js:1382 
GET http://localhost:3000/vendor/xapiwrapper 
404 (Not Found)scheduleTask 
 @ zone.js:1382ZoneDelegate.scheduleTask 
 ...
 @ system.src.js:1051(anonymous function) 
 @ system.src.js:1778ZoneAwarePromise 
 @ zone.js:518(anonymous function) 
 @ system.src.js:1777(anonymous function) 
 ...
 @ zone.js:232Zone.run 
 ...
(index):17 Error: (SystemJS) XHR error (404 Not Found) 
loading http://localhost:3000/vendor/xapiwrapper(…)
```

However, if you look in the sources tab of the Chrome inspector, 
localhost:3000/vendor/xapiwrapper is exactly where that file is.

Then I read [this SO answer](http://stackoverflow.com/questions/37179236/angular2-error-at-startup-of-the-app-http-localhost3000-traceur-404-not-fo):

```txt
At the beginning of app.component.ts I had commented an earlier version of the silly AppComponent, something like
/*
import { AnotherComponent } from './anotherComponent.component'
// some other code
}*/
import { Component } from '@angular/core';
...
Removing the comment at the beginning of the file has solved the problem.
```

So out of frustration I tried this in the app.components.ts:

```js
import { xAPIWrapper } from '../../vendor/xapiwrapper';
```

As usual, there was a long red squiggly under the path to the xapiwrapper.
Hovering over the red squiggly showed this hint:

```js
[ts] Cannot find module '../../vendor/xapiwrapper'.
```

Normally I would keep trying something until the squiggly went away.
However, just curious, I wanted to see what the error would be now.
Refreshed the app, and guess what?  It ran without error.

Now let's see if we can actually use this lib!

The bad news is that we still can't.

```js
import { ADL } from '../../vendor/xapiwrapper';
...

export class AppComponent {
    adl: ADL;
    constructor(private adl: ADL) {
        var conf = this.getConfig();
        this.adl.XAPIWrapper.changeConfig(conf);
    }
```

This will give us the same errors as above:

```err
zone.js:1382 
GET http://localhost:3000/vendor/xapiwrapper 404 (Not Found)
(index):17 Error: (SystemJS) XHR error (404 Not Found) loading http://localhost:3000/vendor/xapiwrapper(…)
```

So, any ideas?  Go back to Angular 1 just to use xAPI?
Create an issue on the ADL GitHub?
Keep trying to figure out how to fix those errors instead of getting anything done?

Only time will tell.

## xAPI in NodeJS

Trying to inlcude the xAPI lib in this project fails with this error in the browser:

```err
(index):17 Error: (SystemJS) Can't resolve all parameters for XapiComponent: (?).
(…)(anonymous function) @ 
(index):17ZoneDelegate.invoke @ 
zone.js:232Zone.run @ 
...
```

Using the experimental [npm build](https://github.com/zapur1/xAPIWrapper.git)
Installed like this:

```sh
$ npm install https://github.com/zapur1/xAPIWrapper.git
api-pi@1.0.0 /Users/tim/pi/rainbow-connection
└── xAPIWrapper@1.11.0  (git+https://github.com/zapur1/xAPIWrapper.git#ac2f0dd2aabf03c35507c03e161eb3e473506981)
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/bower/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/console-control-strings/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/execSync/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/gauge/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/in-publish/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/node-gyp/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/node-gyp/node_modules/npmlog/package.json'
npm WARN enoent ENOENT: no such file or directory, open '/Users/tim/pi/rainbow-connection/node_modules/karma/node_modules/base64-arraybuffer/package.json'
npm WARN api-pi@1.0.0 No repository field.
$ node -v
v4.4.3
$ npm -v
3.10.7
```

So did this to make sure xAPI would be happy in its new home:

```sh
npm i bower, console-control-strings, execSync, gauge, in-publish, node-gyp, karma
```

It also requires cryptojs_v3.1.2.js
I tried this: ```$ npm install cryptojs```

But I kept getting the error:

```err
Error: Cannot find module 'crypto-js'
    at Function.Module._resolveFilename (module.js:325:15)
    at Function.Module._load (module.js:276:25)
    at Module.require (module.js:353:17)
    at require (internal/module.js:12:17)
    at Object.<anonymous> (/Users/tim/pi/rainbow-connection/node_modules/xAPIWrapper/src/xapiwrapper.js:3:16)
```

So I tried this instead:

```sh
npm install cryptojs
```

And then using the require statements:

```js
var xAPIWrapper = require('./node_modules/xAPIWrapper/src/xapiwrapper');
var xAPIStatement = require('./node_modules/xAPIWrapper/src/xapistatement');
var verbs = require('./node_modules/xAPIWrapper/src/verbs');
var xAPILaunch = require('./node_modules/xAPIWrapper/src/xapi-launch');
var xapiutil = require('./node_modules/xAPIWrapper/src/xapi-util');
```

Now we can use the xAPIWrapper in the node server.
Next, and the more difficult part, is doing the same thing but for the Angular 2 app.
Since it is written in TypeScript, we will be using import statements, not SystemJS require statements 
to wire up the dependencies.
There were problems with the same thing in [another project of ours](https://github.com/timofeysie/tyno-lrs).
But that was Node with TypeScript.  This will be Anuglar 2 with TypeScipt.

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

```py
wpi.setup('wpi');
```

## Physical pin numbering

In pin charts for the Rapsberry Pi, there are often two numbering systems shown.
The GPIO/Function numbering, and the J8 Pin numbering.
The J8 Pine count goes across and down from pin 1 at the top left of header P1 
(nearest to the SD card).
Example: GPIO port 23 is found on P1 header pin 16.

## Angular CLI errors

On a vanilla project started with the CLI on this system, everything works.
But introducing the CLI generated code here does not work.

```sh
ng version/generate or any other cli command give this error:
```

Trying to run this CLI command gives the following error:

```err
Cannot find module 'package.json'
Error: Cannot find module 'package.json'
    at Function.Module._resolveFilename (module.js:325:15)
    at Function.Module._load (module.js:276:25)
    at Module.require (module.js:353:17)
    at require (internal/module.js:12:17)
    at AddonDiscovery.discoverAtPath (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/addon-discovery.js:205:20)
    at AddonDiscovery.<anonymous> (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/addon-discovery.js:114:26)
    at Array.map (native)
    at AddonDiscovery.discoverFromDependencies (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/addon-discovery.js:109:68)
    at AddonDiscovery.discoverProjectAddons (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/addon-discovery.js:48:29)
    at Project.discoverAddons (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/project.js:353:40)
    at Project.initializeAddons (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/project.js:372:8)
    at Project.eachAddonCommand (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/models/project.js:425:10)
    at module.exports (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/cli/lookup-command.js:33:13)
    at CLI.<anonymous> (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/angular-cli/lib/cli/cli.js:34:26)
    at tryCatch (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/rsvp/dist/rsvp.js:538:12)
    at invokeCallback (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/rsvp/dist/rsvp.js:553:13)
    at publish (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/rsvp/dist/rsvp.js:521:7)
    at flush (/Users/tim/.nvm/versions/node/v4.4.3/lib/node_modules/angular-cli/node_modules/rsvp/dist/rsvp.js:2373:5)
    at nextTickCallbackWith0Args (node.js:420:9)
    at process._tickCallback (node.js:349:13)
```

## Git Stash Problem

QuinquenniumF:rainbow-connection tim$ git stash
Saved working directory and index state WIP on xapi: e37855e Fixed a typo
fatal: Unable to create '/Users/tim/pi/rainbow-connection/.git/index.lock': File exists.

If no other git process is currently running, this probably means a
git process crashed in this repository earlier. Make sure no other git
process is running and remove the file manually to continue.

## Set up

The initial example using NodeJS to make the LED blink [can be found here](http://www.instructables.com/id/JavaScript-for-IoT-Blinking-LED-on-Raspberry-Pi-Wi/?ALLSTEPS)
The initial example for using a RESTful API to expose the pins to the internet [can be found here](http://www.robert-drummond.com/2013/05/08/how-to-build-a-restful-web-api-on-a-raspberry-pi-in-javascript-2/) 
The first example used Pi GPIO, and old library which no longer works with current Pi's, 
so the actual GPIO config will be done with WiringPi

The app depends on NodeJS, and other Node libraries.
The first time you run this app, you will need to install the libs.
In the project directory, run the following command in a terminal:

```sh
npm install
```

Run the application using the following command again from the project directory:

```sh
sudo node server.js
```

You can then point your browser at http://localhost:3000/

There is a dev-server.js file which removes the wiring-pi stuff for testing on a non-raspi machine.
Run this command to test:

```sh
node dev-server.js
```

The best thing to do duing development is run the server first, then run:

```sh
npm start
```

This will start the Angular style dev mode with file watch on post 3001 (since the dev-server will be using 3000).
Then, make sure you are looking at port 3000 in the browser.
This way you will have live compile, and the working API at the same time.

To build the Angular 2 app, we must removed the following from package.json:

```json
"dependencies": {
    ...
    "wiring-pi": ">=2.1.1"
```

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

Next up, multiple lights, using input (ie. a button) and a RESTful service using the xAPI telling the pi which light to turn on when the button is pressed.

## Using the Angular 2 Quickstart

As a simpler approach, we are using the official quick start seed.

The http calls are coming from [this module](https://angular.io/docs/ts/latest/guide/server-communication.html) for now.

There are a lot of questions that need to be asnwered regarding using Angular as a front end for the raspi, so the quickest way to a working demo is in right now.

Currently, some of the calls are getting thru, but there is some delay, and we are getting this error:

```err
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

```err
FATAL: Making libWiringPi failed.
Please check install.log and fix any problems. If you're still stuck,
```

On the pi, npm i comnpletes.  This is becuase wiring-pi is meant to be installed on a rapsberry pi.

To test the API calls on the Mac before tyring it out on the pi we have a demo server app.
This is called dev-server.js 
It is the same as the server.js but without wiring-pi.

## Pi GPO package

On the mac, this line in the server.js file:

```py
var wpi = require('pi-gpio');
```

causes the following error when running 'node server.js':

```py
Error: ENOENT: no such file or directory, open '/proc/cpuinfo'
```

On ths pi, this works fine, but there is another error:

```err
Error when trying to open pin 22
/bin/sh 1: gpio-admin: not found
/home/pi/rainbow-connection/server.js:21
Error: Command failed: /bin/sh: 1: gpio-admin: not found
```

After searching a bit, I [followed these instructions](https://www.npmjs.com/package/pi-gpio#installation) 
by building pi-gpio by hand.  Now, I am getting the following error:

```err
Error when trying to open pin 22
gpio-admin: failed to change group permissions of /sys/devices/virtual/gpio25/direction: 
No such file or directory
```

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

```err
zone.js:388 Unhandled Promise rejection: Failed to load app.component.html
```
