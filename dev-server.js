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
var usersIndexFile = './data/users.json';
var usersDir = './data/users';
var usersLoggedIn = './data/users/logged.json';
var encoding = 'utf8';
//console.log('xAPIWrapper', xAPIWrapper);

/*
User API
--------
app.post('/user/login // user email and password and id if existing user

Game API
--------
app.post('/game/question' // Add a question
app.get('/game/question' // Get all questions

app.post('/xapi', // xAPI test endpoint

app.get('/toggle', // API call to toggle the light on and off
var configPin_18_isLedOn = 0;
app.get('/toggle2' // Toggle 2 example
app.post('/toggle' // not used
*/


// ---------------------------------------- //
//                 User APIs                // 
// ---------------------------------------- //
app.post('/user/login', function (req, res) {
  var resultCode = 200; // default server error
  var resultBody = '{"result": "defult"}';
  var jsonString = '';
  req.on('data', function (data) {
      jsonString += data;
  });
  req.on('end', function () {
    console.log('jsonString',jsonString);
      var user = JSON.parse(jsonString);
      // load users list and check if user exists
      fs.readFile(usersIndexFile, encoding, function (err, data) {
        if (err) throw err;
        var users = JSON.parse(data);
        console.log('looking for',user.email);
        var userExistsBool = false;
        var foundUser;
        for (var property in users) {
            if (users.hasOwnProperty(property)) {
                if (users[property].email === user.email) {
                  foundUser = { "id": property, "email":users[property].email};
                  userExistsBool = true;
                  var userFile = usersDir+'/'+property+'.json';
                  // load the users file, check the password
                  fs.readFile(userFile, encoding, function (err, userData) {
                    var userObj = JSON.parse(userData);
                    if (user.password === userObj.password) {
                      console.log('match',userObj);
                      // TODO: save current time
                      resultCode = 200;
                      resultBody = {
                        'result': 'ok',
                        'id': property};
                      console.log('resultBody',resultBody);
                      res.status(resultCode).send(resultBody);
                    } else {
                      console.log('no match');
                      // return 401 Unauthenticated request
                      resultCode = 401;
                      resultBody = {
                        'result': 'failed'};
                      res.status(resultCode).send(resultBody);
                    }
                  });
                }
            }
        }
        
        // if the user doesn't exist,
        // add user to the users.json file
        // and create a file with their email, password, and role, etc.
        if (!userExistsBool) {
            console.log('new user');
            var id = crypto.randomBytes(16).toString("hex");
            users[id] = {'email': user.email,
              'role': user.role}
            var newData = JSON.stringify(users);
            fs.writeFile (usersIndexFile, newData, function(err) {
                if (err) throw err;
                console.log('complete!');
            });
            // add user file in the users directory
            var userFile = usersDir+'/'+id+'.json';
            if (fs.existsSync(userFile)) {
              console.log('user logged in previously');
            } else {
              //create new user file
              fs.writeFile(userFile, jsonString, encoding, function (err) {
                console.log(err);
              });
            }
            resultCode = 401;
            resultBody = {
              'result': 'added_user'};
            res.status(resultCode).send(resultBody);
        }
      }); 
    });
});

/** Get all user.
 * Return the email and role.
 */
app.get('/users', function (req, res) {
    fs.readFile(usersIndexFile, encoding, function (err, data) {
      if (err) throw err;
      var questions = JSON.parse(data);
      console.log('data',data);
      res.status(200).send(data);
    });
});


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
            });
      });
    });
  } catch (error) {
    console.log('error',error);
  }
  res.status(200).send('{"result": "thanks"}');
});
// Get all questions
app.get('/game/question', function (req, res) {
    fs.readFile(questionsIndexFile, encoding, function (err, data) {
      if (err) throw err;
      var questions = JSON.parse(data);
      res.status(200).send(data);
    });
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