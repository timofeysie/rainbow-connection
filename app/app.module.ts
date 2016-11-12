import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';
import { AppComponent }  from './app.component';
import { HeroListComponent }  from './toh/hero-list.component';
declare var ADL: any;

@NgModule({
  imports: [ 
    BrowserModule,
    FormsModule,
    HttpModule,
    JsonpModule ],
  declarations: [ 
    AppComponent,
    HeroListComponent ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
