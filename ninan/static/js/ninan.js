// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
$(function(){
    $('#lang_dropdown li a.lang').click(function(){
        $('#language_selecter').val($(this).data('code'));
        $('#language_form').submit();
    })
});
/*-------------------------------------------------*/
/* 在页面上单击时，出现积分的特效
 * http://www.anotherhome.net/1412#more-1412
/*-------------------------------------------------*/
jQuery(document).ready(function($) {
    $("html,body").click(function(e){
        var n=Math.round(Math.random()*100);
        var $i=$("<b/>").text("+"+n);
        var x=e.pageX,y=e.pageY;
        $i.css({
        "z-index":99999,
        "top":y-20,
        "left":x,
        "position":"absolute",
        "color":"#E94F06"
        });
        $("body").append($i);
        $i.animate(
            {"top":y-180,"opacity":0},
            1500,
            function(){$i.remove();}
        );
        e.stopPropagation();
    });
});
