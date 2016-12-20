/* Initialization of the change_list page - this script is run once everything is ready. */
$(function($) {
    "use strict";

    if(!$("body").hasClass("change-list-pages")) {
      return;
    }
    if(!window.pages) {
        return;
    }
    var pages = window.pages;
    var static_url = window.static_url;
    var django = window.django;
    var action = false;
    var selected_page = false;
    var changelist = $('#page-list');

    if(!window.gettext) {
        window.gettext = function(str) {
            return str;
        };
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
                if ($.inArray(i, expanded) !== -1) {
                    $('#c'+i).addClass('expanded loading');
                    add_children(i, callback);
                }
            });
            if(callback) {
                callback(children);
            }
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
        if ($.inArray(id, expanded) === -1) {
            expanded.push(id);
            set_expanded(expanded);
        }
    }

    // Remove a page id from the list of expanded pages
    function rem_expanded(id) {
        var expanded = get_expanded();
        var index = $.inArray(id, expanded);
        if (index !== -1) {
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
        $('.publish-select', elements).change(function() {
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
                update_actions();
            }
        );
    }

    function expand_collapse(link, e) {
        e.preventDefault();
        var id = link.attr('id').substring(1);
        if (link.toggleClass('expanded').hasClass('expanded')) {
            add_expanded(id);
            add_children(id, function (children) {
                init_publish_hanlder(children);
                // Update the move and add links of the inserted rows
                if (action === 'move') {
                    var selected_row = $('#page-row-'+selected_page);
                    selected_row.addClass('selected');
                    selected_row.add(get_children(selected_page));
                    selected_row.addClass('highlighted');
                    // this could become quite slow with a lot of pages
                    $('tr:not(.highlighted)', changelist).addClass('insertable');
                } else if (action === 'add') {
                    $('#page-row-'+selected_page).addClass('highlighted insertable');
                }
            });
        } else {
            rem_expanded(id);
            rem_children(id);
        }
    }

    function move_target(link, e) {
        e.preventDefault();
        var position = link.attr('class').match(/left|right|first-child/)[0];
        var id = link.parent().attr('id').split('move-target-')[1];
        var row = $('#page-row-'+selected_page);

        changelist.removeClass('insert-add insert-move');
        $('tr', changelist).removeClass('selected insertable');
        $('.expand-collapse', row).remove();
        $('.insert', row).after('<img class="insert-loading" src="'+static_url+'pages/images/loading.gif" alt="Loading" />');

        if (action === 'move') {
            move_page(selected_page, position, id);
        } else if (action === 'add') {
            window.location.href += 'add/'+$.query.set('target', id).set('position', position).toString();
        }
    }

    function add_link(link, e) {
        e.preventDefault();
        reset_states();
        action = 'add';
        selected_page = link.attr('id').split('add-link-')[1];
        changelist.addClass('insert-add');
        $('#page-row-'+selected_page).addClass('selected').addClass('highlighted insertable');
    }

    function move_link(link, e) {
        e.preventDefault();
        reset_states();
        action = 'move';
        selected_page = link.attr('id').split('move-link-')[1];
        changelist.addClass('insert-move');
        $('#page-row-'+selected_page).addClass('selected').add(
            get_children(selected_page)
        ).addClass('highlighted');
        $('tr:not(.highlighted)', changelist).addClass('insertable');
    }

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
                move_link(link, e);
            }
            // Ask where to insert the new page
            else if (link.hasClass('addlink')) {
                add_link(link, e);
            }
            // Move or add the page and come back to the initial state
            else if (link.hasClass('move-target')) {
                move_target(link, e);
            }
            // Expand or collapse pages
            else if (link.hasClass('expand-collapse')) {
                expand_collapse(link, e);
            }
        }
    });

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
        var insert_at = false;
        var trs;
        var source_left, source_right, source_tree_id;
        var all_lines;

        $("#page-list").on("mousedown", ".movelink", function(e) {
            all_lines = $("#page-table-dnd tbody tr");
            down = this;
            line = $($(this).parents("tr").get(0));
            line_id = line.attr('id').split('page-row-')[1];
            insert_at = 'above'
            move_y = 0;
            start_y = e.pageY;
            source_left = parseInt(line.data('mptt-left'), 10);
            source_right = parseInt(line.data('mptt-right'), 10);
            source_tree_id = parseInt(line.data('mptt-tree-id'), 10);
            return false;
        });

        $("#page-list").on("mousemove", function(e) {
            if(down) {
              move_y = start_y - e.pageY;
              // we have a drag an drop
              if(Math.abs(move_y) > 8 && !drag_initiated) {
                indicator = $(".drag-indicator");
                indicator.show();
                $(".moved-page-title").text(line.find(".title").text());
                drag_initiated = true;
                $(line).css("opacity", "0.5");
                trs = $("#page-list tbody tr");
                trs.each(function(i, el) {
                  var possible_target = $(el);
                  var left = parseInt(possible_target.data('mptt-left'), 10);
                  var right = parseInt(possible_target.data('mptt-right'), 10);
                  var tree_id = parseInt(possible_target.data('mptt-tree-id'), 10);
                  if(source_tree_id === tree_id && left > source_left && right < source_right) {
                    return;
                  }
                  lines_position.push(
                    {el:el, pos:possible_target.position(), h:possible_target.height()}
                  );
                });
              }
              if(drag_initiated) {
                indicator.show();
                indicator.css("top", e.pageY-22 + "px");
                indicator.css("left", e.pageX-8 + "px");
                var i;
                choosen_line = lines_position[0];
                var distance = 10000;
                for(i = 0; i<lines_position.length; i++) {
                  var _line = lines_position[i];
                  var top = Math.abs((_line.pos.top + _line.h / 2) - e.pageY) ;
                  if(top < distance) {
                      distance = top;
                      choosen_line = _line;
                  }
                }

                all_lines.removeClass('target-insert-first-child target-insert-left target-insert-right highlighted');
                var target_line_id = choosen_line.el.id.split('page-row-')[1];
                if(choosen_line && target_line_id != line_id) {
                  var percent = (e.pageY - choosen_line.pos.top) / parseFloat(choosen_line.h, 10);
                  insert_at = 'first-child';
                  if(percent < 0.30) {
                    insert_at = 'left';
                  }
                  if(percent > 0.70) {
                    insert_at = 'right';
                  }
                  $(choosen_line.el).addClass('highlighted').addClass('target-insert-' + insert_at);
                }
              }
            }
            return false;
        });

        $(document).on("mouseup", function(e) {
            if(down == false) {
                return;
            }

            // release
            var target_line_id = choosen_line.el.id.split('page-row-')[1];

            if(drag_initiated && target_line_id != line_id) {
              drag_initiated = false;
                move_page(line_id, insert_at, target_line_id);
            }

            $(line).css("opacity", "1");
            $(".drag-indicator").hide();
            down = false;
            drag_initiated = false;
            lines_position = [];
        });

    }
    bind_sortable();
});
