export interface Customer {
    name: string;
    answers: Answer[];
}

export interface Answer {
    answerText: string;
    correct: string;
}