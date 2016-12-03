import { Component } from '@angular/core';
import { ADL } from '../../vendor/xapiwrapper';

import './rxjs-operators';
@Component({
    selector: 'my-app',
    styleUrls: ['app/app.component.css'],
    templateUrl: 'app/app.component.html'
})
export class AppComponent {
    constructor(private adl: ADL) {
        var conf = this.getConfig();
        this.adl.XAPIWrapper.changeConfig(conf);
    }

    getConfig() {
        var conf = {};
        conf['endpoint'] = "http://localhost:8000/xapi/";
        try {
            conf['auth'] = 'Basic tom:1234';
        }
        catch (e) {
            log("Exception in Config trying to encode auth: " + e);
        }
        return conf;
    }
 }
