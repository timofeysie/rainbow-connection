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
var CreateGameComponent = (function () {
    function CreateGameComponent(_fb, gameService) {
        this._fb = _fb;
        this.gameService = gameService;
    }
    CreateGameComponent.prototype.ngOnInit = function () {
        this.myForm = this._fb.group({
            question: ['', [forms_1.Validators.required, forms_1.Validators.minLength(5)]],
            answers: this._fb.array([
                this.initAnswer(),
            ])
        });
    };
    CreateGameComponent.prototype.initAnswer = function () {
        return this._fb.group({
            answerText: ['', forms_1.Validators.required],
            correct: [false]
        });
    };
    CreateGameComponent.prototype.addAnswer = function () {
        var control = this.myForm.controls['answers'];
        control.push(this.initAnswer());
    };
    CreateGameComponent.prototype.removeAnswer = function (i) {
        var control = this.myForm.controls['answers'];
        control.removeAt(i);
    };
    CreateGameComponent.prototype.save = function (_questionForm) {
        var question = Object(_questionForm.value);
        console.log('save', question);
        var questionOperation;
        questionOperation = this.gameService.add(question);
        questionOperation.subscribe(function (questions) {
            console.log('questions', questions);
        }, function (err) {
            // Log errors if any
            console.log('save err:', err);
        });
    };
    CreateGameComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'create-game',
            styleUrls: ['../app.component.css'],
            templateUrl: 'create-game.component.html',
        }), 
        __metadata('design:paramtypes', [forms_1.FormBuilder, game_service_1.GameService])
    ], CreateGameComponent);
    return CreateGameComponent;
}());
exports.CreateGameComponent = CreateGameComponent;
//# sourceMappingURL=create-game.component.js.map