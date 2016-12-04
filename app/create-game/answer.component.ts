import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
    moduleId: module.id,
    selector: 'answer',
    templateUrl: 'answer.component.html',
})
export class AnswerComponent {
    @Input('group')
    public answerForm: FormGroup;
}