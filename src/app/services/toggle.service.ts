import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';
import {Observable} from 'rxjs/Rx';

// Import RxJs required methods
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

@Injectable()
export class ToggleService {
     // Resolve HTTP using the constructor
     constructor (private http: Http) {}
     // private instance variable to hold base url
     private toggleUrl = 'http://localhost:3000/toggle'; 

     lightOne() {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });
        console.log('options',options);
         return this.http.post(this.toggleUrl, null, options)
            .map((res:Response) => res.json())
            .catch((error:any) => Observable.throw(error.json().error || 'Server error'));
    }
}