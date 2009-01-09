$(document).ready(function() {
    // Confirm language and template change if page is not saved
    $.each(["language", "template"], function(i, label) {
        var select = $('#id_'+label);
        if (select.length > 0) {
            var index = select[0].selectedIndex;
            select.change(function() {
                if (this.selectedIndex != index) {
                    var array = window.location.href.split('?');
                    var query = $.query.set(label, this.options[this.selectedIndex].value).toString();
                    var question = gettext("Are you sure you want to change the %(field_name)s without saving the page first?")
                    var answer = confirm(interpolate(question, {
                        field_name: select.prev().text().slice(0,-1),
                    }, true));
                    if (answer) {
                        window.location.href = array[0]+query;
                    } else {
                        this.selectedIndex = index;
                    }
                }
            });
        }
    });
    document.getElementById("id_title").focus();
    var template = $.query.get('template');
    if(template) {
        $('#id_template').find("option").each(function() {
            this.selected = false;
            if (template==this.value)
                this.selected = true;
        })
    }
    $("#id_slug").change(function() { this._changed = true; });
    $("#id_title").keyup(function() {
        var e = $("#id_slug")[0];
        if (!e._changed) {
            e.value = URLify(this.value, 64);
        }
    });
    $('#traduction-helper-select').change(function() {
        var index = this.selectedIndex;
        if(index == 0) {
            $('#traduction-helper-content').hide(); return;
        }
        var array = window.location.href.split('?');
        $.get(array[0]+'traduction/'+this.options[index].value+'/', function(html) {
            $('#traduction-helper-content').html(html);
            $('#traduction-helper-content').show();
        });
    });
    $('.revisions-list a').click( function() {
        var link = this;
        $.get(this.href, function(html) {
            $('a', $(link).parent().parent()).removeClass('selected');
            $(link).addClass('selected');
            var form_row = $(link).parents('.form-row')[0];
            if($('a.disable', form_row).length) {
                $('iframe', form_row)[0].contentWindow.document.getElementsByTagName("body")[0].innerHTML = html;
            } else {
                var formrow_textarea = $('textarea', form_row);
                formrow_textarea.attr('value', html);
                // support for WYMeditor
                if (WYMeditor) {
                    $(WYMeditor.INSTANCES).each(function(i, wym) {
                        if (formrow_textarea.attr('id') === wym._element.attr('id')) {
                            wym.html(html);
                        }
                    });
                }
            }
        });
        return false;
    });
});
