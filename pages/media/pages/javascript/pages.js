/* Common stuff used in pages_list.js as well as in pages_form.js */


var pages = {};

pages.cookie = function(name, value, options) {
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } else { // only name given, get cookie
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
};


pages.fade_color = function (elem, o) {
    o = $.extend({
        duration: 2000,     // Time [ms] the animation should last
        frame: 50,          // Time [ms] a frame lasts
        color1: 'FFFFBB',   // Color to start the animation with
        color2: 'FFFFFF',   // Color to end the animation with
        css: 'background-color', // What CSS property the color affects
        keep: false // Should the CSS property be kept or removed on the element once the animation is finished
    }, o);

    function c2d(c,i) { return parseInt(c.substr(i,2),16); }    // Color to decimal (RRGGBB => 255)
    function d2c(d) { return d.toString(16); }                  // Decimal to color (255 => FF)
    function c2a(c) { return [c2d(c,0), c2d(c,2), c2d(c,4)]; }  // Color to array (RRGGBB => [255,255,255])
    function a2c(c) { return d2c(c[0])+d2c(c[1])+d2c(c[2]); }   // Array to color ([255,255,255] => RRGGBB)

    var c = [];
    var c1 = c2a(o.color1);
    var c2 = c2a(o.color2);
    var elapsed = 0;
    var interval = setInterval(function () {
        if ((elapsed += o.frame) >= o.duration) {
            clearInterval(interval);
            elem.css(o.css, o.keep ? '#'+o.color2 : '');
        } else {
            for (var i = c1.length; i--;)
                c[i] = Math.round(c1[i]+(c2[i]-c1[i])*elapsed/o.duration);
            elem.css(o.css, '#'+a2c(c));
        }
    }, o.frame);
};


pages.update_published_icon = function (url, select, img, change_status) {
    var opt = { 0: 'draft', 1: 'published', 2: 'expired', 3: 'hidden' };
    var select_val = opt[$(select).val()];
    img.attr({
        'src': img.attr('src').replace(/icons\/.*/, 'loading.gif'),
        'alt': 'Loading'
    });
    if (change_status) {
        $.post(url+'change-status/', {'status':$(select).val()}, function(val) {
            img.attr({
                'src': img.attr('src').replace('loading.gif', 'icons/'+select_val+'.gif'),
                'alt': select_val
            });
        });
    } else {
        img.attr({
            'src': img.attr('src').replace('loading.gif', 'icons/'+select_val+'.gif'),
            'alt': select_val
        });
    }
};


$(function () {
    // Ignore clicks on help popups, just hide the help message
    $('a.popup .help, .popup a .help').click(function (e) {
        var help = $(this).css('display', 'none')
        help.closest('a').mouseout(function() {
            help.css('display', '');
        });
        e.stopPropagation();
        return false;
    });
});
