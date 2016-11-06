import { Component } from '@angular/core';
import '../../public/css/styles.css';
import { ToggleService } from '../app/services/toggle.service';
@Component({
  selector: 'my-app',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent { 
  constructor(private toggleService: ToggleService) {
  }
  
  toggleLight() {
    console.log('toggle light');
    this.toggleService.lightOne();
  }
}
