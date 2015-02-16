/**
 * Based off the django i18n JS.
 *
 * The catalog is meant to be registered in the head of the page, rendered
 * by the server as json.
 */
(function (globals) {

  var i18n = globals.i18n || (globals.i18n = {});

  i18n.pluralidx = function (n) {
    var v=i18n.plural(n);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };

  /* gettext library */
  
  if (typeof(i18n.catalog) === "undefined") {
    i18n.catalog = {};
  }

  i18n.gettext = function (msgid) {
    var value = i18n.catalog[msgid];
    if (typeof(value) == 'undefined') {
      return msgid;
    } else {
      return (typeof(value) == 'string') ? value : value[0];
    }
  };

  i18n.ngettext = function (singular, plural, count) {
    value = i18n.catalog[singular];
    if (typeof(value) == 'undefined') {
      return (count == 1) ? singular : plural;
    } else {
      return value[i18n.pluralidx(count)];
    }
  };

  i18n.gettext_noop = function (msgid) { return msgid; };

  i18n.pgettext = function (context, msgid) {
    var value = i18n.gettext(context + '\x04' + msgid);
    if (value.indexOf('\x04') != -1) {
      value = msgid;
    }
    return value;
  };

  i18n.npgettext = function (context, singular, plural, count) {
    var value = i18n.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
    if (value.indexOf('\x04') != -1) {
      value = i18n.ngettext(singular, plural, count);
    }
    return value;
  };

  i18n.interpolate = function (fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  };


  /* add to global namespace */
  globals.pluralidx = i18n.pluralidx;
  globals.gettext = i18n.gettext;
  globals.ngettext = i18n.ngettext;
  globals.gettext_noop = i18n.gettext_noop;
  globals.pgettext = i18n.pgettext;
  globals.npgettext = i18n.npgettext;
  globals.interpolate = i18n.interpolate;

}(this));
