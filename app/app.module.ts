import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';
import { AppComponent }  from './app.component';
import { HeroListComponent }  from './toh/hero-list.component';
import { LoginComponent } from './login/login.component';
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
    LoginComponent ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
