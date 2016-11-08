var http = require('http');
var express = require('express');
var wpi = require('wiring-pi');
var app = express();

var inputs = [{ pin: '16', gpio: '23', value: null },
              { pin: '22', gpio: '25', value: null }];


// GPIO pin of the led
var configPin = 7;
// Blinking interval in usec
var configTimeout = 1000;

wpi.setup('wpi');
wpi.pinMode(configPin, wpi.OUTPUT);

var isLedOn = 0;

// API call to toggle the light on and off
app.get('/toggle', function (req, res) {
	isLedOn = +!isLedOn;
  console.log('change pin to '+isLedOn);
	wpi.digitalWrite(configPin, isLedOn);
  res.status(300).send('new pin '+isLedOn);
});

app.post('/toggle', function (req, res) {
	isLedOn = +!isLedOn;
  var jsonString = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  req.on('end', function () {
      console.log(JSON.parse(jsonString).name);
  });
  res.status(300).send('thanks');
	//wpi.digitalWrite(configPin, isLedOn);
});

// Old code used to make the light blink continuously
// uncomment for testing purposes
// setInterval(function() {
// 	isLedOn = +!isLedOn;
// 	//isLedOn = !isLedOn;
// 	wpi.digitalWrite(configPin, isLedOn );
// }, configTimeout);

// serve index.html and static pages stored in the home directory,
// along with the client.js file
app.use(express.static(__dirname));

// define the API for routes to the API calls and/or 
// page requests to our server.
// Express route for incoming requests for a single input
app.get('/inputs/:id', function (req, res) {
  var i;
  console.log('received API request for port number ' + req.params.id);
  for (i in inputs){
    if ((req.params.id === inputs[i].gpio)) {
      // send to client an inputs object as a JSON string
      res.send(inputs[i]);
      return;
    }
  } // for
   console.log('invalid input port');
  res.status(403).send('dont recognise that input port number ' + req.params.id);
}); // apt.get()

// Express route for any other unrecognised incoming requests
app.get('*', function(req, res) {
  res.status(404).send('Unrecognised API call');
});

// Express route to handle errors
app.use(function(err, req, res, next) {
  if (req.xhr) {
    res.status(500).send('Oops, Something went wrong!');
  } else {
    next(err);
  }
});

// process.on('SIGINT', function() {
//   var i;
//   console.log("\nGracefully shutting down from SIGINT (Ctrl+C)");
//   console.log("closing GPIO...");
//   for (i in inputs) {
//     gpio.close(inputs[i].pin);
//   }
//   process.exit();
// });

app.listen(3000);
console.log('App Server running at port 3000');