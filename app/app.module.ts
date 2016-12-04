import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';
import { AppComponent }  from './app.component';
import { HeroListComponent }  from './toh/hero-list.component';
import { LoginComponent } from './login/login.component';
import { CreateGameComponent } from './create-game/create-game.component';
import { AddressComponent } from './create-game/address.component';
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
    AddressComponent ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
