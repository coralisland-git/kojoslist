jQuery(document).ready(function() {

    jQuery(".flyer1").click(function() {
        jQuery(".home-map-ads-top").css('display', 'none');
    });
    jQuery("#flyertopclose").click(function() {
        jQuery(".home-map-ads-top").css('display', 'none');
    });
//    var windowwidth = jQuery(window).width();
//    if (windowwidth <= 930) {
//        jQuery(".country-list li").each(function() {
//            var country1 = jQuery(this).find("a.show_country").text()
//
//            if (country1.length > 10) {
//                jQuery(this).find("a.show_country").text(country1.substring(0, 10) + "..");
//            }
//
//        });
//    }
});
