
var ID2 = ID2 || {};
ID2.Database = {};

ID2.Database.init = function() {
    $(".db-register-form").submit(ID2.Database.registerFormSubmitHandler);
    $(".database-items .database-item .db-delete-btn").click(ID2.Database.deleteClickHandler);
    ID2.Database.jQueryPluginLoad();
};

/*
 * Fancy jQuery plugin to accurately
 * serialize checkboxes - i.e., to leave
 * them in, even if they are not checked.
 */


ID2.Database.jQueryPluginLoad = function() {
    (function ($) {
         $.fn.serialize = function (options) {
             return $.param(this.serializeArray(options));
         };
 
         $.fn.serializeArray = function (options) {
             var o = $.extend({
                 checkboxesAsBools: false
             }, options || {});
 
             var rselectTextarea = /select|textarea/i;
             var rinput = /text|hidden|password|search|url/i;
 
             return this.map(function () {
                 return this.elements ? $.makeArray(this.elements) : this;
             })
            .filter(function () {
                return this.name && !this.disabled &&
                   (this.checked
                   || (o.checkboxesAsBools && this.type === 'checkbox')
                   || rselectTextarea.test(this.nodeName)
                   || rinput.test(this.type));
            })
            .map(function (i, elem) {
                 var val = $(this).val();
                 return val == null ?
                 null :
                 $.isArray(val) ?
                 $.map(val, function (val, i) {
                    return { name: elem.name, value: val };
                 }) :
                 {
                     name: elem.name,
                     value: (o.checkboxesAsBools && this.type === 'checkbox') ? //moar ternaries!
                           (this.checked ? 'true' : 'false') :
                           val
                 };
             }).get();
        };
    })(jQuery);
}


ID2.Database.serializeForm = function($form){
    var serialized = $form.serializeArray({ checkboxesAsBools: true });
    var s = '';
    var data = {};

    for(s in serialized) {
        data[serialized[s]['name']] = serialized[s]['value']
    }

    return JSON.stringify(data);
}

ID2.Database.getCookie = function(name) {
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

/*
 * A little helper-function, dealing
 * with setting content-type and
 * relevant HTTP headers just before
 * sending AJAX request.
 */

ID2.Database.BeforeSendHandlerHelper = function(xhr) {
   xhr.setRequestHeader("Content-Type","application/json");
   xhr.setRequestHeader("X-csrftoken", ID2.Database.getCookie('csrftoken'));
}

ID2.Database.registerFormSubmitHandlerAjaxResponseHandler = function(event) {
}

/*
 * Handle submissions of register-form
 */

ID2.Database.registerFormSubmitHandler = function(event) {
    $(".db-register-form .btn").css('display', 'none');
    $("label[for]").css('color', 'black');

    // If pk is part off the form, we are supposed
    // to update an entry
    ID2.Database.pk = $(".form-horizontal.db-register-form #id_register_form-pk").val();

    $.ajax({
        type: ID2.Database.pk == undefined ? "POST" : "PUT",
        url: "/api/2/databases/" + (ID2.Database.pk != undefined ? ID2.Database.pk : ""),
        data:  ID2.Database.serializeForm($("#db-register-form")),
        success: function(data, textStatus, jqXHR)  {
            if ((jqXHR.status == 200) || (jqXHR.status == 201)) {
                if (!ID2.Database.pk) {
                    $(".db-register-form .btn-reset").click();
                }

                $(".db-register-form .alert-content").text(
                    ID2.Database.pk == undefined ?
                    'External database successfully registered' :
                    'Updated external database'
                );
            }

            else {
                 $(".db-register-form .alert-content").text('Unable to save, something failed');

                 for (var key in data) {
                     $("label[for='id_" + key + "'] " ).css('color', 'red');
                 }
            }

            $(".db-register-form.alert").css('display', 'inline-block');
            $(".db-register-form .btn").css('display', ' inline-block');

        },
        error: function(jqXHR, status, error) {
            this.success(jqXHR.error().responseJSON, status, jqXHR);
        },
        dataType: "json",
        beforeSend: ID2.Database.BeforeSendHandlerHelper,
    });

   return false; // Make sure form isn't submitted
}


/*
 * Handle when 'delete' button is pressed.
 * Ask for confirmation, and if sure,
 * call actual deletion handler,
 * forwarding the event object to that handler.
 */

ID2.Database.deleteClickHandler = function(event) {
    if (confirm('Are you sure?')) {
        return ID2.Database.deleteSubmitHandler(event);
    }
}


/*
 * Actually delete database entry.
 */

ID2.Database.deleteSubmitHandler = function(event) {
    $.ajax({
        type: "DELETE",
        url: "/api/2/databases/" + event.target.getAttribute('db-item-id'),
        data: "",
        success: function(data, textStatus, jqXHR) {
            if (jqXHR.status == 204) {
                event.target.parentElement.parentElement.style.display = "none";
            }

            else {
                alert('An error occured: ' + jqXHR.statusText);
            }
        },
        error: function(jqXHR, status, error) {
            this.success(jqXHR.error().responseJSON, status, jqXHR);
        },
        dataType: "json",
        beforeSend: ID2.Database.BeforeSendHandlerHelper,
    });

    return false;
}

ID2.Database.init();
