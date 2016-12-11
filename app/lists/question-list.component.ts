import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { GameService } from '../providers/game.service';
import { EmitterService } from '../providers/emitter.service';
import { QuestionObject } from '../models/game.interface';

@Component({
    selector: 'question-list',
    templateUrl: 'question-list.component'
})
export class QuestionListComponent implements OnInit, OnChanges{
    questions: QuestionObject[];
    private listId = 'COMMENT_COMPONENT_LIST';
    constructor(private gameService: GameService) {}

    ngOnInit() {
            this.loadQuestions()
    }

    loadQuestions() {
        this.gameService.getQuestions()
            .subscribe(
                questions => this.questions = questions,
                err => {
                console.log(err);
            }
        );
    }

    ngOnChanges(changes:any) {
        EmitterService.get(this.listId).subscribe((questions:QuestionObject[]) => { 
            this.loadQuestions()});
    }

}