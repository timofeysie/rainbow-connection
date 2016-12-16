import { Component, Input } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { GameService } from '../providers/game.service';
import { EmitterService } from '../providers/emitter.service';
import { Observable } from 'rxjs/Rx';

@Component({
  moduleId: module.id,
  styleUrls: ['../app.component.css'],
  selector: 'game-control',
  templateUrl: 'game-control.component.html'
})
export class GameControlComponent {
  constructor(
    private gameService: GameService) { 
        this.gameState = 'pre-game';
    }

    questionNumber: number;
    playerList: any [];
    gameState: string;

    ready() {
        this.gameState = 'ready';
    }
    start() {
        this.questionNumber = 0;
        this.gameState = 'game on';
    }
    pause() {
        this.gameState = 'pause';
    }
    endTurn() {
        this.gameState = 'turn over';
    }
}