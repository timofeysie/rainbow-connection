var http = require('http');
var express = require('express');
var app = express();


// API call to toggle the light on and off
app.get('/toggle', function (req, res) {
	isLedOn = +!isLedOn;
  console.log('change pin to '+isLedOn);
	wpi.digitalWrite(configPin, isLedOn);
});

// serve index.html and static pages stored in the home directory,
// along with the client.js file
app.use(express.static(__dirname));

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

app.listen(3000);
console.log('App Server running at port 3000');