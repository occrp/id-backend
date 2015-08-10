
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
    for (cb in ID2.Podaci.callbacks) {
        var item = cb.split(" ");
        var event = item.pop();
        var selector = item.join(" ");
        $(selector).on(event, ID2.Podaci.callbacks[cb]);
    }

    // ID2.Podaci.search("");
    ID2.Podaci.update_collections();

    ID2.Podaci.tagid = $("#podaci_tag_id").val();
    ID2.Podaci.fileid = $("#podaci_file_id").val();
    ID2.Podaci.selection = [];
    ID2.Podaci.update_selection();
    ID2.Podaci.init_fileupload();
    ID2.Podaci.init_listmode();
    ID2.Podaci.init_taggedtext();
    ID2.Podaci.init_edit_tags();
};

ID2.Podaci.search = function(q) {
    ID2.Podaci.results_clear();
    $.getJSON("/podaci/search/", {"q": q}, function(data) {
        console.log("Search results back!");
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
        console.log("Timer reset");
    }
    if (code == 13) {
        ID2.Podaci.trigger_search();
    } else {
        ID2.Podaci.searchbox_timer = setTimeout(ID2.Podaci.trigger_search, 2000);
    }
}

ID2.Podaci.trigger_search = function() {
    console.log("Search triggered");
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
}

ID2.Podaci.add_file_to_results = function(file) {
    var fo = $("<div>");
    fo.hide;
    fo.addClass("podaci-file");
    fo.append("<img src=\"" + file.thumbnail + "\" class=\"podaci-file-thumbnail\"/>");
    fo.append("<span class=\"podaci-file-filename\">" + (file.name || file.filename) + "</span>");
    fo.attr("data-id", file.id);
    fo.click(ID2.Podaci.file_click);
    $("#resultbox").append(fo);
    fo.hide().slideDown(600);
}

ID2.Podaci.search_term_add = function(term) {
    var v = $("#searchbox").val();
    v += " " + term;
    $("#searchbox").val(v);
};

ID2.Podaci.search_term_remove = function(term) {
    var v = $("#searchbox").val();
    v = v.replace(" " + term, "");
    $("#searchbox").val(v);
};

ID2.Podaci.update_collections = function() {
    console.log("Updating collections");
    $.getJSON("/podaci/collection/", function(data) {
        console.log("Collections:", data);
        $("#mycollections").empty();
        for (collection in data.results) {
            collection = data.results[collection];
            $("#mycollections").append("<li><a data-collection=\"" + collection.id + "\"><i class=\"fa fa-folder\"></i> " + collection.name + "</a></li>");
        }
    });
};

ID2.Podaci.collection_filter_click = function(e) {
    console.log("FOO!");
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

ID2.Podaci.init_edit_tags = function() {
    $("#podaci_add_tags_input").select2({
        ajax: {
            url: "/podaci/tag/list/?format=json&structure=select2",
            dataType: 'json',
            delay: 250,
            processResults: function (data, page) {
                return data;
            }
        },
        minimumInputLength: 1,
    });
};

ID2.Podaci.init_taggedtext = function() {
    $('textarea.tagged_text').mentionsInput({
        onDataRequest: function (mode, query, callback) {
            $.getJSON('/podaci/search/mention/', { "format": "json", "q": query }, function(data) {
                callback.call(this, data);
            });
        }
    });
};

ID2.Podaci.init_listmode = function() {
    ID2.Podaci.listmode_icons();
};

ID2.Podaci.listmode_icons = function() {
    $(".podaci-files-list").hide();
    $(".podaci-files-icons").show();
    $("#podaci-list-mode-icons").addClass("active");
    $("#podaci-list-mode-list").removeClass("active");
};

ID2.Podaci.listmode_list = function() {
    $(".podaci-files-icons").hide();
    $(".podaci-files-list").show();
    $("#podaci-list-mode-list").addClass("active");
    $("#podaci-list-mode-icons").removeClass("active");
};

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
        console.log("Selecting " + id);
        ID2.Podaci.select([id]);
    } else {
        console.log("Deselecting " + id);
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
    console.log("Toggling " + id);
    ID2.Podaci.select_toggle(id);
}

ID2.Podaci.init_fileupload = function() {
    $('.podaci_upload_files').fileupload({
        url: '/podaci/file/create/',
        dataType: 'json',
        done: function (e, data) {
            setTimeout(ID2.Podaci.refresh_files, 300);
        },
        dropzone: $(".podaci_upload_dropzone"),
        disableImageResize: /Android(?!.*Chrome)|Opera/
            .test(window.navigator.userAgent),
    }).on('fileuploadadd', function (e, data) {
        data.context = $('#podaci_upload_list');
        $.each(data.files, function (index, file) {
            var node = $('<tr class="podaci-file podaci-file-pending"/>');
            var linkcolumn = node.append('<td/>')
            linkcolumn.append('<a>'+file.name+'</a>');
            node.append('<td><textarea></textarea></td>');
            node.appendTo(data.context);
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
        if (data.id) {
            $(data.context.children()[index]).removeClass("podaci-file-pending");
            $(data.context.children()[index]).children[0]
                .prop('href', '/podaci/file/' + data.id + '/');
        } else if (data.error) {
            var error = $('<span class="text-danger"/>').text(data.error);
            $(data.context.children()[index])
                .append('<br>')
                .append(error);
        }
        setTimeout(ID2.Podaci.refresh_files, 300);
    }).on('fileuploadfail', function (e, data) {
        // FIXME: Test failure modes. Make this pretty.
        $.each(data.files, function (index) {
            var error = $('<span class="text-danger"/>').text('File upload failed.');
            $(data.context.children()[index])
                .append('<br>')
                .append(error);
        });
    });
};

ID2.Podaci.upload_click = function(e, target) {
    $("#podaci_upload_modal").modal();
};

ID2.Podaci.create_tag = function() {
    $("#podaci_create_tag_modal").modal();
};

ID2.Podaci.edit_users = function() {
    $("#podaci_edit_users_modal").modal();
    $("#podaci_edit_users_add_user").select2({
        ajax: {
            url: $(this).data('url'),
        }
    });
};

ID2.Podaci.add_tags = function() {
    $("#podaci_add_tags_modal").modal();
};

ID2.Podaci.remove_tags = function() {
    for (i in self.selection) {

    }
    $("#podaci_remove_tags_modal").modal();
};

ID2.Podaci.create_tag_submit = function() {
    $.post('/podaci/tag/create/',
           $("#podaci_create_tag_form").serialize(),
           function(data) {
        if (data.error) {
            console.log("ERROR: ", data.error);
            $("#podaci_create_tag_error").html(data.error);
            $("#podaci_create_tag_error").show();
        } else {
            $("#podaci_create_tag_modal").modal("hide");
            setTimeout(ID2.Podaci.refresh_tags, 300);
        }
    });
};

ID2.Podaci.refresh_tags = function() {
    $(".podaci-tags").each(function(index, el) {
        var tag = $(el).data("tag");
        $.getJSON('/podaci/tag/' + tag + '/', {format: "json"},
                  function(data) {
            if (data.error) {
                console.log("ERROR: ", data.error);
            } else {
                $(el).empty();
                console.log(data);
                for (idx in data.result_tags) {
                    tag = data.result_tags[idx];
                    console.log(tag);
                    $(el).append('<li><a href="/podaci/tag/' + tag.id + '/"><i class="icon-tag"></i> ' + tag.meta.name + '</a></li>');
                }
            }
        });
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
    id = $(e.target).closest("div").data("id");
    e.preventDefault();
    e.stopPropagation();
    if (ID2.Podaci.selection.indexOf(id) == -1) {
        ID2.Podaci.select([id]);
    } else {
        ID2.Podaci.deselect([id]);
    }
};

ID2.Podaci.file_doubleclick = function(e) {
    window.location = $(e.target).closest("a")[0].href;
};

ID2.Podaci.get_user_tags = function(callback) {
    $.getJSON("/podaci/tag/list/", {format:"json"}, callback);
};

ID2.Podaci.get_user_tags_url = function(callback) {
    return "/podaci/tag/list/?format=json";
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
    ".podaci_upload click": ID2.Podaci.upload_click,
    ".podaci_upload_dropzone drop": ID2.Podaci.upload_click,
    ".podaci_edit_users click": ID2.Podaci.edit_users,
    ".podaci_add_tags click": ID2.Podaci.add_tags,
    ".podaci_remove_tags click": ID2.Podaci.remove_tags,
    ".podaci_create_tag click": ID2.Podaci.create_tag,
    "#podaci_create_tag_btn click": ID2.Podaci.create_tag_submit,

    ".podaci_btn_select_all click": ID2.Podaci.select_all,
    ".podaci_btn_select_none click": ID2.Podaci.select_none,
    ".podaci_btn_select_invert click": ID2.Podaci.select_invert,
    ".podaci_file_select_all change": ID2.Podaci.select_invert,
    ".podaci_file_select_box change": ID2.Podaci.select_toggle_checkbox,
    ".podaci_selection_download_zip click": ID2.Podaci.download_zip,
    ".podaci_open_in_overview click": ID2.Podaci.open_in_overview,

    ".podaci-files-icons > .podaci-file click": ID2.Podaci.file_click,
    ".podaci-files-icons > .podaci-file dblclick": ID2.Podaci.file_doubleclick,

    "#podaci-list-mode-icons click": ID2.Podaci.listmode_icons,
    "#podaci-list-mode-list click": ID2.Podaci.listmode_list,

    "#podaci_note_save click": ID2.Podaci.file_add_note,
    "#extra_metadata_save click": ID2.Podaci.metadata_save,

    ".collectionfilters a click": ID2.Podaci.collection_filter_click,
    "#searchbox keyup": ID2.Podaci.searchbox_keyup,
};


$(ID2.Podaci.init);
