/*
 * general utility stuff
 */

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

String.prototype.truncate =
    function(n){
        var p  = new RegExp("^.{0," + n + "}[\\S]*", 'g');
        var re = this.match(p);
        var l  = re[0].length;
        var re = re[0].replace(/\s$/,'');

        if (l < this.length) return re + '&hellip;';
        return this;
    };

function filesizeformat(fileSizeInBytes) {
    // Purloined from http://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
    do {
        fileSizeInBytes = fileSizeInBytes / 1024;
        i++;
    } while (fileSizeInBytes > 1024);

    return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
};


/*
 * general ID2 podaci stuff
 */

var ID2 = ID2 || {};
ID2.Podaci = {};

ID2.Podaci.init = function() {
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    for (cb in ID2.Podaci.callbacks) {
        var item = cb.split(" ");
        var event = item.pop();
        var selector = item.join(" ");
        $(selector).on(event, ID2.Podaci.callbacks[cb]);
    }

    ID2.Podaci.current_files = [];
    ID2.Podaci.selection = [];
    ID2.Podaci.update_selection();
    ID2.Podaci.query = '';
    ID2.Podaci.search("");
    ID2.Podaci.update_collections();

    ID2.Podaci.init_fileupload();
};


/*
 * search
 */

ID2.Podaci.search = function(q) {
    ID2.Podaci.results_clear();
    var ticketId = $('#podaci-ticket-id').val(),
        query = q + ' ';
    if (ticketId && ticketId.length) {
      query = query + 'ticket:' + ticketId;
    }
    console.log("Searching:", query, ticketId);
    $.getJSON("/podaci/search/", {"q": query}, function(data) {
        ID2.Podaci.query = q;
        for (i in data.results) {
            file = data.results[i];
            ID2.Podaci.add_file_to_results(file);
        }
    });
};

ID2.Podaci.searchbox_keyup = function(e) {
    var code = (e.keyCode ? e.keyCode : e.which);
    if (ID2.Podaci.searchbox_timer) {
        clearTimeout(ID2.Podaci.searchbox_timer);
    }
    if (code == 13) {
        ID2.Podaci.trigger_search();
    } else {
        ID2.Podaci.searchbox_timer = setTimeout(ID2.Podaci.trigger_search, 2000);
    }
}

ID2.Podaci.trigger_search = function() {
    q = $("#searchbox").val();
    ID2.Podaci.search(q);
}

ID2.Podaci.get_file_list = function() {
    ID2.Podaci.results_clear();
    $.getJSON("/podaci/file/", function(data) {
        for (i in data.results) {
            file = data.results[i];
            ID2.Podaci.add_file_to_results(file);
        }
    });
}

ID2.Podaci.results_clear = function() {
    $("#podaci-file-list").empty();
    ID2.Podaci.current_files = [];
}

ID2.Podaci.render_resultset = function() {
    for (f in ID2.Podaci.current_files) {
        ID2.Podaci.render_file_to_resultset(ID2.Podaci.current_files[f]);
    }
}

ID2.Podaci.add_file_to_results = function(file) {
    ID2.Podaci.current_files.push(file);
    ID2.Podaci.render_file_to_resultset(file);
}

ID2.Podaci.render_file_to_resultset = function(file) {
    var tags = $("<span>");
    tags.addClass("podaci-tags");
    for (tag in file.tags) {
        tag = file.tags[tag];
        tags.append("<a data-tag=\"" + tag + "\">" + tag + "</a>");
    }

    var filename = $("<a class=\"podaci-filename\">" + (file.title || file.filename) + "</a>");
    filename.click(ID2.Podaci.file_doubleclick);
    filename.attr("data-id", file.id);

    var selectbar = $("<div class=\"podaci-selectbar\">");
    selectbar.mousedown(ID2.Podaci.file_click);

    var thumbnail = $("<img src=\"" + file.thumbnail + "\" class=\"podaci-file-thumbnail\"/>");
    thumbnail.click(ID2.Podaci.file_click);

    var fo = $("<div>");
    fo.addClass("podaci-file");
    fo.append(selectbar);
    fo.append(thumbnail);
    fo.append("<span class=\"podaci-filesize\">" + filesizeformat(file.size) + "</span>");

    if (file.mimetype) {
      var mimeinfo = $("<a data-mimetype=\"" + file.mimetype + "\" class=\"podaci-filetype\">" + file.mimetype.split("/")[1].toUpperCase() + "</a>");
      mimeinfo.click(function() { ID2.Podaci.search_term_add("mime:" + file.mimetype); });
      fo.append(mimeinfo);
    }

    fo.append(filename);
    fo.append(tags);
    fo.append("<div class=\"podaci-description\">" + file.description.truncate(200) + "</div>")
    fo.attr("data-id", file.id);
    fo.attr("data-file", JSON.stringify(file));

    if (file.public_read) {
        fo.append("<div class=\"podaci-file-public\">Public</div>");
    }
    if (file.staff_read) {
        fo.append("<div class=\"podaci-file-staff\">OCCRP Staff Access</div>");
    }

    fo.attr("draggable", true);
    fo.on("dragstart", ID2.Podaci.selection_drag);
    fo.on("click", ".podaci-tags a", ID2.Podaci.tag_click);
    $("#podaci-file-list").append(fo);
}

ID2.Podaci.search_term_add = function(term) {
    var v = $("#searchbox").val();
    v += " " + term;
    $("#searchbox").val(v);
    ID2.Podaci.trigger_search();
};

ID2.Podaci.search_term_remove = function(term) {
    var v = $("#searchbox").val();
    v = v.replace(" " + term, "");
    $("#searchbox").val(v);
    ID2.Podaci.trigger_search();
};

ID2.Podaci.search_term_toggle = function(term) {
  var terms = $("#searchbox").val().split(' ');
  if (terms.indexOf(term) == -1) {
    ID2.Podaci.search_term_add(term);
  } else {
    ID2.Podaci.search_term_remove(term);
  }
};


/*
 * collections support
 */

ID2.Podaci.update_collections = function() {
    $.getJSON("/podaci/collection/", function(data) {
        $("#mycollections").empty();
        for (collection in data.results) {
            ID2.Podaci.add_collection(data.results[collection]);
        }
    });
};

ID2.Podaci.add_collection = function(collection, targetli) {
    var col = $("<a data-collectionid=\"" + collection.id + "\" data-collection=\"" + collection.name.replace(" ", "_") + "\"><i class=\"fa fa-folder\"></i> " + collection.name + "<span class=\"pull-right badge\">" + collection.files.length + "</span></a>");
    col.click(ID2.Podaci.collection_filter_click);
    if (targetli) {
        colli = targetli;
        colli.empty();
    } else {
        colli = $("<li>");
    }
    colli.append(col);
    col.on("dragover", function(e) {
        e.preventDefault();
        col.addClass("drop-on-me");
    });
    col.on("dragleave", function(e) {
        e.preventDefault();
        col.removeClass("drop-on-me");
    })
    col.on("drop", ID2.Podaci.selection_drop);
    if (!targetli) {
        $("#mycollections").append(colli);
    }
}


ID2.Podaci.collection_filter_click = function(e) {
    collectionid = $(e.target).data("collection");
    e.preventDefault();
    e.stopPropagation();
    ID2.Podaci.select_none()
    if ($(e.target).hasClass("selected")) {
        $(e.target).removeClass("selected");
        ID2.Podaci.search_term_remove("in:" + collectionid);
    } else {
        $(e.target).addClass("selected");
        ID2.Podaci.search_term_add("in:" + collectionid);
    }

}


ID2.Podaci.update_selection = function() {
    var not_selected = _.difference(
        $.map($(".podaci-file"), function(e) { return $(e).data("id") },
        ID2.Podaci.selection));

    for (idx in not_selected) { // It might be faster to just apply this to $(".podaci-file"), without a loop?
        $(".podaci-file[data-id='" + not_selected[idx] + "']").removeClass("podaci-file-selected");
    }
    for (idx in ID2.Podaci.selection) {
        $(".podaci-file[data-id='" + ID2.Podaci.selection[idx] + "']").addClass("podaci-file-selected");
    }

    if (ID2.Podaci.selection.length == 0 && not_selected.length == 0) {
        $("#podaci_selection_menu").html("No files <span class=\"caret\"></span>");
        // $("#podaci_selection_menu")
    } else if (ID2.Podaci.selection.length == 0) {
        $("#podaci_selection_menu").html("All files <span class=\"caret\"></span>");
    } else {
        $("#podaci_selection_menu").html("Selection (" + ID2.Podaci.selection.length + ") <span class=\"caret\"></span>");
    }
};




ID2.Podaci.create_collection_submit = function() {
    $.post('/podaci/collection/', $("#podaci_create_collection_form").serialize(),
            function(data) {
        $("#podaci_create_collection_modal").modal("hide");
        ID2.Podaci.add_collection(data);
    }).fail(function(data) {
        console.log("ERROR: ", data);
        if (data.responseJSON.non_field_errors[0] == "The fields name, owner must make a unique set.") {
            $("#podaci_create_collection_error").html("You already have a collection with this name.");
            $("#podaci_create_collection_error").show();
        }

    });
};


/*
 * selecting and deselecting
 */

ID2.Podaci.select = function(selection) {
    ID2.Podaci.selection = _.union(ID2.Podaci.selection, selection);
    console.log(selection)
    ID2.Podaci.update_selection();
};


ID2.Podaci.deselect = function(selection) {
    ID2.Podaci.selection = _.difference(ID2.Podaci.selection, selection);
    ID2.Podaci.update_selection();
};


ID2.Podaci.select_toggle = function(id) {
    if (ID2.Podaci.selection.indexOf(id) == -1) {
        ID2.Podaci.select([id]);
    } else {
        ID2.Podaci.deselect([id]);
    }
};


ID2.Podaci.select_invert = function() {
    ID2.Podaci.selection = _.difference(
        $.map($(".podaci-file"), function(e) { return $(e).data("id") }),
        ID2.Podaci.selection);
    ID2.Podaci.update_selection();
};


ID2.Podaci.select_all = function() {
    ID2.Podaci.selection = $.map($(".podaci-file"), function(e) { return $(e).data("id") });
    ID2.Podaci.update_selection();
};


ID2.Podaci.select_none = function() {
    ID2.Podaci.selection = [];
    ID2.Podaci.update_selection();
};


ID2.Podaci.select_toggle_checkbox = function(e) {
    id = $(e.target).parent().parent().data("id");
    ID2.Podaci.select_toggle(id);
}


/*
 * drag and drop dead
 */

ID2.Podaci.selection_drag = function(e) {
    // ...
    ID2.Podaci.select([parseInt($(e.currentTarget).attr('data-id'))])
    ID2.Podaci.internal_drag = true; // TODO: make sure this flag gets cleared always when needed!
};

ID2.Podaci.selection_drop = function(e) {
    e.preventDefault();
    ID2.Podaci.internal_drag = false;
    $(e.target).removeClass("drop-on-me");
    var targetli = $(e.target).closest("li");
    var id = $(e.target).data("collectionid")
    $.ajax("/podaci/collection/" + id + "/", {
        type: "PATCH",
        data: {"add_files": ID2.Podaci.selection}
    }).done(function(data) {
        ID2.Podaci.add_collection(data, targetli);
        console.log(data);
        ID2.Podaci.select_none()
    }).fail(function(data) {
        console.log(data);
    });
};


/*
 * file upload
 */

ID2.Podaci.init_fileupload = function() {
    var col = $('#podaci-file-list-container'),
        progressbar = $('.podaci_upload_progress'),
        files_form = $('.podaci_upload_files_form');
    ID2.Podaci.results_cache = [];

    $('.podaci_upload_tickets').val($('#podaci-ticket-id').val());

    col.on("dragover", function(e) {
        e.preventDefault();
        if (!ID2.Podaci.internal_drag) {
            col.addClass("dropzone");
        }
        //col.children('#podaci-file-list').empty();
    });

    col.on("dragleave", function(e) {
        e.preventDefault();
        col.removeClass("dropzone");
        //ID2.Podaci.render_resultset();
    });

    col.children('.dropzone-to-be').on("drop", function(e) {
        ID2.Podaci.results_clear();
        col.removeClass("dropzone");
    });

    $('.podaci_upload_files').fileupload({
        url: '/podaci/file/create/',
        dataType: 'json',
        done: function (e, data) {
            setTimeout(ID2.Podaci.refresh_files, 300);
        },
        dropzone: $("#podaci-file-list-container > .dropzone-to-be"),
        disableImageResize: /Android(?!.*Chrome)|Opera/
            .test(window.navigator.userAgent),

    }).on('fileuploadadd', function (e, data) {
        progressbar.show();
        files_form.hide();
        data.context = $('#podaci_upload_list');
        $.each(data.files, function (index, file) {
            var node = $('<tr class="podaci-file podaci-file-pending"/>');
            var linkcolumn = node.append('<td/>')
            linkcolumn.append('<a>'+file.name+'</a>');
        });

    }).on('fileuploadprocessalways', function (e, data) {
        console.log("fileuploadprocessalways");
        var index = data.index,
            file = data.files[index],
            node = $(data.context.children()[index]);
        if (file.preview) {
            node
                .prepend('<br>')
                .prepend(file.preview);
        }
        if (file.error) {
            node
                .append('<br>')
                .append($('<span class="text-danger"/>').text(file.error));
        }
        if (index + 1 === data.files.length) {
            data.context.find('button')
                .text('Upload')
                .prop('disabled', !!data.files.error);
        }

    }).on('fileuploadprogressall', function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        progressbar.find('.progress-bar').css('width', progress + '%');

    }).on('fileuploaddone', function (e, data) {
        ID2.Podaci.add_file_to_results(data.result);
        progressbar.hide();
        $("#podaci_upload_modal").modal('hide');
        $("#podaci_add_modal").modal('hide');
        files_form.show();

        // ticket pages with no files need to be reloaded to show file list:
        //if($("#podaci-file-list").length == 0) {
        //  document.location.reload();
        //}

    }).on('fileuploadfail', function (e, data) {
        // FIXME: Test failure modes. Make this pretty.
        progressbar.hide();
        files_form.show();
    });
};


ID2.Podaci.upload_click = function(e, target) {
  $('.podaci_upload_progress').hide()
  $("#podaci_upload_modal").modal();
};


ID2.Podaci.ticket_add_file = function(event) {
  // var ticketId = $(event.target).data('ticket');
  $('.podaci_upload_progress').hide();
  $("#podaci_add_modal").modal();
};


ID2.Podaci.edit_users = function() {
    $("#podaci_edit_users_modal").modal();
    $("#podaci_edit_users_add_user").select2({
        ajax: {
            url: $(this).data('url'),
        }
    });
};


/*
 * tags
 */

ID2.Podaci.tag_click = function(event) {
  ID2.Podaci.search_term_toggle('#' + $(this).data('tag'));
};


ID2.Podaci.get_selected_tags = function() {
    // console.log(ID2.Podaci);
    var selected = null;
    $(".podaci-file").each(function(index, el) {
      var $el = $(el),
          tags = [];
      if (ID2.Podaci.selection.indexOf($el.data('id')) != -1) {
        var file = $el.data('file');
        if (selected === null) {
          selected = file.tags;
        } else {
          selected = _.intersection(selected, file.tags);
        }
      }

    });
    return selected;
};

ID2.Podaci.edit_tags = function() {
    $("#podaci_edit_tags_modal").modal();
    var $input = $("#podaci_edit_tags_input");
    var common = ID2.Podaci.get_selected_tags();
    $input.select2({
      tags: true,
      data: common,
      tokenSeparators: [',', ' ']
    });
    $input.val(common).trigger("change");
};


ID2.Podaci.edit_tags_submit = function() {
    var tags = $("#podaci_edit_tags_input").val(),
        common = ID2.Podaci.get_selected_tags(),
        added = _.without(tags, common),
        removed = _.without(common, tags);
    // console.log('VALUES', tags, common, added, removed);

    $(".podaci-file").each(function(index, el) {
      var $el = $(el),
          $tags = $el.find(".podaci-tags");
      if (ID2.Podaci.selection.indexOf($el.data('id')) != -1) {
        var file = $el.data('file'),
            tags = [];
        $.each(added, function(i, t) {
          tags.push(t);
        });
        $.each(file.tags, function(i, t) {
          if (removed.indexOf(t.name) == -1 &&
              added.indexOf(t.name) == -1) {
            tags.push(t);
          }
        });
        file.tags = _.uniq(tags);
        $.ajax({
          type: 'PUT',
          url: '/podaci/file/' + file.id + '/',
          data: JSON.stringify(file),
          contentType: 'application/json',
          dataType: 'json',
          success: function(file_ret) {
            console.log(file_ret);
          }
        });
        $tags.empty()
        for (tag in file.tags) {
          tag = file.tags[tag];
          $tags.append("<a data-tag=\"" + tag + "\">" + tag + "</a>");
        }
      }
    });
    $("#podaci_edit_tags_modal").modal('hide');
};


ID2.Podaci.refresh_files = function() {
    // FIXME: This currently fetches tag info, but discards it.
    //        We should opportunistically update the tag sets
    //        since we have the data anyway.
    // FIXME: This currently does one database hit per .podaci-files
    //        entry in the document. That is smart if there are many
    //        with different views, but is stupid if there is more
    //        than one with the same view.
    console.log("Refreshing...");
    $(".podaci-files").each(function(index, el) {
        var tag = $(el).data("tag");
        if (tag == undefined || tag == null || tag == "") {
            console.log("No tag, so no action.");
            return;
        } else {
            console.log("Refreshing files on ", el);
            url = "/podaci/tag/" + tag + "/";
        }
        $.getJSON(url, {"format": "json"}, function(data) {
            console.log("Got data: ", data);
            if (!data || data.error) {
                Alert.show(data.error, 'error', $('#alerts'), $('body'));
            } else {
                if ($(el).hasClass("podaci-files-list")) {
                    el = $(el).find("tbody");
                    $(el).empty();
                    for (index in data.result_files) {
                        file = data.result_files[index];
                        var tr = $('<tr class="podaci-file"/>');
                        tr.data("mime", file.meta.mimetype);
                        tr.data("size", file.meta.size);
                        tr.data("id", file.meta.id);
                        tr.data("tags", file.meta.tags);
                        $(el).append(tr);

                        tr.append($('<td><input type="checkbox" class="podaci_file_select_box"/></td>'));

                        var td = $("<td nowrap/>");
                        var a = $("<a/>");
                        a.attr("href", "/podaci/podaci/file/" + file.id + "/");
                        a.text(file.meta.identifier);
                        td.append(a);
                        tr.append(td);

                        td = $("<td nowrap/>");
                        a = $("<a/>");
                        a.attr("href", "/podaci/file/" + file.id + "/");
                        a.html('<i class="icon-file"></i>' + file.meta.filename);
                        td.append(a);
                        td.addClass("overflow-hidden");
                        tr.append(td);

                        tr.append($('<td nowrap style="text-align: right;">'+ filesizeformat(file.meta.size) + '</td>'));
                        tr.append($('<td nowrap>'+ file.meta.mimetype + '</td>'));
                    }
                } else {
                    $(el).empty();
                    for (index in data.result_files) {
                        file = data.result_files[index];
                        var li = $('<li class="podaci-file"/>');
                        li.data("mime", file.meta.mimetype);
                        li.data("size", file.meta.size);
                        li.data("id", file.meta.id);
                        li.data("tags", file.meta.tags);
                        $(el).append(li);
                        var a = $("<a/>");
                        a.attr("href", "/podaci/podaci/file/" + file.id + "/");
                        a.html('<i class="icon-file podaci-icon-big"></i>' + file.meta.filename);
                        li.append(a);
                    }
                }

            }
        });
    });
};

ID2.Podaci.download_zip = function() {
    if (ID2.Podaci.selection.length == 0) {
        Alert.show("Error: Cannot download the entire world.", 'error', $('#alerts'), $('body'));
        return;
    } else {
        src = "/podaci/zip/?files=" + ID2.Podaci.selection.join("&files=");
    }
    window.location = src;
};

ID2.Podaci.file_click = function(e) {
    id = $(e.target).parent().closest("div").data("id");
    console.log('clicked: ' + id)
    e.preventDefault();
    e.stopPropagation();
    if (ID2.Podaci.selection.indexOf(id) == -1) {
        ID2.Podaci.select([id]);
    } else {
        ID2.Podaci.deselect([id]);
    }
};

ID2.Podaci.file_doubleclick = function(e) {
    e.preventDefault();
    e.stopPropagation();

    var fileId = $(e.currentTarget).data('id');
    $.getJSON('/podaci/file/' + fileId + '/', function(data) {
      console.log("Showing modal!", data);
      var $modal = $("#file-modal");
      $modal.find('#file-modal-filename').text(data.title || data.filename);
      $modal.find('#file-download-link').attr('href', '/podaci/file/' + fileId + '/download');
      $modal.find('#file-title').val(data.title);
      $modal.find('#file-name').val(data.filename);
      $modal.find('#file-date').val(moment(data.date_added).format('LL'));
      $modal.find('#file-tags').select2({
        tags: true,
        data: data.tags,
        tokenSeparators: [',', ' ']
      });
      $modal.find('#file-tags').val(data.tags).trigger("change");

      // authz
      $modal.find('#file-public-read').val(data.public_read);
      $modal.find('#file-staff-read').val(data.staff_read);
      var userConfig = {
        ajax: {
          url: "/accounts/suggest/",
          dataType: 'json',
          delay: 250,
          data: function (params) {
            return {prefix: params.term};
          },
          processResults: function (data, page) {
            return {
              results: data.results
            };
          },
          cache: true,
        },
        templateResult: function(obj) {
          return obj.display_name;
        },
        templateSelection: function(obj) {
          return obj.display_name;
        },
        // data: data.allowed_users_read + data.allowed_users_write,
        minimumInputLength: 1
      };
      $modal.find('#file-users-read').select2(userConfig);
      var $readSelect = $modal.find('#file-users-read').select2();
      for (var i in data.allowed_users_read) {
        var user = data.allowed_users_read[i],
            opt = new Option(user.display_name, user.id, true, true);;
         $readSelect.append(opt);
      }
      $readSelect.trigger('change');

      $modal.find('#file-users-write').select2(userConfig);
      var $writeSelect = $modal.find('#file-users-write').select2();
      for (var i in data.allowed_users_write) {
        var user = data.allowed_users_write[i],
            opt = new Option(user.display_name, user.id, true, true);;
         $writeSelect.append(opt);
      }
      $writeSelect.trigger('change');

      $modal.modal("show");

      $modal.find('#file-save-link').click(function() {
        data.title = $modal.find('#file-title').val();
        data.tags = $modal.find('#file-tags').val() || [];
        data.public_read = $modal.find('#file-public-read').val() || false;
        data.staff_read = $modal.find('#file-staff-read').val() || false;
        data.allowed_users_read = $modal.find('#file-users-read').val() || [];
        data.allowed_users_write = $modal.find('#file-users-write').val() || [];

        $.ajax({
          type: 'PUT',
          url: '/podaci/file/' + fileId + '/',
          data: JSON.stringify(data),
          contentType: 'application/json',
          dataType: 'json'
        });
        $modal.modal("hide");
      });
    });
};

// FIXME: Normalize on _ or - .. using both is silly.
ID2.Podaci.callbacks = {
    "#podaci-upload click": ID2.Podaci.upload_click,
    ".podaci-upload_dropzone drop": ID2.Podaci.upload_click,
    ".podaci_edit_users click": ID2.Podaci.edit_users,
    "#podaci_create_collection_btn click": ID2.Podaci.create_collection_submit,

    ".podaci_btn_select_all click": ID2.Podaci.select_all,
    ".podaci_btn_select_none click": ID2.Podaci.select_none,
    ".podaci_btn_select_invert click": ID2.Podaci.select_invert,
    ".podaci_file_select_all change": ID2.Podaci.select_invert,
    ".podaci_file_select_box change": ID2.Podaci.select_toggle_checkbox,
    ".podaci_selection_download_zip click": ID2.Podaci.download_zip,
    ".podaci_open_in_overview click": ID2.Podaci.open_in_overview,

    ".podaci_edit_tags click": ID2.Podaci.edit_tags,
    "#podaci_edit_tags_btn click": ID2.Podaci.edit_tags_submit,

    ".podaci-files-icons > .podaci-file click": ID2.Podaci.file_click,
    ".podaci-files-icons > .podaci-file dblclick": ID2.Podaci.file_doubleclick,

    "#podaci-list-mode-icons click": ID2.Podaci.listmode_icons,
    "#podaci-list-mode-list click": ID2.Podaci.listmode_list,

    ".collectionfilters a click": ID2.Podaci.collection_filter_click,
    "#searchbox keyup": ID2.Podaci.searchbox_keyup,
    "#collection-new click": function() { $("#podaci_create_collection_modal").modal(); },

    "#ticket-file-add click": ID2.Podaci.ticket_add_file,
};


$(ID2.Podaci.init);
