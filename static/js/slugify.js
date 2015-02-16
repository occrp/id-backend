(function($) {

    function slugify(text) {
        text = text.replace(/[^a-zA-Z\s]+/ig, '');
        text = text.replace(/\s/gi, "_");
        return text;
    }

    function registerSlugify() {
        $('.slug_source').keyup(function() {
            var $this = $(this);
            var value = $this.val();

            if (value !== undefined && value !== null) {
                $('.slug_target').val(slugify(value).toLowerCase());
            }
        });
    }

    $(document).ready(registerSlugify);

})(window.jQuery);
