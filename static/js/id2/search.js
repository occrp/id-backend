var ID2 = ID2 || {};
ID2.Search = {};

ID2.Search.init = function() {
    $(".provider input[type=checkbox]").on("change", ID2.Search.startSearch);
    $("#search_submit").on("click", ID2.Search.startSearch);
    $("#search_form").on("submit", ID2.Search.startSearch);
};

ID2.Search.renderMediaResult = function(item) {
    var timestamp = new Date(item.timestamp*1000);
    result = $('<div class="image-search-result"/>');
    result.append('<a href="'+item.result_url+'"><img src="'+item.image_url+'"/></a>');
    result.append('<div class="image-search-caption">'+item.caption+'</div>');
    result.append('<div class="image-search-link"><a href="'+item.linkurl+'">'+item.linktitle+'</a></div>');
    result.append('<div class="image-search-date">'+timestamp+'</div>');
    result.append('<div class="search-origin">Source: <span class="provider ' + item.provider + '"><i class="fa fa-' + (item.provider=='VKontakte' ? 'vk' : item.provider.toLowerCase()) + '"></i>'+ item.provider + '</span></div>');
    return result;
};

ID2.Search.renderDocumentResult = function(item) {
    var result = $('<div class="document-search-result"/>');
    console.log(item);
    result.append('<h4><a href="' + item.result_url + '" target="_blank">' + item.title + '</a></h4>');
    if (item.text) {
        result.append('<p>' + item.text + '</p>');
    }
    result.append('<div class="search-origin">Source: <span class="provider ' + item.provider + '">'+ item.provider + '</span></div>');

    var tags = $('<div class="search-tags"/>');
    if (item.metadata && item.metadata.fields && item.metadata.fields.tags) {
      for (tag in item.metadata.fields.tags) {
          tag = item.metadata.fields.tags[tag];
          tags.append('<span class="search-tag">' + tag + '</span>');
      }
      if (item.metadata.fields.tags.length) {
          result.append(tags);
      }
    }
    return result;
};

ID2.Search.renderDefaultResult = function(item) {
    result = $('<div class="result">' + item + '</div>');
    return result;
};

ID2.Search.resultcallbacks = {
    "media": ID2.Search.renderMediaResult,
    "document": ID2.Search.renderDocumentResult,
    "default": ID2.Search.renderDefaultResult,
}

ID2.Search.urls = {
    // FIXME: Get this from elsewhere
    "media": "/search/media/query/",
    "document": "/search/document/query/",
}

ID2.Search.handleResults = function(data, resultcallback, $count) {
  if (!data.status) {
    $count.html('FAIL');
    return;
  }
  for (idx in data.results) {
      var item = data.results[idx];
      var result = resultcallback(item);
      $("#search_results").append(result);
  }
  $count.html(data.total || '0');
};

ID2.Search.startSearch = function() {
    console.log("STARTING SEARCH");
    $("#search_results").empty();
    var type = $("#search_form").data("type");
    var callback = ID2.Search.resultcallbacks[type];
    if (!callback) {
        callback = ID2.Search.resultcallbacks["default"];
    }
    var url = ID2.Search.urls[type];
    var query = $("#search_form").serialize();
    $("#search_results").empty();

    $.each($("#search_form").serializeArray(), function(i, obj) {
      if (obj.name == 'providers') {
        var $el = $('.provider-' + obj.value),
            $running = $el.find('.running'),
            $count = $el.find('.count');
        $running.show();
        $count.empty();
        var providerquery = query + '&provider=' + obj.value;
        $.getJSON(url, providerquery, function(data) {
          ID2.Search.handleResults(data, callback, $count);
          $running.hide();
        });
      }
    });
    return false;
};

$(function() {
    ID2.Search.init();
});
