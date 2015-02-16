
Podaci = {};

Podaci.init = function() {
    for (cb in Podaci.callbacks) {
        var item = cb.split(" ");
        var event = item.pop();
        var selector = item.join(" ");
        $(selector).on(event, Podaci.callbacks[cb]);
    }

    Podaci.tagid = $("#podaci_tag_id").val();
    Podaci.selection = [];
    Podaci.update_selection();
    Podaci.init_fileupload();
};

Podaci.update_selection = function() {
    var not_selected = _.difference(
        $.map($(".podaci-file"), function(e) { return $(e).data("id") }, 
        Podaci.selection));

    for (idx in not_selected) { // It might be faster to just apply this to $(".podaci-file"), without a loop?
        $(".podaci-file[data-id='" + not_selected[idx] + "'").removeClass("podaci-file-selected");
    }
    for (idx in Podaci.selection) {
        $(".podaci-file[data-id='" + Podaci.selection[idx] + "'").addClass("podaci-file-selected");
    }
    if (Podaci.selection.length == 0) {
        $("#podaci_selection_menu").text("All files");
    } else {
        $("#podaci_selection_menu").text("Selection (" + Podaci.selection.length + ")");
    }
}

Podaci.select = function(selection) {
    Podaci.selection = _.union(Podaci.selection, selection);
    Podaci.update_selection();
}

Podaci.deselect = function(selection) {
    Podaci.selection = _.difference(Podaci.selection, selection);
    Podaci.update_selection();
}

Podaci.select_invert = function() {
    Podaci.selection = _.difference(
        $.map($(".podaci-file"), function(e) { return $(e).data("id") }), 
        Podaci.selection);
    Podaci.update_selection();
}

Podaci.select_all = function() {
    Podaci.selection = $.map($(".podaci-file"), function(e) { return $(e).data("id") });
    Podaci.update_selection();
}

Podaci.select_none = function() {
    Podaci.selection = [];
    Podaci.update_selection();
}

Podaci.init_fileupload = function() {
    $('.podaci_upload_files').fileupload({
        url: '/podaci/file/create/',
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $('<p/>').text(file.name).appendTo(document.body);
            });
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

Podaci.edit_groups = function() {
    $("#podaci_edit_groups_modal").modal();
};

Podaci.edit_tags = function() {
    $("#podaci_edit_tags_modal").modal();
};

Podaci.create_tag_submit = function() {
    $.post('/podaci/tag/create/', 
           $("#podaci_create_tag_form").serialize(), 
           function(data) {
        console.log(data);
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
}


Podaci.refresh_files = function() {
    // FIXME: This currently fetches tag info, but discards it.
    //        We should opportunistically update the tag sets
    //        since we have the data anyway.
    $(".podaci-files").each(function(index, el) {
        var tag = $(el).data("tag");
        if (tag == undefined || tag == null || tag == "") {
            return;
        } else {
            console.log("Refreshing files on ", el);
            url = "/podaci/tag/" + tag + "/";
        }
        $.getJSON(url, {"format": "json"}, function(data) {
            if (!data || data.error) {
                // FIXME: Handle error.
            } else {
                $(el).empty();
                for (index in data.result_files) {
                    file = data.result_files[index];
                    var li = $('<li class="podaci-file"/>');
                    li.data("mime", file.meta.mimetype);
                    li.data("size", file.meta.size);
                    li.data("id", file.meta.id);
                    $(el).append(li);
                    var a = $("<a/>");
                    a.attr("href", "/podaci/podaci/file/" + file.id + "/");
                    a.html('<i class="icon-file podaci-icon-big"></i>' + file.meta.filename);
                    li.append(a);
                }
            }
        });
    });
}

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
}

Podaci.file_click = function(e) {
    id = $(e.target).closest("li").data("id");
    e.preventDefault();
    e.stopPropagation();
    if (Podaci.selection.indexOf(id) == -1) {
        Podaci.select([id]);
    } else {
        Podaci.deselect([id]);        
    }
}

Podaci.file_doubleclick = function(e) {
    window.location = $(e.target).closest("a")[0].href;
}

Podaci.get_user_tags = function(callback) {
    $.getJSON("/podaci/tag/list/", {format:"json"}, callback);
}

Podaci.get_user_tags_url = function(callback) {
    return "/podaci/tag/list/?format=json";
}


Podaci.callbacks = {
    ".podaci_upload click": Podaci.upload_click,
    ".podaci_upload_dropzone drop": Podaci.upload_click,
    ".podaci_edit_users click": Podaci.edit_users,
    ".podaci_edit_groups click": Podaci.edit_groups,
    ".podaci_edit_tags click": Podaci.edit_tags,
    ".podaci_create_tag click": Podaci.create_tag,
    "#podaci_create_tag_btn click": Podaci.create_tag_submit,

    ".podaci_btn_select_all click": Podaci.select_all,
    ".podaci_btn_select_none click": Podaci.select_none,
    ".podaci_btn_select_invert click": Podaci.select_invert,
    ".podaci_selection_download_zip click": Podaci.download_zip,

    ".podaci-file click": Podaci.file_click,
    ".podaci-file dblclick": Podaci.file_doubleclick,
};


$(Podaci.init);

