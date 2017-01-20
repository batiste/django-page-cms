

$(function () {
	var attributes = $('<div id="attributes">'+
		'<label>width <input type="text" id="width"></input></label>'+
		'<label>height <input type="text" id="height"></input></label>'+
		'</div>');
	var img, w, h;
	w = attributes.find('#width');
	h = attributes.find('#height');

	$(document).on('change keyup', '#width', function(e){
		console.log(w.val())
		img.attr('width', w.val());
	});
	$(document).on('change keyup', '#height', function(e){
		img.attr('height', h.val());
	});

	$(document).on('click', 'img', function(e) {
		console.log(e)
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