var http = require('http');
var express = require('express');
var xAPIWrapper = require('./node_modules/xAPIWrapper/src/xapiwrapper');
var xAPIStatement = require('./node_modules/xAPIWrapper/src/xapistatement');
var verbs = require('./node_modules/xAPIWrapper/src/verbs');
var xAPILaunch = require('./node_modules/xAPIWrapper/src/xapi-launch');
var xapiutil = require('./node_modules/xAPIWrapper/src/xapi-util');
var app = express();

//console.log('xAPIWrapper', xAPIWrapper);

app.post('/game/question', function (req, res) {
  var jsonString = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  try {
    req.on('end', function () {
      console.log('add question: jsonString',jsonString);
    });
  } catch (error) {
    console.log('error',error);
  }
  res.status(200).send('{"result": "thanks"}');
});

var isLedOn = 0;

// API call to toggle the light on and off
app.get('/toggle', function (req, res) {
	isLedOn = +!isLedOn;
  console.log('toggle: change pin to '+isLedOn);
  res.status(200).send('new pin '+isLedOn);
	//wpi.digitalWrite(configPin, isLedOn);
});

// Toggle 2 example
var configPin_18_isLedOn = 0;
app.get('/toggle2', function (req, res) {
	configPin_18_isLedOn = +!configPin_18_isLedOn;
  console.log('toggle2: change pin to '+configPin_18_isLedOn);
  res.status(200).send('new pin '+configPin_18_isLedOn);
	//wpi.digitalWrite(configPin, isLedOn);
});

app.post('/toggle', function (req, res) {
	isLedOn = +!isLedOn;
  var jsonString = '';
  var result = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  try {
  req.on('end', function () {
    result = JSON.parse(jsonString).name;
      console.log(result);
  });
  } catch (error) {
    console.log('jsonString',jsonString);
  }
  res.status(200).send('thanks, '+JSON.parse(jsonString).name);
	//wpi.digitalWrite(configPin, isLedOn);
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

/* xAPI test endpoint */
app.post('/xapi', function (req, res) {
  var jsonString = '';
  var result = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  try {
  req.on('end', function () {
    result = JSON.parse(jsonString).name;
      console.log(result);
  });
  } catch (error) {
    console.log('jsonString',jsonString);
  }
  res.status(200).send('thanks, '+JSON.parse(jsonString).name);
});