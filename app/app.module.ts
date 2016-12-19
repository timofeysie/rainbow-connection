import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';
import { AppComponent }  from './app.component';
import { HeroListComponent }  from './toh/hero-list.component';
import { LoginComponent } from './login/login.component';
import { CreateGameComponent } from './create-game/create-game.component';
import { AnswerComponent } from './create-game/answer.component';
import { GameService } from './providers/game.service';
import { UserService } from './providers/user.service';
import { EmitterService } from './providers/emitter.service';
import { QuestionListComponent } from './lists/question-list.component';
import { GameControlComponent } from './referee/game-control.component';
declare var ADL: any;

@NgModule({
  imports: [ 
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpModule,
    JsonpModule ],
  declarations: [ 
    AppComponent,
    HeroListComponent,
    LoginComponent,
    CreateGameComponent,
    AnswerComponent,
    QuestionListComponent,
    GameControlComponent ],
  providers: [
    GameService,
    UserService,
    EmitterService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
