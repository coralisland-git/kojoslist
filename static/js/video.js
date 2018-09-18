var video = document.getElementById('video');
var play = document.getElementById('videoPlay');

jQuery(document).ready(function($){
    $('#videoPlay').on('click', function() {
        $('#video')[0].play();
    });

    $(function() {
        $(".video-play-button").click(function() {
            $(".video-desc").addClass("display-none");
        });
    });

    $("#video").on('click', function() {
        if(this.paused) {
            this.play();
            $(".video-desc").addClass("display-none");
        } else {
            this.pause();
            $(".video-desc").removeClass("display-none");
        }
    })

});


