export interface Question {
    name: string;
    answers: Answer[];
}

export interface Answer {
    answerText: string;
    correct: boolean;
}

export interface User {
    id: string;
    email: string;
    password: string;
}

export class QuestionObject implements Question {
    constructor(
        public name: string, 
        public answers: AnswerObject[]
        ){}
}

export class AnswerObject implements Answer {
    constructor(
        public answerText: string,
        public correct: boolean
    ) {}
}

export class UserObject implements User {
    constructor(
        public id: string,
        public email: string, 
        public password: string
        ){}
}