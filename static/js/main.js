jQuery(function($) {
	"use strict";

	$.validate();

	new WOW().init();
	//Variables
	var fixed_point = 0;
	var loaded = false;

	// Author Code Here
	$(window).load(function(){
		$('.owl-book').owlCarousel({
			singleItem:true,
			items:1,
			pagination:false,
			autoPlay:3000
		});
		$('.owl-reviews').owlCarousel({
			items:3,
			navigation:true,
			autoPlay:5000,
			navigationText: ["<i class='arrow_carrot-left'></i>","<i class='arrow_carrot-right'></i>"]
		});
		$('.main-nav').onePageNav({
			currentClass: 'active',
			changeHash: false,
			scrollSpeed: 400
		});
		$(".get-direction").tooltip({
		    direction: "top"
		});
		// Navbar "Breaking" Fix
		loaded = true;
		Adjust();
		$('.navbar').after("<div class='navbar-filler'></div>");
	});

	$(window).resize(function(){
		Adjust();
	});


	$(window).scroll(function(){

		//Following Navbar
		if($(window).scrollTop() > fixed_point && loaded)
		{
			$('.navbar').addClass('nav-fixed');
			$('.navbar-filler').height($('.navbar').outerHeight(true));
		}
		else
		{
			$('.navbar').removeClass('nav-fixed');
			$('.navbar-filler').height(0);
		}
	});

	function Adjust(){
		if($(window).width() > 768)
		{
			$('header').height($(window).height());
			$('.intro-book').css('top', ($('header').height() / 2 - $('.intro-book').height() / 2) + "px");
			$('.intro-text').css('top', ($('header').height() / 2 - $('.intro-text').height() / 2) + "px");
		}
		else {
			$('header').height(400);
		}
		if(!$('.navbar').hasClass("nav-fixed") && loaded)
			fixed_point = $('.navbar').offset().top;
	}
	
	$('.sample-button').click(function(event){
		$('#sample-form').slideDown();
		event.preventDefault();
	});

	$('form').submit(function(event){
		if($(this).find(".has-error").length > 0)
			return;
		event.preventDefault();
		var that = $(this),
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

	// Mobile Nav
	$('.mobile-nav > ul').html($('.navbar-nav').html());
	$('.mobile-nav').append("<a href='#' class='close-btn'><i class='icon_close'></i></a>");

	$('.navbar-toggle').click(function(event){
		event.stopPropagation();
		$('#wrapper').addClass('behind');
		$('.mobile-nav').addClass('active');
	});
	$('.mobile-nav a.close-btn').click(function(event){
		$('#wrapper').removeClass('behind');
		$('.mobile-nav').removeClass('active');
		event.preventDefault();
	});

	// Scrolling
	$('.mobile-nav a.scrollto').click(function(event) {
		if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
			event.preventDefault();
			var target = document.getElementById($(this).attr('href').substring(1));
			var top = target.offsetTop;
			if(target != null) {
				$('#wrapper').removeClass('behind');
				$('.mobile-nav').removeClass('active');
				$('html,body').animate({
					scrollTop: top
				}, 1000);
			}
		}
	});
});