"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('@angular/core');
var user_service_1 = require('../providers/user.service');
var emitter_service_1 = require('../providers/emitter.service');
var UserListComponent = (function () {
    function UserListComponent(userService) {
        this.userService = userService;
        this.listId = 'COMMENT_COMPONENT_LIST';
    }
    UserListComponent.prototype.ngOnInit = function () {
        this.loadUsers();
    };
    UserListComponent.prototype.loadUsers = function () {
        var _this = this;
        this.userService.getUsers().toArray()
            .subscribe(function (users) {
            var response = Object(users[0]);
            _this.users = [];
            for (var i in response) {
                _this.users.push(response[i]);
            }
        }, function (err) {
            console.log(err);
        });
    };
    UserListComponent.prototype.ngOnChanges = function (changes) {
        var _this = this;
        emitter_service_1.EmitterService.get(this.listId).subscribe(function (users) {
            _this.loadUsers();
        });
    };
    UserListComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'user-list',
            templateUrl: 'user-list.component.html',
            styleUrls: ['../app.component.css']
        }), 
        __metadata('design:paramtypes', [user_service_1.UserService])
    ], UserListComponent);
    return UserListComponent;
}());
exports.UserListComponent = UserListComponent;
//# sourceMappingURL=user-list.component.js.map