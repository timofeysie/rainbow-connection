
"use strict";

var xAPIWrapper = require('./xapiwrapper');
var xAPIStatement = require('./xapistatement');
var verbs = require('./verbs');
var xAPILaunch = require('./xapi-launch');
var xapiutil = require('./xapi-util');

// if (typeof window !== 'undefined'){
//     window.ADL = {xAPIWrapper: xAPIWrapper, XAPIStatement: xAPIStatement, verbs: verbs, launch: xAPILaunch, xapiutil: xapiutil};
// } else {
//     module.exports = {XAPIWrapper: xAPIWrapper};
// }

var toExport = {
  XAPIWrapper: xAPIWrapper,
  XAPIStatement: xAPIStatement,
  verbs: verbs,
  launch: xAPILaunch,
  xapiutil: xapiutil
};

(function() {
  var root = this;
  if( typeof window === 'undefined' ) {
    exports = module.exports = toExport;
    exports.ADL = toExport;
  } else {
    root.ADL = toExport;    // this attaches to the window
    window.ADL = toExport;
  }
}).call(this);
