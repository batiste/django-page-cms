jQuery.cookie = function(name, value, options) {
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

function hide_children(obj, id){
    obj.visibles = new Array();
    $('tr.child-of-' + id + ':visible').each(function(){
        var the_id = this.id.substring(9);
        obj.visibles.push(the_id);
        $(this).hide();
    });
}

function restore_children(obj, id){
    for(the_id in obj.visibles){
        $('tr#page-row-' + obj.visibles[the_id]).show();
    }
}

$(window).unload( function (){
    pushVisibles();
});

function pushVisibles() {
   var visibles = new Array();
    $('tr:visible').each(function(){
         visibles.push(this.id.substring(9));
    });
    $.cookie('tree_visibles', visibles.join(',').substring(1));
}

function bindTreeCollapseEvents() {
    var visibles = $.cookie('tree_visibles');
    if(visibles){
        visibles = visibles.split(',');
    }
    for(i in visibles) {
        $('tr#page-row-' + visibles[i]).show();
        var rel = $('tr#page-row-' + visibles[i] + ' a.collapse')[0].rel
        if (rel){
            $('a#c' + rel).removeClass('collapsed');
        }
    }
    $("a.collapse").click(function() {
        var the_id = this.id.substring(1);
        var clicked = $(this);
        clicked.toggleClass('collapsed');
        $("a[rel=" + the_id + "]").each(function() {
            id = this.id.substring(1);
            if (clicked.hasClass('collapsed')) {
                $(this).parent().parent().hide();
                hide_children(this, id);
            } else {
                $(this).parent().parent().show();
                restore_children(this, id);
            }
        });
        return false;
    });
}
