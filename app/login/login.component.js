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
var forms_1 = require('@angular/forms');
var game_service_1 = require('../providers/game.service');
var LoginComponent = (function () {
    function LoginComponent(fb, gameService) {
        this.gameService = gameService;
        if (localStorage.getItem('jwt')) {
            this.authenticated = true;
            this.profile = JSON.parse(localStorage.getItem('profile'));
        }
        this.loginForm = fb.group({
            'email': ['test@tim.com', forms_1.Validators.required],
            'password': ['asdf', forms_1.Validators.required],
            'role': ['admin', forms_1.Validators.required],
        });
    }
    LoginComponent.prototype.submitForm = function (value) {
        var savesUser = localStorage.getItem('value.email');
        this.profile = {
            'email': value.email,
            'password': value.password,
            'role': value.role
        };
        this.authenticated = true;
        var questionOperation;
        questionOperation = this.gameService.getQuestions();
        questionOperation.subscribe(function (questions) {
            console.log('questions', questions);
        }, function (err) {
            // Log errors if any
            console.log('save err:', err);
        });
        if (!savesUser) {
            localStorage.setItem(value.email, JSON.stringify(this.profile));
        }
    };
    LoginComponent.prototype.logout = function () {
        this.authenticated = false;
    };
    LoginComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            styleUrls: ['../app.component.css'],
            selector: 'login-form',
            templateUrl: 'login.component.html'
        }), 
        __metadata('design:paramtypes', [forms_1.FormBuilder, game_service_1.GameService])
    ], LoginComponent);
    return LoginComponent;
}());
exports.LoginComponent = LoginComponent;
//# sourceMappingURL=login.component.js.map