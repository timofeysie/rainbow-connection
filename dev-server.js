var http = require('http');
var fs = require('fs');
var express = require('express');
var xAPIWrapper = require('./node_modules/xAPIWrapper/src/xapiwrapper');
var xAPIStatement = require('./node_modules/xAPIWrapper/src/xapistatement');
var verbs = require('./node_modules/xAPIWrapper/src/verbs');
var xAPILaunch = require('./node_modules/xAPIWrapper/src/xapi-launch');
var xapiutil = require('./node_modules/xAPIWrapper/src/xapi-util');
const crypto = require('crypto');
var app = express();
var questionsDir = './data/questions';
var questionsIndexFile = './data/questions.json';
var encoding = 'utf8';
//console.log('xAPIWrapper', xAPIWrapper);



// --------
// Game API
// --------
app.post('/game/question', function (req, res) {
  var jsonString = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  try {
    req.on('end', function () {
      console.log('add question: jsonString',jsonString);
      const id = crypto.randomBytes(16).toString("hex");
      console.log('id',id);
      var newQuestionFile = questionsDir+'/'+id+'.json';
      fs.writeFile(newQuestionFile, jsonString, encoding, function (err) {
        console.log(err);
      });
      fs.readFile(questionsIndexFile, encoding, function (err, data) {
            if (err) throw err;
            var questionObj = JSON.parse(jsonString);
            var oldData = JSON.parse(data);
            oldData[id] = {"questions": questionObj.question}
            var newData = JSON.stringify(oldData);
            fs.writeFile (questionsIndexFile, newData, function(err) {
                if (err) throw err;
                console.log('complete');
            });
      });
    });
  } catch (error) {
    console.log('error',error);
  }
  res.status(200).send('{"result": "thanks"}');
});


// ----------------
// Raspberry Pi API
// ----------------
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