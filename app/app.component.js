"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('@angular/core');
var xapiwrapper_1 = require('../../vendor/xapiwrapper');
require('./rxjs-operators');
var AppComponent = (function () {
    function AppComponent(adl) {
        this.adl = adl;
        var conf = this.getConfig();
        this.adl.XAPIWrapper.changeConfig(conf);
    }
    AppComponent.prototype.getConfig = function () {
        var conf = {};
        conf['endpoint'] = "http://localhost:8000/xapi/";
        try {
            conf['auth'] = 'Basic tom:1234';
        }
        catch (e) {
            log("Exception in Config trying to encode auth: " + e);
        }
        return conf;
    };
    AppComponent = __decorate([
        core_1.Component({
            selector: 'my-app',
            styleUrls: ['app/app.component.css'],
            templateUrl: 'app/app.component.html'
        }), 
        __metadata('design:paramtypes', [(typeof (_a = typeof xapiwrapper_1.ADL !== 'undefined' && xapiwrapper_1.ADL) === 'function' && _a) || Object])
    ], AppComponent);
    return AppComponent;
    var _a;
}());
exports.AppComponent = AppComponent;
//# sourceMappingURL=app.component.js.map