import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { QuestionObject } from '../models/game.interface';

@Injectable()
export class GameService {
  constructor(private http: Http) {
  }
  private gameUrl = 'game'; 

  add(body: Object): Observable<QuestionObject[]> {
    let bodyString = JSON.stringify(body); // Stringify payload
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ headers: headers }); 
    return this.http.post(this.gameUrl+'/question', bodyString, options) 
        .map((res:Response) => res.json()) 
        .catch((error:any) => Observable.throw(error.json().error || 'Server error')); 
    }   

    getQuestions(): Observable<QuestionObject[]> {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers }); 
        return this.http.get(this.gameUrl+'/question', options) 
        .map((res:Response) => res.json()) 
        .catch((error:any) => Observable.throw(error.json().error || 'Server error')); 
    }  

}