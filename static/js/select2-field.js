// var exports = window;

(function($) {
  var Select2Field = {};

  Select2Field.init = function() {
    $('[data-provide=select2-field]').each(function(index, el) {
      (new Select2Field.Field($(el))).render();
    });
  };

  Select2Field.Field = function($el) {
    this.$el = $el;
    this.ajaxUrl = $el.data('ajax-url');
    this.id = $el.val();
    this.text = $el.data('text');
    this.multiple = ($el.data('multiple') === 'True');

    // allow for hard-coded options to be loaded via field_id_options variable
    // taken care of by the form macro.
    this.options_field = $el.data('options');
    this.options_data = this.options_field ? window[this.options_field] : null;
  };

  Select2Field.Field.prototype = {
    render: function() {
      var $this = this;
      var opts = {
        width: '220px',
        multiple: this.multiple,
        initSelection: function(element, callback) {
          var cbdata;
          if ($this.multiple) {
            var ids = $this.id.split(',');
            var texts = $this.text.split('|');
            cbdata = new Array();
            for (var i = 0; i < ids.length; i++) {
              cbdata[i] = {id: ids[i], text: texts[i]};
            }
          } else {
            cbdata = {id: $this.id, text: $this.text};
          }
          callback(cbdata);
        }
      }

      if ($this.options_field) {
        opts['data'] = $this.options_data;
      } else {
        opts['minimumInputLength'] = 2;
        opts['ajax'] = {
          url: this.ajaxUrl,
          dataType: 'json',
          data: function(query) {
            return {
              'query': query,
              'type': 'all'
            }
          },
          results: function(data) {
            return data;
          },
          quietMillis: 1000
        };
      }

      this.$el.select2(opts);
    }
  };

  window.Select2Field = Select2Field;

})(window.jQuery);

