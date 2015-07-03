(function($) {
	$(document).ready(function() {
		// Show or hide the sidebar menu
		$("#sidebar_menu").click(function() {			
			if ($("#sidebar").hasClass("show_sidebar")) {
				$("#sidebar").removeClass("show_sidebar");
			} else {
				$("#sidebar").addClass("show_sidebar", {duration:500});
			}
		});

	});
})(django.jQuery);


