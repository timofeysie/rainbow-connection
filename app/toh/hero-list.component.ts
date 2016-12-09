// Observable Version
import { Component, OnInit } from '@angular/core';
import { Hero }              from './hero';
import { HeroService }       from './hero.service';

@Component({
  moduleId: module.id,
  selector: 'hero-list',
  templateUrl: 'hero-list.component.html',
  providers: [ HeroService ],
  styleUrls: ['hero-list.component.css', '../app.component.css']
})
export class HeroListComponent implements OnInit {
  errorMessage: string;
  heroes: Hero[];
  response: any;
  constructor (private heroService: HeroService) {}
  ngOnInit() { this.getHeroes(); }
  getHeroes() {
    this.heroService.getHeroes()
                    .subscribe(
                      (result) => { this.response = result
                        console.log('result',result); },
                      (error) =>  this.errorMessage = <any>error);
  }
  addHero (name: string) {
    if (!name) { return; }
    this.heroService.addHero(name)
                     .subscribe(
                       (result)  => {this.response = result
                         console.log('result',result);},
                       (error) =>  this.errorMessage = <any>error);
  }
  toggleGet() {
    this.heroService.toggleGet()
        .then((result) => { 
          this.response = result;
          console.log('result',result); 
        }, (error) =>  this.errorMessage = <any>error);
  }
  togglePost (name: string) {
    if (!name) { return; }
    this.heroService.togglePost(name)
        .then((result)  => {
          this.response = result;
          console.log('result',result);
        }, (error) =>  this.errorMessage = <any>error);
  }
  toggleGet2() {
    this.heroService.toggleGet2()
        .then((result) => { 
          this.response = result;
          console.log('result',result); 
        }, (error) =>  this.errorMessage = <any>error);
  }
}
