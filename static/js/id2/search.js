
var id2 = {};
id2.search = {};

id2.search.init = function() {
    $("#image_search_submit").on("click", id2.search.startImageSearch);
    $("#image_search_form").on("submit", id2.search.startImageSearch);
};

id2.search.checkResults = function(searchid, resultcallback) {
    $.getJSON('{{url("search_results")}}', {"id": searchid}, function(data) {
        if (data.status) {
            $("#search_results").empty();
            $("#search_statistics").text("Found " + data.results.length + " images from " + data.bots_done + " of " + data.bots_total + " image sources.");
            $("#search_statistics").show();
            for (item in data.results) {
                var item = data.results[item];
                var result = resultcallback(item);
                $("#search_results").append(result);
            }
            if (data.done || data.checkin_after == -1) {
                $("#searching_notice").hide();
                $('body').animate({
                    scrollTop: $('#search_results').offset().top
                }, 1000);
            } else {
                window.setTimeout(function() { id2.checkSearchResults(searchid, resultcallback); }, data.checkin_after);
            }
        } else {
            window.setTimeout(function() { id2.checkSearchResults(searchid, resultcallback); }, 2000);
        }
    });
};

id2.search.renderImageResult = function(item) {
    var timestamp = new Date(item.data.timestamp*1000);
    result = $('<div class="image-search-result"/>');
    result.append('<a href="'+item.data.result_url+'"><img src="'+item.data.image_url+'"/></a>');
    result.append('<div class="image-search-caption">'+item.data.caption+'</div>');
    result.append('<div class="image-search-link"><a href="'+item.data.linkurl+'">'+item.data.linktitle+'</a></div>');
    result.append('<div class="image-search-date">'+timestamp+'</div>');
    result.append('<div class="image-search-origin">Source: <span class="provider ' + item.provider + '"><i class="fa fa-' + (item.provider=='VKontakte' ? 'vk' : item.provider.toLowerCase()) + '"></i>'+ item.provider + '</span></div>');
    return result;
};

id2.search.startImageSearch = function() {
    $("#search_results").empty();
    $("#search_statistics").hide();
    $.getJSON(search_images_query, $("#image_search_form").serialize(), function(data) {
        if (data.status) {
            $("#searching_notice").show();
            window.setTimeout(function() { 
                id2.checkSearchResults(data.searchid, id2.search.renderImageResult); 
            }, data.checkin_after);
        }
    });
};

$(function() {
    id2.search.init();
});