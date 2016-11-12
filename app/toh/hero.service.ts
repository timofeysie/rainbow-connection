import { Injectable }     from '@angular/core';
import { Http, Response } from '@angular/http';
import { Hero }           from './hero';
import { Observable }     from 'rxjs/Observable';
import { Headers, RequestOptions } from '@angular/http';
@Injectable()
export class HeroService {
  private heroesUrl = 'toggle'; 
  private heroesUrl2 = 'toggle2'; 
  constructor (private http: Http) {}
  addHero (name: string): Observable<any> {
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ headers: headers });
    return this.http.post(this.heroesUrl, { name }, options)
                    .map(this.extractData)
                    .catch(this.handleError);
  }
  togglePost (name: string): Promise<any> {
    return new Promise((resolve, reject) => {
      let headers = new Headers({ 'Content-Type': 'application/json' });
      let options = new RequestOptions({ headers: headers });
      this.http.post(this.heroesUrl, { name }, options)
        .subscribe(res => {
          resolve (res);
         }, (err) => {
            reject(err);
        });
    });
  }
  getHeroes (): Observable<any> {
    return this.http.get(this.heroesUrl)
                    .map(this.extractData)
                    .catch(this.handleError);
  }
  toggleGet(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get(this.heroesUrl)
        .subscribe(res => {
          resolve (res);
        }, (err) => {
          reject(err);
        });
    });
  }
  private extractData(res: Response) {
    console.log('res');
    return res;
  }
  private handleError (error: Response | any) {
    let errMsg: string;
    if (error instanceof Response) {
      const body = error.json() || '';
      const err = body.error || JSON.stringify(body);
      errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
    } else {
      errMsg = error.message ? error.message : error.toString();
    }
    console.error(errMsg);
    return Observable.throw(errMsg);
  }

  /** Toggle 2 */
  toggleGet2(): Promise<any> {
    return new Promise((resolve, reject) => {
      this.http.get(this.heroesUrl2)
        .subscribe(res => {
          resolve (res);
        }, (err) => {
          reject(err);
        });
    });
  }
}
