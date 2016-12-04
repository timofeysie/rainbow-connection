import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Customer } from '../models/game.interface';

@Component({
  moduleId: module.id,
  selector: 'create-game',
  templateUrl: 'create-game.component.html',
})
export class CreateGameComponent implements OnInit {
    public myForm: FormGroup;

    constructor(private _fb: FormBuilder) { }

    ngOnInit() {
        this.myForm = this._fb.group({
            name: ['', [Validators.required, Validators.minLength(5)]],
            answers: this._fb.array([
                this.initAnswer(),
            ])
        });
    }

    initAnswer() {
        return this._fb.group({
            street: ['', Validators.required],
            postcode: ['']
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

    save(model: Customer) {
        console.log(model);
    }
}