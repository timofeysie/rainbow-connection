import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { QuestionObject } from '../models/game.interface';

@Injectable()
export class UserService {
  constructor(private http: Http) {
  }
  private userUrl = 'user'; 

  login(body: Object): Observable<QuestionObject[]> {
    let bodyString = JSON.stringify(body); // Stringify payload
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ headers: headers }); 
    return this.http.post(this.userUrl+'/login', bodyString, options)  
        .map((res:Response) => res.json()) 
        .catch((error:any) => Observable.throw('what?'+error.json().error || 'Server error')); 
  }

  getUsers(): Observable<QuestionObject[]> {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers }); 
        return this.http.get(this.userUrl+'s', options) 
        .map((res:Response) => res.json()) 
        .catch((error:any) => Observable.throw(error.json().error || 'Server error')); 
  }  

}