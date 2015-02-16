google.load('picker', '1');

(function($) {

  var DrivePicker = function($el) {
    this.$el = $el;
    this.fileIds = $el.siblings('input');
    this.type = $el.data('type');

    if ($el.data('spinner') == 'before') {
      this.spinner = new IDSpinner({before: $el});
    } else {
      this.spinner = new IDSpinner({after: $el});
    }
  };

  DrivePicker.prototype = {
    startLoading: function() {
      this.$el.prop('disabled', true);
      this.spinner.spin();
    },

    stopLoading: function() {
      this.$el.prop('disabled', false);
      this.spinner.stop();
    },

    checkOAuth: function(success_callback) {
      var $this = this;
      $this.startLoading();
      $.get('/file/upload_check/')
        .done(function(data) {
          if (data.status == 'authorize') {
            CenteredPopup.show('/file/oauth_success/', 'auth-popup', 600, 600);
          } else if (data.status == 'success') {
            success_callback(data.email_address);
          }
        })
        .always(function() {
          $this.stopLoading();
        });
    },

    createPicker: function(email_address) {
      var cb = this.type == 'form' ? this.formCallback : this.ajaxCallback;
      var upload = new google.picker.DocsUploadView();
      var picker = new google.picker.PickerBuilder()
        .enableFeature(google.picker.Feature.NAV_HIDDEN)
        .setAuthUser(email_address)
        .addView(upload)
        .setCallback($.proxy(cb, this))
        .build();
      picker.setVisible(true);
    },

    formCallback: function(data) {
      if (data.action == google.picker.Action.PICKED) {
        var selectedFiles = [];
        var selectedFilesList = this.$el.siblings('.selected-files');
        selectedFilesList.empty().show();
        var ul = $('<ul/>', {'class': 'unstyled'});
        for (var i = 0; i < data.docs.length; i++) {
          var doc = data.docs[i];
          selectedFiles.push(doc.id);
          var li = $('<li/>');
          $('<img/>', {'src': doc.iconUrl}).appendTo(li);
          $('<span/>', {'text': doc.name}).appendTo(li);
          li.appendTo(ul);
        }
        this.fileIds.val(JSON.stringify(selectedFiles));
        selectedFilesList.append(ul);
      }
    },

    ajaxCallback: function(data) {
      if (data.action == google.picker.Action.PICKED) {
        var $this = this;
        var key = this.$el.data('key');
        var firstFile = $('.list-files').length == 0;
        var selectedFiles = [];
        for (var i = 0; i < data.docs.length; i++) {
          selectedFiles.push(data.docs[i].id);
        }
        var fileIds = JSON.stringify(selectedFiles);
        $this.startLoading();
        $.post('/file/upload/', {
          file_ids: fileIds,
          key: key,
          first_file: firstFile
        }).done(function(data) {
          if (firstFile) {
            window.location.reload();
          } else {
            Alert.show(i18n.gettext('File(s) successfully attached.'), 'success');
            window.ListFiles.render();
          }
        }).fail(function() { Alert.show(i18n.gettext('Error attaching file(s).'), 'error'); })
          .always(function() {
            $this.stopLoading();
          });
      }
    }
  };

  $(document).on('click.drive-picker.data-api', '[data-toggle=drive-picker]', function(e) {
    // Check for OAuth credentials and show drive picker if they are valid
    var dp = new DrivePicker($(this));
    dp.checkOAuth(function(email_address) {
      dp.createPicker(email_address);
    });
  });

})(window.jQuery);

