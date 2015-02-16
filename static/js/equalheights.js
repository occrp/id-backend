/*!
 * Simple jQuery Equal Heights
 *
 * Copyright (c) 2013 Matt Banks
 * Dual licensed under the MIT and GPL licenses.
 * Uses the same license as jQuery, see:
 * http://docs.jquery.com/License
 *
 * @version 1.5.1
 *
 * David Wolfe, Peter Darrow adjusted to make it dynamic; depends on underscore
 *  Currently assumes 'style' attribute isn't being used by anyone else...
 */

(function($) {
    $.fn.equalHeights = function() {
        var maxHeight = 0,
        $this = $(this);

        $this.removeAttr('style');
        $this.each( function() {
            var height = $(this).innerHeight();

            if ( height > maxHeight ) { maxHeight = height; }
        });

        return $this.css('height', maxHeight);
    };

    // auto-initialize plugin
    run_equalsize = function() {
        $('[data-equal]').each(function(){
            var $this = $(this),
            target = $this.data('equal');
            $this.find(target).equalHeights();
        });
    };

    $(document).ready(run_equalsize);
    $(window).resize(_.debounce(run_equalsize, 200));
})(window.jQuery);
