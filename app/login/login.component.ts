import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

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

  constructor(fb: FormBuilder){
    if(localStorage.getItem('jwt')){
      this.authenticated = true;
      this.profile = JSON.parse(localStorage.getItem('profile'));
    }
    this.loginForm = fb.group({
      'email' : ['test@tim.com', Validators.required],
      'password': ['asdf', Validators.required],
      'role': ['admin', Validators.required],
    })
  }

  submitForm(value: any) {
    let savesUser = localStorage.getItem('value.email');
    this.profile = {
      'email' : value.email,
      'password' : value.password,
      'role' : value.role
    }
    this.authenticated = true;
    if (!savesUser) {
      localStorage.setItem(value.email, JSON.stringify(this.profile));
    }
  }
  
  logout() {
    this.authenticated = false;
  }
}
