$(document).ready(function accountRequestInit() {
    /**
    * Initializes the form and hides the media and circulation parent
    * fields if the industry value matches any of the `matches` values.
    */
    var matches = ['non_profit', 'for_profit', 'freelance']; 
    var other_match = ['other'];

    var $toWatch = $('select[name="industry"]');
    var $toHide = _.map(['media', 'circulation'], function(sel) {
        // div.control-group > div.controls > select[name=foo]
        return $('select[name="' + sel + '"]').parent().parent()[0];
    });


    // div.control-group > div.controls > input[name=industry_other]
    var $otherField = $('input[name="industry_other"]').parent().parent();

    function setHidden(hide) {
        $.each($toHide, function(idx, el) {
            $(el)[hide === true ? 'show' : 'hide']();
        });
    };

    function setOther(hide) {
        $otherField[hide === true ? 'show' : 'hide']();
    };

    function refresh() {
        setHidden(_.indexOf(matches, $toWatch.val()) > -1);
        setOther(_.indexOf(other_match, $toWatch.val()) > -1);
    };

    $toWatch.on('change', refresh);

    refresh();
});

