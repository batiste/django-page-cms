/* Initialization of the change_form page - this script is run once everything is ready. */
"use strict";

$(function() {

    if(!$("body").hasClass("change-form")) {
      return;
    }

    // Hide form rows containing only hidden inputs
    $('.form-row').each(function() {
        if (!$('p, label, select, input:not([type=hidden])', this).length) {
            $(this).hide();
        }
    });

    // Focus the title
    $('#id_title').focus();

    // Automatically update the slug when typing the title
    var slug_auto = true;
    var slug = $("#id_slug").change(function() {
        slug_auto && (slug_auto = false);
    });
    $("#id_title").keyup(function() {
        slug_auto && slug.val(URLify(this.value, 64));
    });

    // Set the publication status
    var select = $('#id_status');
    var opt = ({ 0: 'draft', 1: 'published', 2: 'expired', 3: 'hidden' })[select.val()];
    var img = $('<img src="'+static_url+'pages/images/icons/'+opt+'.gif" alt="'+opt+'" />').insertAfter(select);
    // disable ajax post if page not already created (add view)
    var change_status = (typeof(add_form) !== 'undefined' && add_form) ? 0 : 1;

    select.change(function(e) {
        pages.update_published_icon('', select, img, change_status);
    });

    // Confirm language and template change if page is not saved
    // this code doesn't work with languages
    $.each(['language', 'template'], function(i, label) {
        var select = $('#id_'+label);
        if (select.length) {
            var orig_ = select.val();
            select.change(function() {
                if(confirm(gettext('You may lose any changes you have done to the page. Are you sure?')))
                    $('input[name=_continue]').click();
            });
        };
    });

    if(document.location.search) {
        // append query arguments to the language selectors;
        $('.language_choice_widget').each(function(_, widget) {
            var search = document.location.search.substring(1);
            // remove the current language (if any);
            var params = search.split('&');
            var new_params = "";
            for(var i=0; i<params.length; i++) {
                if(params[i].split('=')[0] != 'language') {
                    new_params += params[i];
                }
            }
            $(widget).find('li a').each(function(_, s) {
                s.href = s.href + "&" + new_params;
            });
        });
    }

    // Disable the page content if the page is a redirection
    /*
    // To fix if we use placeholder in templates for META or extra content

    var redirect = $('#id_redirect_to').change(update_redirect);
    var affected = $('.form-row:has(#id_language), .form-row:has(#id_template), .module-content .form-row')
        .css('position', 'relative');
    var overlay = $('<div class="overlay"></div>').css({
            'display': 'none',
            'position': 'absolute',
            'z-index': '1000',
            'top': '0',
            'left': '0',
            'height': '100%',
            'width': '100%',
            'opacity': '0.66',
            'background': 'white'
        }).appendTo(affected);
    function update_redirect() {
        redirect.val() ? overlay.show() : overlay.hide();
    }
    update_redirect();
    */

    // Content revision selector
    $('.revisions').change(function () {
        var select = $(this);
        var val = select.val();
        if (val) {
            $.get(val, function (html) {
                var formrow = select.closest('.form-row');

                if ($('a.disable', formrow).length) {
                    $('iframe', formrow)[0].contentWindow.document.getElementsByTagName("body")[0].innerHTML = html;
                } else {
                    // support for multiple input widget
                    if($('input, textarea', formrow).length > 1) {
                      var values = html.split("\\");
                      $('input, textarea', formrow).each(function(i, e) {
                         $(e).val(values[i]);
                      });
                      return false;
                    }
                    // support for TextInput
                    $('input', formrow).val(html);
                    // support for TextArea
                    var formrow_textarea = $('textarea', formrow).val(html);
                    // support for WYMeditor
                    if (window.WYMeditor !== undefined) {
                        $(WYMeditor.INSTANCES).each(function (i, wym) {
                            if (formrow_textarea.attr('id') === wym._element.attr('id')) {
                                wym.html(html);
                            }
                        });
                    }
                    // support for TinyMCE
                    if (window.tinyMCE !== undefined) {
                        var editor = tinyMCE.get(formrow_textarea.attr('id'));
                        if (editor !== undefined) {
                            editor.setContent(html);
                        }
                    }
                }
            });
        }
        return false;
    });

    $('.js-confirm-delete').click(function() {
        return confirm(gettext('Are you sure you want to delete this content?'));
    });
});
