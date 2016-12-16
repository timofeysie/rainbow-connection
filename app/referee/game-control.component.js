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
var GameControlComponent = (function () {
    function GameControlComponent(gameService) {
        this.gameService = gameService;
        this.gameState = 'pre-game';
    }
    GameControlComponent.prototype.ready = function () {
        this.gameState = 'ready';
    };
    GameControlComponent.prototype.start = function () {
        this.questionNumber = 0;
        this.gameState = 'game on';
    };
    GameControlComponent.prototype.pause = function () {
        this.gameState = 'pause';
    };
    GameControlComponent.prototype.endTurn = function () {
        this.gameState = 'turn over';
    };
    GameControlComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            styleUrls: ['../app.component.css'],
            selector: 'game-control',
            templateUrl: 'game-control.component.html'
        }), 
        __metadata('design:paramtypes', [game_service_1.GameService])
    ], GameControlComponent);
    return GameControlComponent;
}());
exports.GameControlComponent = GameControlComponent;
//# sourceMappingURL=game-control.component.js.map