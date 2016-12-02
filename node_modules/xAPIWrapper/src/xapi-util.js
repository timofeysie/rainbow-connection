var getObjDefName = function (o) {
    if (o.definition && o.definition.name) {
        return xapiutil.getLangVal(o.definition.name);
    }
    return undefined;
};

var getSubStatementDisplay = function (o) {
    if (o.objectType !== "SubStatement") return;
    if (o.object.objectType === "SubStatement") return;
    if (o.id || o.stored || o.version || o.authority) return;
    var disp = xapiutil.getActorId(o.actor) + ":" + xapiutil.getVerbDisplay(o.verb) + ":" + xapiutil.getObjectId(o.object);
    return disp;
};


var xapiutil = {};

xapiutil.getLang = function () {
    var lang;
    if (typeof navigator !== 'undefined')
        lang = navigator.language || navigator.browserLanguage ||
            navigator.systemLanguage || navigator.userLanguage;
    else if (process && process.env) {
        var str = process.env.LANG;
        lang = str.slice(0, str.indexOf('.'));
        lang = lang.replace(/_/, '-')
    }
    return lang || "en-US";
};

xapiutil.getLangVal = function (langprop) {

    if (!langprop) return;

    var options = Object.keys(langprop);
    // test that langprop is a dict (obj)
    // skips if not a dict(obj) and returns
    if (options.length == 0) return undefined;

    var lang = xapiutil.getLang(),
        ret,
        dispGotten = false;

    do {    //test and retest
        if (langprop[lang]) {
            ret = langprop[lang];
            dispGotten = true;
        }
        else if (lang.indexOf('-')) {
            lang = lang.substring(0, lang.lastIndexOf('-'));
        }
    } while (!dispGotten && lang !== "");

    return ret;
};

xapiutil.getMoreStatements = function (iterations, callback, searchParams) {

    var stmts = [];

    ADL.XAPIWrapper.getStatements(searchParams, null, function getMore(r) {
        if (!(r && r.response)) return;
        var res = JSON.parse(r.response);
        if (!res.statements) return;
        stmts = stmts.concat(res.statements);

        if (iterations-- <= 0) {
            callback(stmts);
        }
        else {
            if (res.more && res.more !== "") {
                ADL.XAPIWrapper.getStatements(searchParams, res.more, getMore);
            }
            else if (res.more === "") {
                callback(stmts);
            }
        }
    });
};

xapiutil.getActorId = function (a) {
    return a.mbox || a.openid || a.mbox_sha1sum || a.account;
};

xapiutil.getActorIdString = function (a) {
    var id = a.mbox || a.openid || a.mbox_sha1sum;
    if (!id) {
        if (a.account) id = a.account.homePage + ":" + a.account.name;
        else if (a.member) id = "Anon Group " + a.member;
        else id = 'unknown';
    }
    return id;
};

xapiutil.getActorDisplay = function (a) {
    return a.name || xapiutil.getActorIdString(a);
};

xapiutil.getVerbDisplay = function (v) {
    if (!v) return;
    if (v.display) {
        return xapiutil.getLangVal(v.display) || v.id;
    }
    return v.id;
};

xapiutil.getObjectType = function (o) {
    return o.objectType || ((o.id) ? "Activity" : "Agent");
};

xapiutil.getObjectId = function (o) {
    if (o.id) return o.id;
    var type = xapiutil.getObjectType(o);
    if (type === "Agent" || type === "Group") return xapiutil.getActorId(o);
    return undefined;
};

xapiutil.getObjectIdString = function (o) {
    if (!o) return 'unknown'
    if (o.id) return o.id;
    var type = xapiutil.getObjectType(o);
    if (type === "Agent" || type === "Group") return xapiutil.getActorIdString(o);
    else if (type == "SubStatement") {
        return getSubStatementDisplay(o);
    }
    return 'unknown';
};

xapiutil.getObjectDisplay = function (o) {
    if (!o) return "unknown"
    var disp = getObjDefName(o) || o.name || o.id;
    if (!disp) {
        var type = xapiutil.getObjectType(o);
        if (type === "Agent" || type == "Group") disp = xapiutil.getActorDisplay(o);
        else if (type == "SubStatement") {
            disp = getSubStatementDisplay(o);
        }
    }

    return disp;
};

module.exports = xapiutil;