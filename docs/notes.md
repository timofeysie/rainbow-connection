# Notes

## zone.js:1382 POST http://localhost:3000/user/login 500 (Internal Server Error)
EXCEPTION: Unexpected end of JSON input
The service has to be very concise with it's observables. 
Adding extra block of code for example to log out parts of the equation seemed to be causing the problem.
Also, on the node end, we were returning the response before the files had finished being read.
Node is tricky like that.  
None blocking means you really have to be careful when a particular order of executtion is required.


## Argument of type '(resp: any, error: any) => void' is not assignable to 
Argument of type '(resp: any, error: any) => void' is not assignable to parameter of type 'NextObserver<QuestionObject[]> | ErrorObserver<QuestionObject[]> | CompletionObserver<QuestionObj...'.
  Type '(resp: any, error: any) => void' is not assignable to type '(value: QuestionObject[]) => void'.

## Error Cannot read property 'Symbol(Symbol.iterator)' of undefined

When testing a failed login, this error popped up:
```
core.umd.js:3010 TypeError: Cannot read property 'Symbol(Symbol.iterator)' of undefined
    at Object.subscribeToResult (subscribeToResult.ts:58)
```

That was for a successful login, and, the app is functioning normally.

For what should be a failed login, we get this:
```
zone.js:1382 POST http://localhost:3000/user/login 500 (Internal Server Error)scheduleTask 
@ zone.js:1382ZoneDelegate.scheduleTask @ zone.js:245Zone.scheduleMacroTask 
@ zone.js:171(anonymous function) @ zone.js:1405send @ VM8598:3(anonymous function) @ http.umd.js:1128Observable.subscribe @ Observable.ts:95Observable._subscribe @ Observable.ts:155MapOperator.call @ map.ts:54Observable.subscribe @ Observable.ts:93Observable._subscribe @ Observable.ts:155CatchOperator.call @ catch.ts:35Observable.subscribe @ Observable.ts:93LoginComponent.submitForm @ login.component.ts:37_View_LoginComponent1._handle_ngSubmit_5_0 @ component.ngfactory.js:535(anonymous function) @ core.umd.js:9437schedulerFn @ forms.umd.js:1562SafeSubscriber.__tryOrUnsub @ Subscriber.ts:238SafeSubscriber.next @ Subscriber.ts:190Subscriber._next @ Subscriber.ts:135Subscriber.next @ Subscriber.ts:95Subject.next @ Subject.ts:61EventEmitter.emit @ forms.umd.js:1542FormGroupDirective.onSubmit @ forms.umd.js:3622_View_LoginComponent1._handle_submit_5_1 @ component.ngfactory.js:542(anonymous function) @ core.umd.js:9437(anonymous function) @ platform-browser.umd.js:1525(anonymous function) @ platform-browser.umd.js:1638ZoneDelegate.invoke @ zone.js:232onInvoke @ core.umd.js:6206ZoneDelegate.invoke @ zone.js:231Zone.runGuarded @ zone.js:128NgZone.runGuarded 
@ core.umd.js:6101outsideHandler @ platform-browser.umd.js:1638ZoneDelegate.invokeTask 
@ zone.js:265Zone.runTask @ zone.js:154ZoneTask.invoke @ zone.js:335
user.service.ts:24 
error Response_body: "{"result": "thanks"}"
headers: Headersok: falsestatus: 500
statusText: "Internal Server Error"type: 2
url: "http://localhost:3000/user/login"__proto__: Body
login.component.ts:53 questions Object
9a1aa0a1c5db8e03298a4d399802b125: Object
questions: "What is A"__proto__: Object
fec144be88a600cf831ee75b37c27628: Object__proto__: Object
```
