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
// Observable Version
var core_1 = require('@angular/core');
var hero_service_1 = require('./hero.service');
var HeroListComponent = (function () {
    function HeroListComponent(heroService) {
        this.heroService = heroService;
    }
    HeroListComponent.prototype.ngOnInit = function () { this.getHeroes(); };
    HeroListComponent.prototype.getHeroes = function () {
        var _this = this;
        this.heroService.getHeroes()
            .subscribe(function (result) { _this.response = result; }, function (error) { return _this.errorMessage = error; });
    };
    HeroListComponent.prototype.addHero = function (name) {
        var _this = this;
        if (!name) {
            return;
        }
        this.heroService.addHero(name)
            .subscribe(function (result) { _this.response = result; }, function (error) { return _this.errorMessage = error; });
    };
    HeroListComponent.prototype.toggleGet = function () {
        var _this = this;
        this.heroService.toggleGet()
            .then(function (result) {
            _this.response = result;
        }, function (error) { return _this.errorMessage = error; });
    };
    HeroListComponent.prototype.togglePost = function (name) {
        var _this = this;
        if (!name) {
            return;
        }
        this.heroService.togglePost(name)
            .then(function (result) {
            _this.response = result;
        }, function (error) { return _this.errorMessage = error; });
    };
    HeroListComponent.prototype.toggleGet2 = function () {
        var _this = this;
        this.heroService.toggleGet2()
            .then(function (result) {
            _this.response = result;
        }, function (error) { return _this.errorMessage = error; });
    };
    HeroListComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'hero-list',
            templateUrl: 'hero-list.component.html',
            providers: [hero_service_1.HeroService],
            styleUrls: ['hero-list.component.css', '../app.component.css']
        }), 
        __metadata('design:paramtypes', [hero_service_1.HeroService])
    ], HeroListComponent);
    return HeroListComponent;
}());
exports.HeroListComponent = HeroListComponent;
//# sourceMappingURL=hero-list.component.js.map