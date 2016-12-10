import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Observable } from 'rxjs/Rx';
import { Question } from '../models/game.interface';
import { GameService } from '../providers/game.service';

@Component({
  moduleId: module.id,
  selector: 'create-game',
  styleUrls: ['../app.component.css'],
  templateUrl: 'create-game.component.html',
})
export class CreateGameComponent implements OnInit {
    public myForm: FormGroup;

    constructor(
        private _fb: FormBuilder,
        private gameService: GameService) { }

    ngOnInit() {
        this.myForm = this._fb.group({
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
        const control = <FormArray>this.myForm.controls['answers'];
        control.push(this.initAnswer());
    }

    removeAnswer(i: number) {
        const control = <FormArray>this.myForm.controls['answers'];
        control.removeAt(i);
    }

    save(_questionForm: any) {
        let question = Object(_questionForm.value);
        console.log('save',question);
        let questionOperation:Observable<Comment[]>;
        questionOperation = this.gameService.add(question);
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
