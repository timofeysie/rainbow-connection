import { Component, OnInit, OnChanges } from '@angular/core';
import { GameService } from '../providers/game.service';
import { EmitterService } from '../providers/emitter.service';
import { QuestionObject } from '../models/game.interface';

@Component({
    moduleId: module.id,
    selector: 'question-list',
    templateUrl: 'question-list.component.html'
})
export class QuestionListComponent implements OnInit, OnChanges {
    questions: QuestionObject[];
    private listId = 'COMMENT_COMPONENT_LIST';
    constructor(private gameService: GameService) { }

    ngOnInit() {
            this.loadQuestions()
    }

    loadQuestions() {
        this.gameService.getQuestions().toArray()
            .subscribe(questions => {
                let response = Object(questions[0]);
                this.questions = [];
                for(var i in response) {
                    this.questions.push(response[i]);
                }
                console.log('questions',questions);
                console.log('this.questions',this.questions);
            },
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