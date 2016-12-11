import { Component, Input } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { GameService } from '../providers/game.service';
import { EmitterService } from '../providers/emitter.service';
import { Observable } from 'rxjs/Rx';

@Component({
  moduleId: module.id,
  styleUrls: ['../app.component.css'],
  selector: 'login-form',
  templateUrl: 'login.component.html'
})
export class LoginComponent {
  loginForm : FormGroup;
  authenticated: boolean
  profile : Object;
  @Input() listId: string;

  constructor(
    fb: FormBuilder,
    private gameService: GameService) {
      if(localStorage.getItem('jwt')){
        this.authenticated = true;
        this.profile = JSON.parse(localStorage.getItem('profile'));
      }
      this.loginForm = fb.group({
        'email' : ['test@tim.com', Validators.required],
        'password': ['asdf', Validators.required],
        'role': ['admin', Validators.required],
      });
  }

  submitForm(value: any) {
    let savesUser = localStorage.getItem('value.email');
    this.profile = {
      'email' : value.email,
      'password' : value.password,
      'role' : value.role
    }
    this.authenticated = true;
     let questionOperation:Observable<any[]>;
        questionOperation = this.gameService.getQuestions();
        questionOperation.subscribe(
            questions => {
                console.log('questions',questions);
                EmitterService.get(this.listId).emit(questions);
            }, 
            err => {
                // Log errors if any
                console.log('save err:',err);
            });
    if (!savesUser) {
      localStorage.setItem(value.email, JSON.stringify(this.profile));
    }
  }
  
  logout() {
    this.authenticated = false;
  }
}
