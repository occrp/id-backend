// var exports = window;

(function($) {
  var IDSpinner = function(options) {
    this.options = options;
    this.spinner = new Spinner({
      lines: 9,
      length: 4,
      width: 4,
      radius: 5,
      trail: 40,
      hwaccel: true,
      top: '2px',
      left: '2px'
    });
  };

  IDSpinner.prototype = {
    insertContainer: function() {
      this.target = $('<span/>', {'class': 'id-spinner'});
      if (this.options.before) {
        this.options.before.before(this.target);
      } else if (this.options.after) {
        this.options.after.after(this.target);
      } else if (this.options.target) {
        this.target = this.options.target;
      }
    },

    spin: function() {
      this.insertContainer();
      this.spinner.spin(this.target[0]);
    },

    stop: function() {
      this.spinner.stop();
      this.target.remove();
    }
  };

  var Alert = {};

  Alert.show = function(msg, type, target, parent) {
    target = target ? target : $('#alerts');
    parent = parent ? parent : $('body');

    var template = _.template(
    '<div class="alert alert-block alert-' + type + '">' +
    '<a class="close" data-dismiss="alert">×</a>' + msg +
    '</div>'
    );
    target.empty();
    target.append(template());
    parent.scrollTop(0);
  };

  var CenteredPopup = {};

  CenteredPopup.show = function(url, title, w, h) {
    // Fixes dual-screen position                       Most browsers      Firefox
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    var left = ((screen.width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((screen.height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open(url, title, 'scrollbars=yes, width=' + w +
      ', height=' + h + ', top=' + top + ', left=' + left);

    // Puts focus on the newWindow
    if (window.focus) {
      newWindow.focus();
    }
  };

  var separator = "\t";
  var lineSplitter = '\n';

  /**
   * A multi-widget container which maps a multi-line text area field
   * into user-friendly textboxes and dropdowns.
   *
   * Provides a mechanism to write back and forth between the backend
   * textarea field to keep in sync.
   *
   * @param options Object
   *  {
   *    textarea: $Element,
   *    widgetType: CustomWidget
   *  }
   */
  var MultiWidgetContainer = function MultiWidgetContainer(options) {

    if (!options.textarea || options.textarea.length == 0 || !options.widgetType) {
      // bail early if options aren't properly provided.
      return;
    }

    this.textarea = options.textarea;
    this.base = this.textarea.parent();
    this.base.addClass('multiwidgetcontainer');

    this.widgetType = options.widgetType;
    this.widgets = [];

    // hide the original textarea, and use it as the backend.
    this.textarea.hide();

    // initialize the widget with a single new option.
    _.each(this.fromTextArea(), _.bind(function initWidgets(initial) {
      this.add(new this.widgetType(initial));
    }, this));

    this.base.on('keyup change', this.keyUpHandler());
    this.base.on('click', '.act-add', this.addHandler());

  };

  /**
   * Generates a click handler to add widgets to the container
   */
  MultiWidgetContainer.prototype.addHandler = function addHandler() {
    var add = function add(ev) {
      this.add(new this.widgetType());
    };
    return _.bind(add, this);
  };

  /**
   * Generates a key up handler which is properly scoped and debounced.
   */
  MultiWidgetContainer.prototype.keyUpHandler = function keyUpHandler(){
    var keyUp = _.debounce(function keyUp(ev) {
      this.toTextArea();
    }, 250);
    return _.bind(keyUp, this);
  };

  /**
   * Adds a new widget to the container
   * and moves the plus button to the new widget.
   */
  MultiWidgetContainer.prototype.add = function add(widget) {
    // console.log("Junk!", widget);
    // this.widgets.push(widget);
    var newwidgets = widget.render();
    this.base.append(newwidgets);
    this.base.find('.act-add').remove();
    this.base.append($('<button type="button" class="btn act-add"><i class="fa fa-plus"></i></button>'));
  };

  /**
   * Flushes all of the widget values to the backend text area.
   */
  MultiWidgetContainer.prototype.toTextArea = function toTextArea() {
    var allValues = _.map(this.widgets, function valuesMap(widget) {
      return widget.val();
    });
    this.textarea.val(allValues.join(lineSplitter));
  };

  /**
   * Reads in the backend text area value to be used when initializing
   * the field.
   */
  MultiWidgetContainer.prototype.fromTextArea = function fromTextArea() {
    var raw = this.textarea.val();
    return raw.split(lineSplitter);
  };


  /**
   * Names Widget!
   * <last name> <other names>
   */
  var NamesWidget = function NamesWidget(initial){
    var splitUp = typeof(initial) !== "undefined" ? initial.split(separator) : [""];
    this.initial = {
      lname: splitUp[0],
      other: splitUp.length > 0 ? splitUp[1] : ''
    };
    this.base = $('<div/>').addClass('widget');
  };

  /**
   * @return Element to be appended to the container.
   */
  NamesWidget.prototype.render = function render(){
    this.base.empty();

    var lname = $('<input type="text" class="lastname" placeholder="' + i18n.gettext('Last Name') + '" />');
    var other = $('<input type="text" class="othername" placeholder="' + i18n.gettext('First/Other Names') + '" />');
    var minus = $('<button type="button" class="btn act-remove"><i class="fa fa-minus"></i></button>');
    var base = this.base;
    minus.on("click", function() { base.remove(); });

    lname.val(this.initial.lname);
    other.val(this.initial.other);

    this.base.append(lname);
    this.base.append(other);
    this.base.append(minus);

    return this.base;
  };

  /**
   * @return String final rendered value for the widget.
   */
  NamesWidget.prototype.val = function val() {
    return [
      this.base.find('input.lastname').val(),
      this.base.find('input.othername').val()].join(separator);
  };

  /**
   * Relations Widget!
   * <last name> <other names> <relation>
   */
  var RelationWidget = function RelationWidget(initial){
    var splitUp = typeof(initial) !== "undefined" ? initial.split(separator) : [""];
    this.initial = {
      lname: splitUp[0],
      other: splitUp.length > 0 ? splitUp[1] : '',
      relation: splitUp.length > 1 ? splitUp[2] : ''
    };

    this.base = $('<div/>').addClass('widget');
  };

  /**
   * @return Element to be appended to the container.
   */
  RelationWidget.prototype.render = function render(){
    this.base.empty();

    var lname = $('<input type="text" class="lastname" placeholder="' + i18n.gettext('Last Name') + '" />');
    var other = $('<input type="text" class="othername" placeholder="' + i18n.gettext('First/Other Names') + '" />');
    var sel2 = $('<select class="relation"><select>');

    // hard coded relations for now for expediency
    // ripped from the mockup that Dan provided.
    sel2.html('<option value="parent">Parent</option><option value="spouse">Spouse</option><option value="relative">Other Relative</option><option value="friend">Friend or Acquaintance</option><option value="employer">Employer</option><option value="partner">Business Partner</option><option value="proxy">Proxy</option><option value="director">Director</option><option value="secretary">Secretary</option><option value="authorized">Authorized Person</option><option value="representative">Representative</option><option value="shareholder">Shareholder</option><option value="employee">Employee</option><option value="born">Born In</option><option value="registered">Registered Address</option><option value="home">Home Address</option><option value="subsidiary">Subsidiary</option><option value="partner">Trading Partner</option><option value="registered">Registered Address</option><option value="place">Place of Business</option><option value="other">Other</option>');

    lname.val(this.initial.lname);
    other.val(this.initial.other);
    sel2.val(this.initial.relation);

    this.base.append(lname);
    this.base.append(other);

    this.base.append(sel2);
    sel2.select2({width: '220px'});

    return this.base;
  };

  /**
   * @return String final rendered value for the widget.
   */
  RelationWidget.prototype.val = function val(){
    return [
      this.base.find('input.lastname').val(),
      this.base.find('input.othername').val(),
      this.base.find('.relation').select2('val')].join(separator);
  };


  // aliases (last name, other names)
  var aliasesWidget = new MultiWidgetContainer({
    textarea: $('textarea[name="person-aliases"]'),
    widgetType: NamesWidget
  });

  // sources (last name, other names)
  var sourcesWidget = new MultiWidgetContainer({
    textarea: $('textarea[name="company-connections"]'),
    widgetType: NamesWidget
  });

  // family (last name, other names, dropdown)
  var familyWidget = new MultiWidgetContainer({
    textarea: $('textarea[name="person-family"]'),
    widgetType: RelationWidget
  });

  window.IDSpinner = IDSpinner;
  window.Alert = Alert;
  window.CenteredPopup = CenteredPopup;

})(window.jQuery);
