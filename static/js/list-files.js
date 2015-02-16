// exports = window;

(function($) {
  var ListFiles = function($el) {
    this.folderId = $el.data('folder-id');
    this.listUrl = '/file/list/' + this.folderId;
    this.removeUrl = '/file/remove/';
    $el.on('click', '.remove-file', $.proxy(this.removeFile, this));
    this.$el = $('tbody', $el);
    this.el = $el[0];
  };

  ListFiles.prototype = {
    removeFile: function(e) {
      var $target = $(e.currentTarget);
      $target.prop('disabled', true);
      this.$el.addClass('disabled');
      var $this = this;
      var fileId = $target.data('file-id');
      $.post(this.removeUrl, {
        'file_id': fileId,
        'folder_id': this.folderId
      }).done(function(data) {
        Alert.show(i18n.gettext('File successfully removed.'), 'success');
        $this.render();
      }).fail(function() { Alert.show(i18n.gettext('Error removing attached file.'), 'error'); })
        .always(function() {
          $this.$el.removeClass('disabled');
          $target.prop('disabled', false);
        });
    },

    render: function(data) {
      var $this = this;
      $this.$el.empty();

      $this.$el.append('<tr><td colspan="5"><span></span>&nbsp;</td></tr>');
      var spinner = new IDSpinner({target: $('td span', $this.$el)});
      spinner.spin();

      $.get(this.listUrl).done(function(data) {
        $this.$el.empty();
        if (data.length == 0) {
          $this.$el.append('<tr><td colspan="5" class="muted">'+i18n.gettext('No files attached.')+'</td></tr>');
          return;
        }
	data.sort(function(a, b){
          var asortkey = a.title.toLowerCase();
          var bsortkey = b.title.toLowerCase();
          if (asortkey > bsortkey)
            return 1;
          if (asortkey < bsortkey)
            return -1;
          return 0;
        }
        );
        $.each(data, function(index, value) {
          value.createdDate = moment(value.createdDate).format('l'); // TODO: should use global date handling code here at some point
          value.modifiedDate = moment(value.modifiedDate).format('l');
          var template = _.template(
            '<tr>' +
            '<td><a href="{{ value.alternateLink }}"><img src="{{ value.iconLink }}"/>{{ value.title }}</a></td>' +
            '<td>{{ value.createdDate }}</td>' +
            '<td>{{ value.modifiedDate }}</td>' +
            '<td>{{ value.lastModifyingUserName }}</td>' +
            '<td><button class="btn btn-mini remove-file" data-file-id="{{ value.id }}"><i class="icon-minus-sign"></i></button></td>' +
            '</tr>'
          );
          $this.$el.append(template({value: value}));
        });
      }).fail(function() { Alert.show(i18n.gettext('Error displaying attached files.'), 'error'); })
        .always(function() { spinner.stop(); });
    }
  };

  $(document).ready(function() {
    var el = $('[data-provide=list-files]');
    if (el.length > 0) {
      var lf = new ListFiles(el);
      lf.render();
      window.ListFiles = lf;
    }
  });

})(window.jQuery);
