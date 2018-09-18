jQuery(function($){
	$('.content ul li').click(function(){
		var ul = $(this).parents('ul');
		if(ul.hasClass('open')){
			ul.removeClass('open').find('div').slideUp(500);
		}else{
			ul.addClass('open').find('div').slideDown(500);
		}	
	});
});