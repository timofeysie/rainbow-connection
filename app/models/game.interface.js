"use strict";
var QuestionObject = (function () {
    function QuestionObject(name, answers) {
        this.name = name;
        this.answers = answers;
    }
    return QuestionObject;
}());
exports.QuestionObject = QuestionObject;
var AnswerObject = (function () {
    function AnswerObject(answerText, correct) {
        this.answerText = answerText;
        this.correct = correct;
    }
    return AnswerObject;
}());
exports.AnswerObject = AnswerObject;
//# sourceMappingURL=game.interface.js.map