AmCharts.theme = AmCharts.themes.black;

// add all your code to this method, as this will ensure that page is loaded

AmCharts.ready(function() {

    // create AmMap object

    var map = new AmCharts.AmMap();



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

        selectedBrightness:20

    };



    // let's say we want a small map to be displayed, so let's create and add it to the map

    map.smallMap = new AmCharts.SmallMap();



    // write the map to container div

    map.write("mapdiv");
    map.addListener("clickMapObject", function (event) {
         if (event.mapObject.id != undefined ) {
             alert(event.mapObject.id);
             console.log(event.mapObject);
             console.log(event);
          
         }
     });




});


var countryMaps = {
    "AF": [ "afghanistanLow" ],
    "AL": [ "albaniaLow" ],
    "DZ": [ "algeriaLow" ],
    "AD": [ "andorraLow" ],
    "AO": [ "angolaLow" ],
    "AR": [ "argentinaLow" ],
    "AM": [ "armeniaLow" ],
    "AU": [ "australiaLow" ],
    "AT": [ "austriaLow" ],
    "AZ": [ "azerbaijanLow" ],
    "BS": [ "bahamasLow" ],
    "BH": [ "bahrainLow" ],
    "BD": [ "bangladeshLow" ],
    "BY": [ "belarusLow" ],
    "BE": [ "belgiumLow" ],
    "BZ": [ "belizeLow" ],
    "BT": [ "bhutanLow" ],
    "BO": [ "boliviaLow" ],
    "BA": [ "bosniaHerzegovinaCantonsLow" ],
    "BW": [ "botswanaLow" ],
    "BR": [ "brazilLow" ],
    "BN": [ "bruneiDarussalamLow" ],
    "BG": [ "bulgariaLow" ],
    "BF": [ "burkinaFasoLow" ],
    "BI": [ "burundiLow" ],
    "KH": [ "cambodiaLow" ],
    "CM": [ "cameroonLow" ],
    "CA": [ "canadaLow" ],
    "CV": [ "capeVerdeLow" ],
    "CF": [ "centralAfricanRepublicLow" ],
    "TD": [ "chadLow" ],
    "CL": [ "chileLow" ],
    "CN": [ "chinaLow" ],
    "CO": [ "colombiaLow" ],
    "CD": [ "congoDRLow" ],
    "CG": [ "congoLow" ],
    "CR": [ "costaRicaLow" ],
    "HR": [ "croatiaLow" ],
    "CU": [ "cubaLow" ],
    "CY": [ "cyprusLow" ],
    "UN": [ "cyprusNorthernCyprusLow" ],
    "GB": [ "unitedKingdomLow" ],
    "CZ": [ "czechRepublicLow" ],
    "DK": [ "denmarkLow" ],
    "DJ": [ "djiboutiLow" ],
    "DO": [ "dominicanRepublicLow" ],
    "EC": [ "ecuadorLow" ],
    "EG": [ "egyptLow" ],
    "SV": [ "elSalvadorLow" ],
    "EE": [ "estoniaLow" ],
    "FI": [ "finlandLow" ],
    "FR": [ "france2016Low" ],
    "GE": [ "georgiaLow" ],
    "DE": [ "germanyLow" ],
    "GR": [ "greeceLow" ],
    "GT": [ "guatemalaLow" ],
    "GN": [ "guineaLow" ],
    "GY": [ "guyanaLow" ],
    "HT": [ "haitiLow" ],
    "HN": [ "hondurasLow" ],
    "HK": [ "hongKongLow" ],
    "HU": [ "hungaryLow" ],
    "GL": [ "icelandLow" ],
    "IS": [ "icelandLow" ],
    "IN": [ "indiaLow" ],
    "ID": [ "indonesiaLow" ],
    "MY": [ "malaysiaLow" ],
    "IR": [ "iranLow" ],
    "IQ": [ "iraqLow" ],
    "IE": [ "irelandLow" ],
    "IL": [ "israelLow" ],
    "PS": [ "palestineLow" ],
    "VA": [ "italyLow" ],
    "SM": [ "sanMarinoLow" ],
    "MT": [ "italyLow" ],
    "IT": [ "italyLow" ],
    "JM": [ "jamaicaLow" ],
    "JP": [ "japanLow" ],
    "KZ": [ "kazakhstanLow" ],
    "KE": [ "kenyaLow" ],
    "XK": [ "kosovoLow" ],
    "KG": [ "kyrgyzstanLow" ],
    "LA": [ "laosLow" ],
    "LV": [ "latviaLow" ],
    "LT": [ "lithuaniaLow" ],
    "LU": [ "luxembourgLow" ],
    "MK": [ "macedoniaLow" ],
    "ML": [ "maliLow" ],
    "MX": [ "mexicoLow" ],
    "MD": [ "moldovaLow" ],
    "MN": [ "mongoliaLow" ],
    "ME": [ "montenegroLow" ],
    "MA": [ "moroccoLow" ],
    "MM": [ "myanmarLow" ],
    "NP": [ "nepalLow" ],
    "NL": [ "netherlandsLow" ],
    "NZ": [ "newZealandLow" ],
    "NI": [ "nicaraguaLow" ],
    "NG": [ "nigeriaLow" ],
    "NO": [ "norwayLow" ],
    "AE": [ "unitedArabEmiratesLow" ],
    "OM": [ "omanLow" ],
    "PK": [ "pakistanLow" ],
    "PA": [ "panamaLow" ],
    "PY": [ "paraguayLow" ],
    "PE": [ "peruLow" ],
    "PH": [ "philippinesLow" ],
    "PL": [ "polandLow" ],
    "PT": [ "portugalLow" ],
    "PR": [ "puertoRicoLow" ],
    "US": [ "usaLow" ],
    "QA": [ "qatarLow" ],
    "RO": [ "romaniaLow" ],
    "RW": [ "rwandaLow" ],
    "SA": [ "saudiArabiaLow" ],
    "RS": [ "serbiaLow" ],
    "SG": [ "singaporeLow" ],
    "SK": [ "slovakiaLow" ],
    "SI": [ "sloveniaLow" ],
    "LS": [ "southAfricaLow" ],
    "ZA": [ "southAfricaLow" ],
    "KR": [ "southKoreaLow" ],
    "ES": [ "spainLow" ],
    "LK": [ "sriLankaLow" ],
    "SR": [ "surinameLow" ],
    "SE": [ "swedenLow" ],
    "CH": [ "switzerlandLow" ],
    "SY": [ "syriaLow" ],
    "TW": [ "taiwanLow" ],
    "TJ": [ "tajikistanLow" ],
    "TH": [ "thailandLow" ],
    "TR": [ "turkeyLow" ],
    "UG": [ "ugandaLow" ],
    "UA": [ "ukraineLow" ],
    "GG": [ "unitedKingdomLow" ],
    "JE": [ "unitedKingdomLow" ],
    "IM": [ "unitedKingdomLow" ],
    "UY": [ "uruguayLow" ],
    "UZ": [ "uzbekistanLow" ],
    "VE": [ "venezuelaLow" ],
    "VN": [ "vietnamLow" ],
    "YE": [ "yemenLow" ]
  };



  // calculate which map to be used
  var currentMap = {"country_code":"IN","country_name":"India"};
  var titles = [];
  if ( countryMaps[ "IN" ] !== undefined ) {
    currentMap = countryMaps[ "IN" ][ 0 ];

    // add country title
    if ( "India" ) {
      titles.push( {
        "text": "India"
      } );
    }

  }


  var map = AmCharts.makeChart( "mapdiv2", {
      "type": "map",
      "theme": "light",
      "colorSteps": 10,
      "dataProvider": {
        "mapURL": "https://www.amcharts.com/lib/3/maps/svg/usaLow.svg",
        "getAreasFromMap": true,
        "zoomLevel": 0.9,
        "areas": []
      },
      "areasSettings": {
        "autoZoom": true,
        "balloonText": "[[title]]: <strong>[[value]]</strong>"
      },
      "valueLegend": {
        "right": 10,
        "minValue": "little",
        "maxValue": "a lot!"
      },
      "zoomControl": {
        "minZoomLevel": 0.9
      },
      "titles": titles,
      "listeners": [ {
        "event": "init",
        "method": updateHeatmap
      } ]
    } );


    function updateHeatmap( event ) {
      var map = event.chart;
      if ( map.dataGenerated )
        return;
      if ( map.dataProvider.areas.length === 0 ) {
        setTimeout( updateHeatmap, 100 );
        return;
      }
      for ( var i = 0; i < map.dataProvider.areas.length; i++ ) {
        map.dataProvider.areas[ i ].value = Math.round( Math.random() * 10000 );
      }
      map.dataGenerated = true;
      map.validateNow();
    }

