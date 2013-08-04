/* Initialization of the change_list page - this script is run once everything is ready. */
"use strict";

$(function () {

    if(!$("body").hasClass("change-list")) {
      return;
    }

    var action = false;
    var selected_page = false;
    var changelist = $('#changelist');

    if(!window.gettext) {
        window.gettext = function(str) {
            return str;
        }
    }

    function update_actions() {
        // let django admin js know about the new/removed checkboxes
        django.jQuery("tr input.action-select").actions();
    }

    function reset_states() {
        action = selected_page = '';
        changelist.removeClass('insert-add insert-move');
        $('tr', changelist).removeClass('insertable highlighted selected');
    }

    // Get an array of the TR elements that are children of the given page id
    // The list argument should not be used (it is only used by the recursion)
    function get_children(id, list) {
        list = list || [];
        $('.child-of-'+id).each(function () {
            list.push(this);
            get_children(this.id.substring(9), list);
        });
        return list;
    }

    // Request and insert to the table the children of the given page id
    function add_children(id, callback) {
        var page_row = $('#page-row-'+id);
        var link = $('.expand-collapse', page_row).addClass('loading');

        $.get(id+'/sub-menu/', function (html) {
            page_row.after(html);
            link.removeClass('loading');
            var expanded = get_expanded();
            var children = $('.child-of-'+id, changelist).each(function () {
                var i = this.id.substring(9);
                if ($.inArray(i, expanded) != -1) {
                    $('#c'+i).addClass('expanded loading');
                    add_children(i, callback);
                }
            });
            callback && callback(children);
            update_actions();
        });
    }

    // Remove the children of the given page id from the table
    function rem_children(id) {
        $('.child-of-'+id, changelist).each(function () {
            rem_children(this.id.substring(9));
            $(this).remove();
        });
        update_actions();
    }

    // Add a page id to the list of expanded pages
    function add_expanded(id) {
        var expanded = get_expanded();
        if ($.inArray(id, expanded) == -1) {
            expanded.push(id);
            set_expanded(expanded);
        }
    }

    // Remove a page id from the list of expanded pages
    function rem_expanded(id) {
        var expanded = get_expanded();
        var index = $.inArray(id, expanded);
        if (index != -1) {
            // The following code is based on J. Resig's optimized array remove
            var rest = expanded.slice(index+1);
            expanded.length = index;
            expanded.push.apply(expanded, rest);
            set_expanded(expanded);
        }
    }

    // Get the list of expanded page ids from the cookie
    function get_expanded() {
        var cookie = pages.cookie('tree_expanded');
        return cookie ? cookie.split(',') : [];
    }

    // Save the list of expanded page ids to the cookie
    function set_expanded(array) {
        pages.cookie('tree_expanded', array.join(','), { 'expires': 14 }); // expires after 12 days
    }

    // Add the event hanlder to handle the changes of the publication status through ajax
    // In IE, event delegation doesn't work for the onchange event, so we do it the old way
    function init_publish_hanlder(elements) {
        $('.publish-select', elements).change(function (e) {
            var url = this.name.split('status-')[1]+'/';
            var img = $(this).parent().find('img');
            pages.update_published_icon(url, this, img, 1);
        });
    }

    init_publish_hanlder(changelist);

    function move_page(selected_page, position, id) {
        $.post(selected_page+'/move-page/',
            { position: position, target: id },
            function (html) {
                $('#page-list').html(html);
                init_publish_hanlder(changelist);
                pages.fade_color($('#page-row-'+selected_page).add(get_children(selected_page)));
                action = selected_page = '';
                //bind_sortable()
                update_actions();
            }
        );
    };

    // let's start event delegation
    changelist.click(function (e) {
        var target = $(e.target);
        var link = target.closest('a').andSelf().filter('a');

        if (!target.hasClass('help') && link.length) {
            // Toggles a previous action to come back to the initial state
            if (link.hasClass('cancellink')) {
                reset_states();
                return false;
            }
            // Ask where to move the page to
            else if (link.hasClass('movelink')) {
                reset_states();
                action = 'move';
                selected_page = link.attr('id').split('move-link-')[1];
                changelist.addClass('insert-move');
                $('#page-row-'+selected_page).addClass('selected').add(
                    get_children(selected_page)
                ).addClass('highlighted');
                $('tr:not(.highlighted)', changelist).addClass('insertable');
                return false;
            }
            // Ask where to insert the new page
            else if (link.hasClass('addlink')) {
                reset_states();
                action = 'add';
                selected_page = link.attr('id').split('add-link-')[1];
                changelist.addClass('insert-add');
                $('#page-row-'+selected_page).addClass('selected').addClass('highlighted insertable');
                return false;
            }
            // Move or add the page and come back to the initial state
            else if (link.hasClass('move-target')) {
                var position = link.attr('class').match(/left|right|first-child/)[0];
                var id = link.parent().attr('id').split('move-target-')[1];
                var row = $('#page-row-'+selected_page);

                changelist.removeClass('insert-add insert-move');
                $('tr', changelist).removeClass('selected insertable');
                $('.expand-collapse', row).remove();
                $('.insert', row).after('<img class="insert-loading" src="'+static_url+'pages/images/loading.gif" alt="Loading" />');

                if (action == 'move') {
                    move_page(selected_page, position, id);
                } else if (action == 'add') {
                    window.location.href += 'add/'+$.query.set('target', id).set('position', position).toString();
                }
                return false;
            }
            // Expand or collapse pages
            else if (link.hasClass('expand-collapse')) {
                var id = link.attr('id').substring(1);
                if (link.toggleClass('expanded').hasClass('expanded')) {
                    add_expanded(id);
                    add_children(id, function (children) {
                        init_publish_hanlder(children);
                        // Update the move and add links of the inserted rows
                        if (action == 'move') {
                            var selected_row = $('#page-row-'+selected_page)
                            selected_row.addClass('selected')
                            selected_row.add(get_children(selected_page))
                            selected_row.addClass('highlighted');
                            // this could become quite slow with a lot of pages
                            $('tr:not(.highlighted)', changelist).addClass('insertable');
                        } else if (action == 'add') {
                            $('#page-row-'+selected_page).addClass('highlighted insertable');
                        }
                    });
                } else {
                    rem_expanded(id);
                    rem_children(id);
                }
                return false;
            }
        }
    });


    var drag_clientx = false;
    var insert_position = 'right';
    // will be better of not rewritting the table everytime
    function bind_sortable() {
        // Initialise the table for drag and drop

        var down = false;
        var move_y = 0;
        var start_y = 0;
        var line = false;
        var line_id = false;
        var indicator = false;
        //indicator.css("position", "absolute");
        //indicator.hide();
        var drag_initiated = false;
        var lines_position = [];
        var choosen_line = false;
        var trs;

        $("#page-list").on("mousedown", ".movelink", function(e) {
            down = this;
            line = $($(this).parents("tr").get(0));
            line_id = line.attr('id').split('page-row-')[1];
            move_y = 0;
            start_y = e.pageY;
            return false;
        });

        $("#page-list").on("mousemove", function(e) {
            if(down) {
              move_y = start_y - e.pageY;
              // we have a drag an drop
              if(Math.abs(move_y) > 8 && !drag_initiated) { 
                indicator = $(".drag-indicator");
                indicator.text(line.find(".title").text());
                indicator.show();
                drag_initiated = true;
                $(line).css("opacity", "0.5");
                trs = $("#page-list tbody tr").not(line).not($(".child-of-"+line_id));
                trs.each(function(i, el) {
                  lines_position.push(
                    {line:el, pos:$(el).position().top + $(el).height() / 2}
                  );
                }); 
              }
              if(drag_initiated) {
                indicator.show();
                indicator.css("top", e.pageY-22 + "px");
                indicator.css("left", e.pageX-8 + "px");
                var i;
                choosen_line = lines_position[0].line;
                var distance = 10000;
                for(i = 0; i<lines_position.length; i++) {
                  if(Math.abs(lines_position[i].pos - e.pageY) < distance) {
                      distance = Math.abs(lines_position[i].pos - e.pageY);
                      choosen_line = lines_position[i].line;
                  }
                }
                $("#page-list tbody tr").removeClass("highlighted");
                $(choosen_line).addClass("highlighted");
              }
            }
            return false;
        });

        $(document).on("mouseup", function(e) {
            // release
            if(drag_initiated) {
              drag_initiated = false;
              var dialog = $(".drag-dialog");
              dialog.css("top", $(choosen_line).position().top+"px");
              dialog.css("left", (e.pageX - 20) +"px");
              dialog.show();
              /*var target = choosen_line.id.split('page-row-')[1];
              move_page(line_id, "first-child", target);*/
              // choosen_line = false;
            }

            $(line).css("opacity", "1");
            $(".drag-indicator").hide();
            down = false;
            drag_initiated = false;
            lines_position = [];
        });

        $(document).on("click", ".move-top", function(e) {
            var target = choosen_line.id.split('page-row-')[1];
            move_page(line_id, "left", target);
            return false;
        });

        $(document).on("click", ".move-first-child", function(e) {
            var target = choosen_line.id.split('page-row-')[1];
            move_page(line_id, "first-child", target);
            return false;
        }); 

        $(document).on("click", ".move-bottom", function(e) {
            var target = choosen_line.id.split('page-row-')[1];
            move_page(line_id, "right", target);
            return false;
        });

        $(document).on("click", ".move-undo", function(e) {
            $(".drag-dialog").hide();
            $("#page-list tbody tr").removeClass("highlighted");
            return false;
        });

        $(document).on("click", function(e) {
            $("#page-list tbody tr").removeClass("highlighted");
            $(".drag-dialog").hide();
        }); 

    }
    bind_sortable();
});
