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
var game_service_1 = require('../providers/game.service');
var emitter_service_1 = require('../providers/emitter.service');
var QuestionListComponent = (function () {
    function QuestionListComponent(gameService) {
        this.gameService = gameService;
        this.listId = 'COMMENT_COMPONENT_LIST';
    }
    QuestionListComponent.prototype.ngOnInit = function () {
        this.loadQuestions();
    };
    QuestionListComponent.prototype.loadQuestions = function () {
        var _this = this;
        this.gameService.getQuestions().toArray()
            .subscribe(function (questions) {
            var response = Object(questions[0]);
            _this.questions = [];
            for (var i in response) {
                _this.questions.push(response[i]);
            }
            console.log('questions', questions);
            console.log('this.questions', _this.questions);
        }, function (err) {
            console.log(err);
        });
    };
    QuestionListComponent.prototype.ngOnChanges = function (changes) {
        var _this = this;
        emitter_service_1.EmitterService.get(this.listId).subscribe(function (questions) {
            _this.loadQuestions();
        });
    };
    QuestionListComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'question-list',
            templateUrl: 'question-list.component.html'
        }), 
        __metadata('design:paramtypes', [game_service_1.GameService])
    ], QuestionListComponent);
    return QuestionListComponent;
}());
exports.QuestionListComponent = QuestionListComponent;
//# sourceMappingURL=question-list.component.js.map