import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { BrowserModule }  from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { ToggleService } from './services/toggle.service';
@NgModule({
  imports: [
    BrowserModule,
    HttpModule
  ],
  declarations: [
    AppComponent
  ],
  providers: [
      ToggleService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
