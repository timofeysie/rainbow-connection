var util, s1, s2, s3, s4, s5, s6, onBrowser, should, stmts, wrapper, ADL;

before(function () {
    onBrowser = false;
    if (typeof window !== 'undefined') {
        util = ADL.xapiutil;
        onBrowser = true;
        stmts = ADL.stmts;
        wrapper = ADL.XAPIWrapper;
    }
    else {
        should = require('should');
        ADL = require('../../src/');
    }

    s1 = {
        "actor": {
            "mbox": "mailto:tom@tom.com",
            "openid": "openid",
            "mbox_sha1sum": "mbox_sha1sum",
            "account": "wrapperTesting"
        },
        "verb": {"id": "http://verb.com/do1"},
        "object": {
            "id": "http://from.tom/act1",
            "objectType": "StatementRef",
            "definition": {"name": {"en-US": "soccer", "fr": "football", "de": "foossball"}}
        }
    };

    s2 = {
        "actor": {"openid": "openid", "mbox_sha1sum": "mbox_sha1sum", "account": "wrapperTesting", "name": "joe"},
        "verb": {
            "id": "http://verb.com/do2",
            "display": {"fr": "recommander", "de": "empfehlen", "es": "recomendar", "en": "recommend"}
        },
        "object": {"objectType": "Agent", "mbox": "mailto:joe@mail.com"}
    };

    s3 = {
        "actor": {"mbox_sha1sum": "randomstringthatmakesnosensembox_sha1sum", "account": "wrapperTesting"},
        "verb": {"id": "http://verb.com/do3"},
        "object": {
            "objectType": "Group",
            'notid': "http://from.tom/act3",
            "member": ["joe"],
            "name": "obiwan",
            "mbox_sha1sum": "randomstringthatmakesnosensembox_sha1sum"
        }
    };

    s4 = {
        "actor": {"account": {"homePage": 'http://adlnet.gov/test', "name": "wrapperTesting"}},
        "verb": {"id": "http://verb.com/do4", "display": {"en-US": "initialized"}},
        "object": {
            "notid": "http://from.tom/act4",
            "objectType": "SubStatement",
            "actor": {"mbox_sha1sum": "randomstringthatmakesnosensembox_sha1sum", "account": "wrapperTesting"},
            "verb": {"id": "http://verb.com/do3"},
            "object": {
                "objectType": "Group",
                "notid": "http://from.tom/act3",
                "member": ["joe"],
                "mbox_sha1sum": "randomstringthatmakesnosensembox_sha1sum"
            }
        }
    };

    s5 = {
        "actor": {"member": ["joe"], "objectType": "Group"},
        "verb": {"id": "http://verb.com/do5"},
        "object": {"id": "http://from.tom/act5"}
    };

    s6 = {
        "actor": {"some": "thing else"},
        "verb": {"id": "http://verb.com/do6", "display": {"fr": "établi", "de": "etabliert"}},
        "object": {"some": 'thing else'}
    };
});

describe("wrapper should work as a require JS module", function () {
    it("xAPIWrapper", function () {
        ADL.XAPIWrapper.should.have.property("changeConfig").which.is.a.function;
        ADL.XAPIWrapper.should.have.property("changeConfig");
    })

    it("XAPIStatement", function(){

    })

    it("verbs", function(){

    })

})
