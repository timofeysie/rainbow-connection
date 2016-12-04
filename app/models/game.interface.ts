export interface Customer {
    name: string;
    answers: Answer[];
}

export interface Answer {
    street: string;
    postcode: string;
}