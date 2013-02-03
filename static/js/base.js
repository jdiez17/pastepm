$(function(){
	resizeEditor();
});

$(window).resize(resizeEditor);

function resizeEditor(){
	var width = $('body').outerWidth() - 60;
	$(".ace_editor").css('width', width + 'px');
}

$(document).ready(function() {
	$("#button-save").click(function() {
		text = editor.getSession().getDocument().getValue();
		console.log(text);
		$.ajax({
			type: "POST",
			url: "/post",
			data: {'content': text},
			success: function(data, res, xhr) {
				window.location.href = data;
			}
		});
	});
});