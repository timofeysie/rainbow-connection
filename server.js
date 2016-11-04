var http = require('http');
var express = require('express');
var app = express();
// an array of objects for the client to query
var inputs = [{ pin: '11', gpio: '17', value: 1 },
              { pin: '12', gpio: '18', value: 0 }];

// serve index.html and static pages stored in the home directory,
// and the myclient.js file
app.use(express['static'](__dirname ));

// define the API for routes to the API calls and/or 
// page requests to our server.

app.get('/inputs/:id', function(req, res) {
  res.status(200).send(inputs[req.params.id]);
}); 

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