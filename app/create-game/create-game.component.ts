import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Observable } from 'rxjs/Rx';
import { QuestionObject } from '../models/game.interface';
import { GameService } from '../providers/game.service';

@Component({
  moduleId: module.id,
  selector: 'create-game',
  styleUrls: ['../app.component.css'],
  templateUrl: 'create-game.component.html',
})
export class CreateGameComponent implements OnInit {
    public questionForm: FormGroup;

    constructor(
        private _fb: FormBuilder,
        private gameService: GameService) { }

    ngOnInit() {
        this.questionForm = this._fb.group({
            question: ['', [Validators.required, Validators.minLength(5)]],
            answers: this._fb.array([
                this.initAnswer(),
            ])
        });
    }

    initAnswer() {
        return this._fb.group({
            answerText: ['', Validators.required],
            correct: [false]
        });
    }

    addAnswer() {
        const control = <FormArray>this.questionForm.controls['answers'];
        control.push(this.initAnswer());
    }

    removeAnswer(i: number) {
        const control = <FormArray>this.questionForm.controls['answers'];
        control.removeAt(i);
    }

    save(_questionForm: FormGroup) {
        let questionOperation:Observable<QuestionObject[]>;
        questionOperation = this.gameService.add(_questionForm.value);
        questionOperation.subscribe(
            questions => {
                console.log('questions',questions);
            }, 
            err => {
                // Log errors if any
                console.log('save err:',err);
            });
    }
}
