/*
 * jQuery RTE plugin 0.2 - create a rich text form for Mozilla, Opera, and Internet Explorer
 *
 * Copyright (c) 2007 Batiste Bieler
 * Distributed under the GPL (GPL-LICENSE.txt) licenses.
 */

// define the rte light plugin
$(function () {


jQuery.fn.rte = function(static_url, media_url) {

    if(document.designMode || document.contentEditable) {
        $(this).each( function(){
            var textarea = $(this);
            enableDesignMode(textarea);
        });
    }

    function formatText(iframe, command, option) {
        iframe.contentWindow.focus();
        try{
            iframe.contentWindow.document.execCommand(command, false, option);
        } catch(e){console.log(e);}
        iframe.contentWindow.focus();
    }

    function tryEnableDesignMode(iframe, doc, callback) {
        try {
            iframe.contentWindow.document.open();
            iframe.contentWindow.document.write(doc);
            iframe.contentWindow.document.close();
        } catch(error) {
            console.log(error);
        }
        if (document.contentEditable) {
            iframe.contentWindow.document.designMode = "On";
            callback();
            return true;
        }
        else if (document.designMode !== null) {
            try {
                iframe.contentWindow.document.designMode = "on";
                callback();
                return true;
            } catch (error) {
                console.log(error);
            }
        }
        setTimeout(function(){tryEnableDesignMode(iframe, doc, callback);}, 250);
        return false;
    }

    function enableDesignMode(textarea) {
        // need to be created this way
        var iframe = document.createElement("iframe");
        iframe.frameBorder=0;
        iframe.frameMargin=0;
        iframe.framePadding=0;
        iframe.height=200;
        if(textarea.attr('class'))
            iframe.className = textarea.attr('class');
        if(textarea.attr('id'))
            iframe.id = textarea.attr('id');
        if(textarea.attr('name'))
            iframe.title = textarea.attr('name');
        textarea.after(iframe);
        var css = "";
        css = "<link type='text/css' rel='stylesheet' href='"+static_url+"css/font-awesome.min.css' />";
        css = css + "<link type='text/css' rel='stylesheet' href='"+static_url+"css/rte.css' />";
        var content = textarea.val();
        // Mozilla need this to display caret
        if($.trim(content)==='')
            content = '<br>';
        var scripts = "<script src='"+static_url+"javascript/jquery.js'></script><script src='" + 
            static_url+"javascript/iframe.rte.js'></script>";

        var doc = "<html><head>"+css+scripts+"</head><body id='frameBody'>"+content+"</body></html>";
        tryEnableDesignMode(iframe, doc, function() {
            $("#toolbar-"+iframe.title).remove();
            $(iframe).before(toolbar(iframe));
            textarea.remove();
        });
    }

    function disableDesignMode(iframe, submit) {
        var attr = $(iframe.contentWindow.document.getElementById("attributes"));
        attr.remove();
        var content = iframe.contentWindow.document.getElementById("frameBody").innerHTML;
        
        var textarea;
        if(submit === true) {
            textarea = $('<input type="hidden" />');
        } else {
            textarea = $('<textarea cols="40" rows="10"></textarea>');
        }
        textarea.val(content);
        t = textarea.get(0);
        if(iframe.className)
            t.className = iframe.className;
        if(iframe.id)
            t.id = iframe.id;
        if(iframe.title)
            t.name = iframe.title;
        $(iframe).before(textarea);
        if(submit!==true) {
            $(iframe).remove();
        }
        return textarea;
    }

    function toolbar(iframe) {
        
        var tb = $("<div class='rte-toolbar' id='toolbar-"+iframe.title+"'><div>\
            <p><i class='fa fa-font' aria-hidden='true'></i>\
                <select>\
                    <option value=''>Bloc style</option>\
                    <option value='p'>Paragraph</option>\
                    <option value='h3'>Title</option>\
                </select>\
            </p>\
            <p>\
                <a href='#' class='bold'><i class='fa fa-bold' aria-hidden='true'></i></a>\
                <a href='#' class='italic'><i class='fa fa-italic' aria-hidden='true'></i></a>\
            </p>\
            <p>\
                <a href='#' class='unorderedlist'><i class='fa fa-list-ul' aria-hidden='true'></i></a>\
                <a href='#' class='link'><i class='fa fa-link' aria-hidden='true'></i></a>\
                <a href='#' title='insert image from the media library' class='image-lookup'><i class='fa fa-file-image-o' aria-hidden='true'></i></a>\
                <a href='#' title='insert external image' class='image'><i class='fa fa-external-link-square' aria-hidden='true'></i></a>\
                <a href='#' title='disable edit' class='disable'><i class='fa fa-code' aria-hidden='true'></i></a>\
            </p></div></div>");

        $('select', tb).change(function(){
            var index = this.selectedIndex;
            if( index!=0 ) {
                var selected = this.options[index].value;
                formatText(iframe, "formatblock", '<'+selected+'>');
            }
        });

        $('.bold', tb).click(function(){ formatText(iframe, 'bold');return false; });
        $('.italic', tb).click(function(){ formatText(iframe, 'italic');return false; });
        $('.unorderedlist', tb).click(function(){ formatText(iframe, 'insertunorderedlist');return false; });

        $('.link', tb).click(function() {
            var p=prompt("URL:");
            if(p)
                formatText(iframe, 'CreateLink', p);
            return false; 
        });

        $('.image', tb).click(function() {
            var p = prompt("image URL:");
            if(p)
                formatText(iframe, 'InsertImage', p);
            return false; 
        });

        var oldDismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
        var oldDismissAddRelatedObjectPopup = window.dismissAddRelatedObjectPopup;

        function insertHTML(url) {
          var id = "rand" + Math.random();
          var doc = iframe.contentWindow.document;
          if(url.match(/(jpeg|jpg|png)$/)) {
            html = "<img width='200' src='" + url + "' id=" + id + ">";
          } else {
            html = "<a href='" + url + "' id=" + id + ">"+url+"</a>";
          }
          
          if(document.all) {
            var range = doc.selection.createRange();
            range.pasteHTML(html);
            range.collapse(false);
            range.select();
          } else {
            doc.execCommand("insertHTML", false, html);
          }
          return doc.getElementById(id);
        };

        function dismissRelatedLookupPopup(win, chosenId) {
            $.get('/admin/pages/page/' + chosenId + '/media-url/', function(response) {
                insertHTML(media_url + response);
            });
            win.close();
            window.dismissRelatedLookupPopup = oldDismissRelatedLookupPopup;
            window.dismissAddRelatedObjectPopup = oldDismissAddRelatedObjectPopup;
        }

        function showMediaAdminPopup() {
            var name = 'mediaWindowSelect';
            var href = '/admin/pages/media/?_to_field=id&_popup=1';
            window.dismissRelatedLookupPopup = dismissRelatedLookupPopup;
            window.dismissAddRelatedObjectPopup = dismissRelatedLookupPopup;
            var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
            win.focus();
            return false;
        }

         $('.image-lookup', tb).click(function(e) {
             e.preventDefault();
             showMediaAdminPopup();
             return false;
         });
        
        $('.disable', tb).click(function() {
            var txt = disableDesignMode(iframe);
            var edm = $('<a href="#">Enable design mode</a>');
            tb.empty().append(edm);
            edm.click(function(){
                enableDesignMode(txt);
                return false;
            });
            return false; 
        });

        $(iframe).parents('form').submit(function() {
            disableDesignMode(iframe, true);
        });

        var iframeDoc = $(iframe.contentWindow.document);
        
        var select = $('select', tb)[0];
        iframeDoc.mouseup(function() {
            setSelectedType(getSelectionElement(iframe), select);
            return true;
        });
        iframeDoc.keyup(function() {
            setSelectedType(getSelectionElement(iframe), select);
            var body = $('body', iframeDoc);
            var bodyHeight = $(iframeDoc[0].body).height();
            if(body.scrollTop() > 0) {
                var new_height = Math.min(400, Math.max(200, bodyHeight+16));
                $(iframe).css('min-height', new_height);
            }
            return true;
        });
        
        return tb;
    }
        
    function setSelectedType(node, select) {
        while(node.parentNode) {
            var nName = node.nodeName.toLowerCase();
            for(var i=0;i<select.options.length;i++) {
                if(nName==select.options[i].value){
                    select.selectedIndex=i;
                    return true;
                }
            }
            node = node.parentNode;
        }
        select.selectedIndex=0;
        return true;
    }
    
    function getSelectionElement(iframe) {
        if (iframe.contentWindow.document.selection) {
            // IE selections
            selection = iframe.contentWindow.document.selection;
            range = selection.createRange();
            try {
                node = range.parentElement();
            }
            catch (e) {
                return false;
            }
        } else {
            // Mozilla selections
            try {
                selection = iframe.contentWindow.getSelection();
                range = selection.getRangeAt(0);
            }
            catch(e){
                return false;
            }
            node = range.commonAncestorContainer;
        }
        return node;
    }
};

});
