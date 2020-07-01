jQuery(function($) {
	"use strict";

	$('input[type=text]').blur(function(){
		if($.trim($(this).val()) == "")
			$(this).addClass('form-incomplete');
		else
			$(this).removeClass('form-incomplete');
	});

	$('textarea').blur(function(){
		if($.trim($(this).val()) == "")
			$(this).addClass('form-incomplete');
		else
			$(this).removeClass('form-incomplete');
	});

	$('form').submit(function(){
		event.preventDefault();

		var that = mainForm,
			url = $(that).attr('action'),
			type = $(that).attr('method'),
			dataX = {};
			
		$(that).find("[name]").each(function(){
			dataX[$(this).attr("name")] = $(this).val();
		});

		$('.notification-box').addClass('active');

		$.ajax({
			type:'POST',
			url: url,
			data: dataX,
			success: function(response){
				$('.notification-box span').html(response);
					setTimeout(function(){
						$('.notification-box').removeClass('active');
						$('.notification-box span').html("Sending...");
					}, 4000);
				}
		});
	});

	$('.sample-button-done').click(function(){
		$('#sample-form').slideUp();
	});
});