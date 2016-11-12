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
var http_1 = require('@angular/http');
var Observable_1 = require('rxjs/Observable');
var http_2 = require('@angular/http');
var HeroService = (function () {
    function HeroService(http) {
        this.http = http;
        this.heroesUrl = 'toggle';
        this.heroesUrl2 = 'toggle2';
    }
    HeroService.prototype.addHero = function (name) {
        var headers = new http_2.Headers({ 'Content-Type': 'application/json' });
        var options = new http_2.RequestOptions({ headers: headers });
        return this.http.post(this.heroesUrl, { name: name }, options)
            .map(this.extractData)
            .catch(this.handleError);
    };
    HeroService.prototype.togglePost = function (name) {
        var _this = this;
        return new Promise(function (resolve, reject) {
            var headers = new http_2.Headers({ 'Content-Type': 'application/json' });
            var options = new http_2.RequestOptions({ headers: headers });
            _this.http.post(_this.heroesUrl, { name: name }, options)
                .subscribe(function (res) {
                resolve(res);
            }, function (err) {
                reject(err);
            });
        });
    };
    HeroService.prototype.getHeroes = function () {
        return this.http.get(this.heroesUrl)
            .map(this.extractData)
            .catch(this.handleError);
    };
    HeroService.prototype.toggleGet = function () {
        var _this = this;
        return new Promise(function (resolve, reject) {
            _this.http.get(_this.heroesUrl)
                .subscribe(function (res) {
                resolve(res);
            }, function (err) {
                reject(err);
            });
        });
    };
    HeroService.prototype.extractData = function (res) {
        console.log('res');
        return res;
    };
    HeroService.prototype.handleError = function (error) {
        var errMsg;
        if (error instanceof http_1.Response) {
            var body = error.json() || '';
            var err = body.error || JSON.stringify(body);
            errMsg = error.status + " - " + (error.statusText || '') + " " + err;
        }
        else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Observable_1.Observable.throw(errMsg);
    };
    /** Toggle 2 */
    HeroService.prototype.toggleGet2 = function () {
        var _this = this;
        return new Promise(function (resolve, reject) {
            _this.http.get(_this.heroesUrl2)
                .subscribe(function (res) {
                resolve(res);
            }, function (err) {
                reject(err);
            });
        });
    };
    HeroService = __decorate([
        core_1.Injectable(), 
        __metadata('design:paramtypes', [http_1.Http])
    ], HeroService);
    return HeroService;
}());
exports.HeroService = HeroService;
//# sourceMappingURL=hero.service.js.map