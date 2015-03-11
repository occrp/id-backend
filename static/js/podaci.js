
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


Podaci = {};

Podaci.init = function() {
    for (cb in Podaci.callbacks) {
        var item = cb.split(" ");
        var event = item.pop();
        var selector = item.join(" ");
        $(selector).on(event, Podaci.callbacks[cb]);
    }

    Podaci.tagid = $("#podaci_tag_id").val();
    Podaci.fileid = $("#podaci_file_id").val();
    Podaci.selection = [];
    Podaci.update_selection();
    Podaci.init_fileupload();
    Podaci.init_listmode();
    Podaci.init_taggedtext();
    Podaci.init_edit_tags();
};

Podaci.init_edit_tags = function() {
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

Podaci.init_taggedtext = function() {
    $('textarea.tagged_text').mentionsInput({
        onDataRequest: function (mode, query, callback) {
            $.getJSON('/podaci/search/mention/', { "format": "json", "q": query }, function(data) {
                callback.call(this, data);
            });
        }
    });
};

Podaci.init_listmode = function() {
    $(".podaci-files-icons").hide();
    $(".podaci-files-list").show();
    $("#podaci-list-mode-list").addClass("active");
    $("#podaci-list-mode-icons").removeClass("active");
};

Podaci.listmode_icons = function() {
    $(".podaci-files-list").hide();   
    $(".podaci-files-icons").show();
    $("#podaci-list-mode-icons").addClass("active");
    $("#podaci-list-mode-list").removeClass("active");
};

Podaci.listmode_list = function() {
    $(".podaci-files-icons").hide();
    $(".podaci-files-list").show();   
    $("#podaci-list-mode-list").addClass("active");
    $("#podaci-list-mode-icons").removeClass("active");
};

Podaci.update_selection = function() {
    var not_selected = _.difference(
        $.map($(".podaci-files-list .podaci-file"), function(e) { return $(e).data("id") }, 
        Podaci.selection));

    for (idx in not_selected) { // It might be faster to just apply this to $(".podaci-file"), without a loop?
        $(".podaci-file[data-id='" + not_selected[idx] + "']").removeClass("podaci-file-selected");
        $(".podaci-file[data-id='" + not_selected[idx] + "'] .podaci_file_select_box").prop("checked", false);
    }
    for (idx in Podaci.selection) {
        $(".podaci-file[data-id='" + Podaci.selection[idx] + "']").addClass("podaci-file-selected");
        $(".podaci-file[data-id='" + Podaci.selection[idx] + "'] .podaci_file_select_box").prop("checked", true);
    }

    if (Podaci.selection.length == 0 && not_selected.length == 0) {
        $("#podaci_selection_menu").html("No files <span class=\"caret\"></span>");
        // $("#podaci_selection_menu")
    } else if (Podaci.selection.length == 0) {
        $("#podaci_selection_menu").html("All files <span class=\"caret\"></span>");
    } else {
        $("#podaci_selection_menu").html("Selection (" + Podaci.selection.length + ") <span class=\"caret\"></span>");
    }
};

Podaci.select = function(selection) {
    Podaci.selection = _.union(Podaci.selection, selection);
    Podaci.update_selection();
};

Podaci.deselect = function(selection) {
    Podaci.selection = _.difference(Podaci.selection, selection);
    Podaci.update_selection();
};

Podaci.select_toggle = function(id) {
    if (Podaci.selection.indexOf(id) == -1) {
        console.log("Selecting " + id);
        Podaci.select([id]);
    } else {
        console.log("Deselecting " + id);
        Podaci.deselect([id]);
    }
};

Podaci.select_invert = function() {
    Podaci.selection = _.difference(
        $.map($(".podaci-files-list .podaci-file"), function(e) { return $(e).data("id") }), 
        Podaci.selection);
    Podaci.update_selection();
};

Podaci.select_all = function() {
    Podaci.selection = $.map($(".podaci-files-list .podaci-file"), function(e) { return $(e).data("id") });
    Podaci.update_selection();
};

Podaci.select_none = function() {
    Podaci.selection = [];
    Podaci.update_selection();
};

Podaci.select_toggle_checkbox = function(e) {
    id = $(e.target).parent().parent().data("id");
    console.log("Toggling " + id);
    Podaci.select_toggle(id);
}

Podaci.init_fileupload = function() {
    $('.podaci_upload_files').fileupload({
        url: '/podaci/file/create/',
        dataType: 'json',
        done: function (e, data) {
            setTimeout(Podaci.refresh_files, 300);
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
        // FIXME: This does not know which file just got completed.
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
        setTimeout(Podaci.refresh_files, 300);
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

Podaci.upload_click = function(e, target) {
    $("#podaci_upload_modal").modal();
};

Podaci.create_tag = function() {
    $("#podaci_create_tag_modal").modal();  
};

Podaci.edit_users = function() {
    $("#podaci_edit_users_modal").modal();
    $("#podaci_edit_users_add_user").select2({
        ajax: {
            url: $(this).data('url'),
        }
    });
};

Podaci.add_tags = function() {
    $("#podaci_add_tags_modal").modal();
};

Podaci.remove_tags = function() {
    for (i in self.selection) {

    }
    $("#podaci_remove_tags_modal").modal();
};

Podaci.create_tag_submit = function() {
    $.post('/podaci/tag/create/', 
           $("#podaci_create_tag_form").serialize(), 
           function(data) {
        if (data.error) {
            console.log("ERROR: ", data.error);
            $("#podaci_create_tag_error").html(data.error);
            $("#podaci_create_tag_error").show();
        } else {
            $("#podaci_create_tag_modal").modal("hide");
            setTimeout(Podaci.refresh_tags, 300);
        }
    });
};

Podaci.refresh_tags = function() {
    $(".podaci-tags").each(function(index, el) {
        var tag = $(el).data("tag");
        $.getJSON('/podaci/tag/' + tag + '/', {format: "json"}, 
                  function(data) {
            if (data.error) {
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

Podaci.refresh_files = function() {
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

Podaci.download_zip = function() {
    if (Podaci.selection.length == 0 && Podaci.tagid) {
        src = "/podaci/tag/" + Podaci.tagid + "/zip/";
    } else if (Podaci.selection.length == 0) {
        // FIXME: Alerts are so passé.
        alert("Error: Cannot download the entire world.");
        return;
    } else {
        src = "/podaci/tag/selection/zip/?files=" + Podaci.selection.join("&files=");
    }
    window.location = src;
};

Podaci.file_click = function(e) {
    id = $(e.target).closest("li").data("id");
    e.preventDefault();
    e.stopPropagation();
    if (Podaci.selection.indexOf(id) == -1) {
        Podaci.select([id]);
    } else {
        Podaci.deselect([id]);        
    }
};

Podaci.file_doubleclick = function(e) {
    window.location = $(e.target).closest("a")[0].href;
};

Podaci.get_user_tags = function(callback) {
    $.getJSON("/podaci/tag/list/", {format:"json"}, callback);
};

Podaci.get_user_tags_url = function(callback) {
    return "/podaci/tag/list/?format=json";
};

Podaci.update_notes = function(meta) {
    $("#file_notes").empty();
    for (i in meta.notes) {
        n = meta.notes[i];
        $("#file_notes").append(n.html);
    }
}

Podaci.file_add_note = function() {
    fileid = $("#podaci_file_id").val();
    $("#note_text").mentionsInput('val', function(text) {
        $.post('/podaci/file/' + fileid + '/note/add/', 
            $("#note_add_form").serialize() + "&note_text_markedup=" + encodeURIComponent(text),
            function(data) {
                if (data.success) {
                    $("#note_text").val("");
                    $("#note_text").mentionsInput("reset");
                }
                Podaci.update_notes(data.meta);
            }
        );
    });
}

Podaci.metadata_save = function() {
    fileid = $("#podaci_file_id").val();
    $.post('/podaci/file/' + fileid + '/metadata/update/', 
        $("#extra_metadata_form").serialize(),
        function(data) {
            if (data.success) {
                $("#note_text").val("");
            }
            Podaci.update_notes(data.meta);
        });
}

// FIXME: Normalize on _ or - .. using both is silly.
Podaci.callbacks = {
    ".podaci_upload click": Podaci.upload_click,
    ".podaci_upload_dropzone drop": Podaci.upload_click,
    ".podaci_edit_users click": Podaci.edit_users,
    ".podaci_add_tags click": Podaci.add_tags,
    ".podaci_remove_tags click": Podaci.remove_tags,
    ".podaci_create_tag click": Podaci.create_tag,
    "#podaci_create_tag_btn click": Podaci.create_tag_submit,

    ".podaci_btn_select_all click": Podaci.select_all,
    ".podaci_btn_select_none click": Podaci.select_none,
    ".podaci_btn_select_invert click": Podaci.select_invert,
    ".podaci_file_select_all change": Podaci.select_invert,
    ".podaci_file_select_box change": Podaci.select_toggle_checkbox,
    ".podaci_selection_download_zip click": Podaci.download_zip,

    ".podaci-files-icons > .podaci-file click": Podaci.file_click,
    ".podaci-files-icons > .podaci-file dblclick": Podaci.file_doubleclick,

    "#podaci-list-mode-icons click": Podaci.listmode_icons,
    "#podaci-list-mode-list click": Podaci.listmode_list,

    "#podaci_note_save click": Podaci.file_add_note,
    "#extra_metadata_save click": Podaci.metadata_save,
};


$(Podaci.init);

