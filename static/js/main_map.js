AmCharts.theme = AmCharts.themes.black;

// add all your code to this method, as this will ensure that page is loaded
var map;
AmCharts.ready(function() {

    // create AmMap object

    map = new AmCharts.AmMap();



    // set path to images





    /* create data provider object

     mapVar tells the map name of the variable of the map data. You have to

     view source of the map file you included in order to find the name of the

     variable - it's the very first line after commented lines.



     getAreasFromMap indicates that amMap should read all the areas available

     in the map data and treat them as they are included in your data provider.

     in case you don't set it to true, all the areas except listed in data

     provider will be treated as unlisted.

     */

    var dataProvider = {

        mapVar: AmCharts.maps.worldLow,

        getAreasFromMap:true

    };

    // pass data provider to the map object

    map.dataProvider = dataProvider;



    /* create areas settings

     * autoZoom set to true means that the map will zoom-in when clicked on the area

     * selectedColor indicates color of the clicked area.

     */

    map.areasSettings = {

        autoZoom: true,

        rollOverBrightness:10,

        selectedBrightness:20,

    };
	
	 map.mouseWheelZoomEnabled           = true;
	 
	 map.zoomControl.zoomControlEnabled  = false;
	 
	 map.zoomControl.homeButtonEnabled   = false;
	

    // let's say we want a small map to be displayed, so let's create and add it to the map

   // map.smallMap = new AmCharts.SmallMap();



    // write the map to container div

    map.write("main_map");
	
	jQuery('a[href="http://www.amcharts.com/javascript-maps/"]').remove();
	jQuery('.show_country').click(function(){

			var country  = jQuery(this).data('country');
         
			console.log(country);
			map.clickMapObject(map.getObjectById(country));
			if(jQuery('body').scrollTop()>78 || jQuery('html').scrollTop()>78){
				jQuery('body,html').animate({scrollTop:78});
			}
    });
	jQuery('.hedle_zoom').on('mousewheel',function(e){
		e.preventDefault();
		if(e.originalEvent.deltaY > 0){
			map.zoomOut();
            console.log(e.mapObject.id);
		}else{
			map.zoomIn();
		}
	});
	

	map.addListener("clickMapObject", function (event) {
         console.log(event.mapObject.id);
         var cncode = event.mapObject.id;
         var countryid = cncode.toLowerCase();
         window.location = "/profile/#countries/"+countryid+"/"+countryid+"-all";
    });
});

