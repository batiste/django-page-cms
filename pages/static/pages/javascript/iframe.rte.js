
$(function () {
	var attributes = $('<div id="attributes">'+
		'<label><span>width </span><input type="text" id="width"></input></label>'+
		'<label><span>height </span><input type="text" id="height"></input></label>'+
		'<label><span> </span><i class="fa fa-trash" aria-hidden="true" id="remove"></i></label>'+
		'</div>');
	var img, w, h;
	w = attributes.find('#width');
	h = attributes.find('#height');

	$(document).on('change keyup', '#width', function(e){
		img.attr('width', w.val());
	});
	$(document).on('change keyup', '#height', function(e){
		img.attr('height', h.val());
	});
	$(document).on('click', '#remove', function(e){
		img.remove();
		attributes.remove();
	});

	$(document).on('click', 'img', function(e) {
		img = $(e.target);
		w.val(img.attr('width'));
		h.val(img.attr('height'));
		attributes.css('top', e.pageY);
		attributes.css('left', e.pageX);
		$(document.body).append(attributes);
		e.preventDefault();
		return false;
	});

	$(document).on('click', '#attributes', function(e) {
		e.preventDefault();
		return false;
	});

	$(document).on('click', function(e) {
		attributes.remove();
	});

});