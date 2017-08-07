/* Initialization of the change_form page - this script is run once everything is ready. */
"use strict";

$(function() {

    if(!$("body").hasClass("change-form") && !$("body").hasClass("grp-change-form")) {
      return;
    }

    $('iframe').iFrameResize({maxHeight:800});

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
    var status_select = $('#id_status');
    var opt = ({ 0: 'draft', 1: 'published', 2: 'expired', 3: 'hidden' })[status_select.val()];
    var img = $('<img src="'+static_url+'pages/images/icons/'+opt+'.gif" alt="'+opt+'" />').insertAfter(status_select);
    // disable ajax post if page not already created (add view)
    var change_status = (typeof(add_form) !== 'undefined' && add_form) ? 0 : 1;

    status_select.change(function(e) {
        pages.update_published_icon('', status_select, img, change_status);
    });

    var comfirm_msg = gettext('You may lose any changes you have done to the page. Are you sure?');

    // Confirm template change if page is not saved
    var template_select = $('#id_template');
    if (template_select.length) {
        var orig_value = template_select.val();
        template_select.change(function() {
            if(confirm(comfirm_msg)) {
                $('input[name=_continue]').click();
                orig_value = template_select.val();
            } else {
                template_select.val(orig_value);
            }
        });
    };

    $('.js-confirm-change').click(function(e){
        if(confirm(comfirm_msg)) {
            
        } else {
            e.preventDefault();
        }
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
                    // if($('input, textarea', formrow).length > 1) {
                    //   var values = html.split("\\");
                    //   $('input, textarea', formrow).each(function(i, e) {
                    //        $(e).val(values[i]);
                    //   });
                    //   return;
                    // }

                    // support for File Input
                    // debugger
                    var fileinput = $('input[type="file"]', formrow);
                    if(fileinput.length > 0) {
                        var revision_name = fileinput.attr('name') + '-revision';
                        var revision_input = $('[name="' + revision_name + '"]');
                        if(revision_input.length === 0) {
                            revision_input = $('<input type="text">');
                            revision_input.attr('name', revision_name);
                            select.after(revision_input);
                        }                        
                        revision_input.val(html);
                        return;
                    }

                    // support for Text Input
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
        return;
    });

    $('.js-confirm-delete').click(function() {
        return confirm(gettext('Are you sure you want to delete this content?'));
    });
});
