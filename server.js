var http = require('http');
var express = require('express');
console.log('wpi');
var wpi = require('pi-gpio');
console.log('wpi',wpi);
var app = express();
// an array of objects for the client to query
// var inputs = [{ pin: '11', gpio: '17', value: 1 },
//               { pin: '12', gpio: '18', value: 0 }];

var inputs = [{ pin: '16', gpio: '23', value: null },
              { pin: '22', gpio: '25', value: null }];

// initialise the GPIO and open the ports as inputs
var i;
for (i in inputs) {
  console.log('opening GPIO port ' + inputs[i].gpio 
    + ' on pin ' + inputs[i].pin + ' as input');
  gpio.open(inputs[i].pin, "input", function (err) {
    if (err) {
      throw err;
    }
  });
}

// add a timer loop to read each GPIO input and store the latest value 
// in our inputs array. 
// For this, we use the pi-gpio library function gpio.read.
// read and store the GPIO inputs twice a second
setInterval( function () {
  gpio.read(inputs[0].pin, function (err, value) {
    if (err) {
      throw err;
    }
    console.log('read pin ' + inputs[0].pin + ' value = ' + value);
    // update the inputs object
    inputs[0].value = value.toString(); // store value as a string
  });

  gpio.read(inputs[1].pin, function (err, value) {
    if (err) {
      throw err;
    }
    console.log('read pin ' + inputs[1].pin + ' value = ' + value);
    inputs[1].value = value.toString();
  });
}, 500); // setInterval



// serve index.html and static pages stored in the home directory,
// and the myclient.js file
//app.use(express['static'](__dirname ));
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

process.on('SIGINT', function() {
  var i;
  console.log("\nGracefully shutting down from SIGINT (Ctrl+C)");
  console.log("closing GPIO...");
  for (i in inputs) {
    gpio.close(inputs[i].pin);
  }
  process.exit();
});

app.listen(3000);
console.log('App Server running at port 3000');