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
      console.log('user',body);
    let bodyString = body;
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ headers: headers }); 
    return this.http.post(this.userUrl+'/login', bodyString, options) 
        .map((res:Response) => res.json()) 
        .catch((error:any) => Observable.throw(error.json().error || 'Server error')); 
    }   

}