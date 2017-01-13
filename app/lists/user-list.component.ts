import { Component, OnInit, OnChanges } from '@angular/core';
import { UserService } from '../providers/user.service';
import { EmitterService } from '../providers/emitter.service';
import { UserObject } from '../models/game.interface';

@Component({
    moduleId: module.id,
    selector: 'user-list',
    templateUrl: 'user-list.component.html',
    styleUrls: ['../app.component.css']
})
export class UserListComponent implements OnInit, OnChanges {
    users: UserObject[];
    private listId = 'COMMENT_COMPONENT_LIST';
    constructor(private userService: UserService) { }

    ngOnInit() {
            this.loadUsers()
    }

    loadUsers() {
        this.userService.getUsers().toArray()
            .subscribe(users => {
                let response = Object(users[0]);
                this.users = [];
                for(var i in response) {
                    this.users.push(response[i]);
                    console.log('ser',response[i]);
                }
            },
                err => {
                console.log(err);
            }
        );
    }

    ngOnChanges(changes:any) {
        EmitterService.get(this.listId).subscribe((users:UserObject[]) => { 
            this.loadUsers()});
    }

}