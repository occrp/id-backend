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
    ID2.Podaci.search("");
    ID2.Podaci.update_collections();

    ID2.Podaci.init_fileupload();
};

ID2.Podaci.search = function(q) {
    ID2.Podaci.results_clear();
    $.getJSON("/podaci/search/", {"q": q}, function(data) {
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
    $("#resultbox").empty();
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
        tags.append("<a data-tag=\"" + tag.id + "\">" + tag.name + "</a>");
    }

    var mimeinfo = $("<a data-mimetype=\"" + file.mimetype + "\" class=\"podaci-filetype\">" + file.mimetype.split("/")[1].toUpperCase() + "</a>");
    mimeinfo.click(function() { ID2.Podaci.search_term_add("mime:" + file.mimetype); })

    var filename = $("<a class=\"podaci-filename\">" + (file.name || file.filename) + "</a>");
    filename.click = ID2.Podaci.file_doubleclick;

    var selectbar = $("<div class=\"podaci-selectbar\">");
    selectbar.click(ID2.Podaci.file_click);

    var thumbnail = $("<img src=\"" + file.thumbnail + "\" class=\"podaci-file-thumbnail\"/>");
    thumbnail.click(ID2.Podaci.file_click);

    var fo = $("<div>");
    fo.addClass("podaci-file");
    fo.append(selectbar);
    fo.append(thumbnail);
    fo.append("<span class=\"podaci-filesize\">" + filesizeformat(file.size) + "</span>");
    fo.append(mimeinfo);
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
    $("#resultbox").append(fo);
}

ID2.Podaci.selection_drag = function(e) {
    // ...
};

ID2.Podaci.selection_drop = function(e) {
    e.preventDefault();
    $(e.target).removeClass("drop-on-me");
    var targetli = $(e.target).closest("li");
    var id = $(e.target).data("collectionid")
    $.ajax("/podaci/collection/" + id + "/", {
        type: "PATCH",
        data: {"add_files": ID2.Podaci.selection}
    }).done(function(data) {
        ID2.Podaci.add_collection(data, targetli);
        console.log(data);
    }).fail(function(data) {
        console.log(data);
    });
};

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

ID2.Podaci.select = function(selection) {
    ID2.Podaci.selection = _.union(ID2.Podaci.selection, selection);
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

ID2.Podaci.init_fileupload = function() {
    var col = $('.resultbox');
    ID2.Podaci.results_cache = [];

    col.on("dragover", function(e) {
        e.preventDefault();
        col.addClass("dropzone");
        col.empty();
    });
    col.on("dragleave", function(e) {
        e.preventDefault();
        col.removeClass("dropzone");
        ID2.Podaci.render_resultset();
    });
    col.on("drop", function(e) {
        ID2.Podaci.results_clear();
        col.removeClass("dropzone");
    });

    $('.podaci_upload_files').fileupload({
        url: '/podaci/file/create/',
        dataType: 'json',
        done: function (e, data) {
            setTimeout(ID2.Podaci.refresh_files, 300);
        },
        dropzone: $(".resultbox"),
        disableImageResize: /Android(?!.*Chrome)|Opera/
            .test(window.navigator.userAgent),
    }).on('fileuploadadd', function (e, data) {
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
        $('.podaci_upload_progress .progress-bar').css(
            'width',
            progress + '%'
        );
    }).on('fileuploaddone', function (e, data) {
        console.log(data);
        ID2.Podaci.add_file_to_results(data.result);
    }).on('fileuploadfail', function (e, data) {
        // FIXME: Test failure modes. Make this pretty.
    });
};

ID2.Podaci.upload_click = function(e, target) {
    $("#podaci_upload_modal").modal();
};


ID2.Podaci.edit_users = function() {
    $("#podaci_edit_users_modal").modal();
    $("#podaci_edit_users_add_user").select2({
        ajax: {
            url: $(this).data('url'),
        }
    });
};


ID2.Podaci.get_selected_tags = function() {
    // console.log(ID2.Podaci);
    var selected = null;
    $(".podaci-file").each(function(index, el) {
      var $el = $(el),
          tags = [];
      if (ID2.Podaci.selection.indexOf($el.data('id')) != -1) {
        var file = $el.data('file');
        $.each(file.tags, function(tidx, tag) {
          tags.push(tag.name);
        });
      }
      if (selected === null) {
        selected = tags;
      } else {
        selected = _.intersection(selected, tags);
      }
    });
    return selected;
};

ID2.Podaci.edit_tags = function() {
    $("#podaci_edit_tags_modal").modal();
    $("#podaci_edit_tags_input").select2({
      tags: true,
      tokenSeparators: [',', ' ']
    });
    $("#podaci_edit_tags_input").val(ID2.Podaci.get_selected_tags());
};


ID2.Podaci.edit_tags_submit = function() {
    var tags = $("#podaci_edit_tags_input").val(),
        common = ID2.Podaci.get_selected_tags(),
        added = _.without(tags, common),
        removed = _.without(common, tags);
    console.log('VALUES', tags, common, added, removed);

    $(".podaci-file").each(function(index, el) {
      var $el = $(el);
      if (ID2.Podaci.selection.indexOf($el.data('id')) == -1) {
        return;
      }
      var file = $el.data('file'),
          tags = [];
      $.each(added, function(i, t) {
        tags.push({'name': t});
      });
      $.each(file.tags, function(i, t) {
        if (removed.indexOf(t.name) == -1 &&
            added.indexOf(t.name) == -1) {
          tags.push(t);
        }
      });
      file.tags = tags;
      $.ajax({
        type: 'PUT',
        url: '/podaci/file/' + file.id + '/',
        data: file,
        dataType: 'json',
        success: function(file_ret) {
          console.log(file_ret);
        }
      });
    });

    $("#podaci_edit_tags_modal").modal('hide');
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
                // FIXME: Handle error.
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
                        a.attr("href", "/podaci/podaci/file/" + file.id + "/");
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
    if (ID2.Podaci.selection.length == 0 && ID2.Podaci.tagid) {
        src = "/podaci/tag/" + ID2.Podaci.tagid + "/zip/";
    } else if (ID2.Podaci.selection.length == 0) {
        // FIXME: Alerts are so passé.
        alert("Error: Cannot download the entire world.");
        return;
    } else {
        src = "/podaci/tag/selection/zip/?files=" + ID2.Podaci.selection.join("&files=");
    }
    window.location = src;
};

ID2.Podaci.open_in_overview = function() {
    if (ID2.Podaci.selection.length == 0 && ID2.Podaci.tagid) {
        $.getJSON("/podaci/tag/" + ID2.Podaci.tagid + "/overview/", {"format": "json"}, function(data) {
            if (data.ok) {
                window.open("https://www.overviewproject.org/documentsets/" + data.docsetid, "_blank");
            }
        });
    } else if (ID2.Podaci.selection.length == 0) {
        alert("Cannot open all everything in Overview");
    } else {
        $.getJSON("/podaci/tag/selection/overview/?files=" + ID2.Podaci.selection.join("&files="), {"format": "json"}, function(data) {
            if (data.ok) {
                window.open("https://www.overviewproject.org/documentsets/" + data.docsetid, "_blank");
            }
        });
    }
}

ID2.Podaci.file_click = function(e) {
    console.log("file click");
    id = $(e.target).parent().closest("div").data("id");
    e.preventDefault();
    e.stopPropagation();
    if (ID2.Podaci.selection.indexOf(id) == -1) {
        ID2.Podaci.select([id]);
    } else {
        ID2.Podaci.deselect([id]);
    }
};

ID2.Podaci.file_doubleclick = function(e) {
    console.log("filename click");
    e.preventDefault();
    e.stopPropagation();
    console.log("Showing modal!");
    $("#file-modal").modal("show");
    // window.location = $(e.target).closest("a")[0].href;
};


ID2.Podaci.update_notes = function(meta) {
    $("#file_notes").empty();
    for (i in meta.notes) {
        n = meta.notes[i];
        $("#file_notes").append(n.html);
    }
}

ID2.Podaci.file_add_note = function() {
    fileid = $("#podaci_file_id").val();
    $("#note_text").mentionsInput('val', function(text) {
        $.post('/podaci/file/' + fileid + '/note/add/',
            $("#note_add_form").serialize() + "&note_text_markedup=" + encodeURIComponent(text),
            function(data) {
                if (data.success) {
                    $("#note_text").val("");
                    $("#note_text").mentionsInput("reset");
                }
                ID2.Podaci.update_notes(data.meta);
            }
        );
    });
}

ID2.Podaci.metadata_save = function() {
    fileid = $("#podaci_file_id").val();
    $.post('/podaci/file/' + fileid + '/metadata/update/',
        $("#extra_metadata_form").serialize(),
        function(data) {
            if (data.success) {
                $("#note_text").val("");
            }
            ID2.Podaci.update_notes(data.meta);
        });
}

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

    "#podaci_note_save click": ID2.Podaci.file_add_note,
    "#extra_metadata_save click": ID2.Podaci.metadata_save,

    ".collectionfilters a click": ID2.Podaci.collection_filter_click,
    "#searchbox keyup": ID2.Podaci.searchbox_keyup,
    "#collection-new click": function() { $("#podaci_create_collection_modal").modal(); },

};


$(ID2.Podaci.init);
