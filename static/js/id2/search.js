
var id2 = {};
id2.search = {};

id2.search.init = function() {
    $("#search_submit").on("click", id2.search.startSearch);
    $("#search_form").on("submit", id2.search.startSearch);
};

id2.search.checkResults = function(searchid, resultcallback) {
    console.log("Checking results...")
    $.getJSON("/search/results/", {"id": searchid}, function(data) {
        if (data.status) {
            $("#search_results").empty();
            // FIXME: i18n:
            $("#search_statistics").text("Found " + data.results.length + " results from " + data.bots_done + " of " + data.bots_total + " sources.");
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
                window.setTimeout(function() { id2.search.checkResults(searchid, resultcallback); }, data.checkin_after);
            }
        } else {
            window.setTimeout(function() { id2.search.checkResults(searchid, resultcallback); }, 2000);
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
    result.append('<div class="search-origin">Source: <span class="provider ' + item.provider + '"><i class="fa fa-' + (item.provider=='VKontakte' ? 'vk' : item.provider.toLowerCase()) + '"></i>'+ item.provider + '</span></div>');
    return result;
};

id2.search.renderDocumentResult = function(item) {
    var result = $('<div class="document-search-result"/>');
    console.log(item);
    result.append('<h4><a href="' + item.data.result_url + '" target="_blank">' + item.data.title + '</a></h4>');
    result.append('<p>' + item.data.text + '</p>');
    var tags = $('<div class="search-tags"/>');
    for (tag in item.data.metadata.fields.tags) {
        tag = item.data.metadata.fields.tags[tag];
        tags.append('<span class="search-tag">' + tag + '</span>');
    }
    result.append('<div class="search-origin">Source: <span class="provider ' + item.provider + '">'+ item.provider + '</span></div>');
    result.append(tags);
    return result;
/*    <h4><a href="{{ result.fields.url }}" target="_blank">
              <img src="{{ static_url }}img/icons/32px/{{ result.fields.url.rsplit('.')[-1]}}.png"/> {{ result.fields.title }}</a></h4>
              <p>
8             {% if 'highlight' in result %}
              {{ result.highlight.text|join(' ... ')|safe }} </p>
              {% endif %}
              <div class="tags">
                Tags:
              <span class="tags_title">
                {% for tag in result.fields.tags %}
                  <a href="#" data-tag="{{tag}}" class="tag_link">{{ tag }}</a> * 
                {% endfor %}
              </div>*/
};

id2.search.renderDefaultResult = function(item) {
    result = $('<div class="result">' + item + '</div>');
    return result;
};

id2.search.resultcallbacks = {
    "image": id2.search.renderImageResult,
    "document": id2.search.renderDocumentResult,
    "default": id2.search.renderDefaultResult,
}

id2.search.urls = {
    // FIXME: Get this from elsewhere
    "image": "/search/image/query/",
    "document": "/search/document/query/",
}

id2.search.startSearch = function() {
    console.log("STARTING SEARCH");
    $("#search_results").empty();
    $("#search_statistics").hide();
    var type = $("#search_form").data("type");
    var callback = id2.search.resultcallbacks[type];
    if (!callback) {
        callback = id2.search.resultcallbacks["default"];
    }
    url = id2.search.urls[type];
    $.getJSON(url, $("#search_form").serialize(), function(data) {
        if (data.status) {
            $("#searching_notice").show();
            window.setTimeout(function() { 
                id2.search.checkResults(data.searchid, callback); 
            }, data.checkin_after);
        }
    });
    return false;
};

$(function() {
    id2.search.init();
});