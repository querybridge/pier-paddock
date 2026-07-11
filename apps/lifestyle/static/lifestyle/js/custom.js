(function($){
	// Preloader
	$(window).on("load", function(){
		$(".preloader").fadeOut();
	});
    $(document).ready(function(){
		// Sticky Navigation Bar
		$(window).scroll(function(){
			var scrollHeight = $(document).scrollTop();
			if(scrollHeight > 250){
				$('.navigation').addClass('navigation-fixed');
			}else{
				$('.navigation').removeClass('navigation-fixed');
			}
		});

        // Search Box
		var $showsearchbox = $(".search-icon i");
		var $togglesearchbox = $(".searchbox");
		$(document).on('click', function(e) {
			var clickID = e.target.id;
			if ((clickID !== 's')) {
				$togglesearchbox.removeClass('show');
			}
		});
		$showsearchbox.on('click', function(e) {
			e.stopPropagation();
		});
		$('.search-form').on('click', function(e) {
			e.stopPropagation();
		});
		$showsearchbox.on('click', function(e) {
			if (!$togglesearchbox.hasClass("show")) {
				$togglesearchbox.addClass('show');
				e.preventDefault();
			} else
				$togglesearchbox.removeClass('show');
			e.preventDefault();

			if (!$showsearchbox.hasClass("active"))
				$showsearchbox.addClass('active');
			else
				$showsearchbox.removeClass('active');
		});
		
		// Scroll To Top
		$('.totop').hide();
		$(window).on("scroll", function(){
			var scrollHeight = $(document).scrollTop();

			if(scrollHeight > 50){
				$('.header').addClass('nav-fixed');
			}else{
				$('.header').removeClass('nav-fixed');
			}
			// Scroll To Top Apearing
			if(scrollHeight > 150){
				$('.totop').fadeIn();
			}else{
				$('.totop').fadeOut();
			}
		});
		$(".totop a").click(function(event){
			$("html").animate({scrollTop:$("body").offset().top}, "1000");
			event.preventDefault();
		});
        
        // Mobile Menu
		$('#desktop-menu').meanmenu({
			meanMenuContainer	: '#mobile-menu',
			meanScreenWidth		: '991',
            meanMenuClose 		: '<i class="fas fa-times"></i>',
            meanMenuOpen        : '<span></span><span></span><span></span>',
            meanRevealPosition  : 'left'
		});
    });
}(jQuery))