wymeditor_filebrowser = function(wym, wdw) {
  // the URL to the Django filebrowser, depends on your URLconf
  var fb_url = '/admin/filebrowser/';
  
  var dlg = jQuery(wdw.document.body);
  if (dlg.hasClass('wym_dialog_image')) {
    // this is an image dialog
    
    dlg.find('.wym_src').css('width', '200px').attr('id', 'filebrowser')
      .after('<a id="fb_link" title="Filebrowser" href="#">Filebrowser</a>');
    dlg.find('fieldset')
      .append('<a id="link_filebrowser"><img id="image_filebrowser" /></a>' +
              '<br /><span id="help_filebrowser"></span>');
    dlg.find('#fb_link')
      .click(function() {
        fb_window = wdw.open(fb_url + '?pop=1', 'filebrowser', 'height=600,width=840,resizable=yes,scrollbars=yes');
        fb_window.focus();
        return false;
      });
  }
  
  if (dlg.hasClass('wym_dialog_link')) {
    // this is an image dialog

    dlg.find('.wym_href').css('width', '200px').attr('id', 'filebrowser')
      .after('<a id="fb_link" title="Filebrowser" href="#">Filebrowser</a>');
    dlg.find('fieldset')
      .append('<a id="link_filebrowser"><img id="image_filebrowser" /></a>' +
              '<br /><span id="help_filebrowser"></span>');
    dlg.find('#fb_link')
      .click(function() {
        fb_window = wdw.open(fb_url + '?pop=1', 'filebrowser', 'height=600,width=840,resizable=yes,scrollbars=yes');
        fb_window.focus();
        return false;
      });
  }
}
