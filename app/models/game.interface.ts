export interface Question {
    name: string;
    answers: Answer[];
}

export interface Answer {
    answerText: string;
    correct: string;
}