
var ID2 = ID2 || {};
ID2.Database = {};

ID2.Database.init = function() {
    $(".register-form").submit(ID2.Database.submitHandler);
};


ID2.Database.serializeForm = function($form){
    var serialized = $form.serializeArray();
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

ID2.Database.submitHandler = function(event) {
    $(".register-form .btn").css('display', 'none');
    $("label[for]").css('color', 'black');

    $.ajax({
        type: "POST",
        url: "http://10.0.0.7:8080/api/2/databases/",
        data:  ID2.Database.serializeForm($("#register-form"))  ,
        success: function(data, textStatus, jqXHR)  {
            if (data['status'] == true) {
                $(".register-form .btn-reset").click();

                $(".register-form .alert-content").text('External database successfully registered');
            }

            else {
                 $(".register-form .alert-content").text('Unable to save, something failed');

                 for (key in data.errors) {
                     $("label[for='id_register_form-" + key + "'] " ).css('color', 'red');
                 }
            }

            $(".register-form.alert").css('display', 'inline-block');
            $(".register-form .btn").css('display', ' inline-block');

        },
        dataType: "json",

        beforeSend: function(xhr){
            xhr.setRequestHeader("Content-Type","application/json");
            xhr.setRequestHeader("X-csrftoken", ID2.Database.getCookie('csrftoken'));
        },
    });

    return false; // Make sure form isn't submitted
}

ID2.Database.init();
