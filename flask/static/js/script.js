var num = 0;
$('.settings_minus').each(function(){
  if($(this).find('.valid').length >= 0){
    num++;
  }
});


$('.button-remove-minus').click(function() {
  $(this).parent().remove();
});

function process(selectedItem) {
    const data = JSON.stringify({
        "num": num
    });
    $.ajax({
        url: "/settings",
        type: "POST",
        contentType: "application/json",
        data: data
    });
}

$('#add-minus').click(function () {

    $('#minuses').append("<div class='settings_minus'><input class='settings-input' name='minus" + num++ + "' type='text'>\n<a class='button-remove-minus'>\n<img src='static/img/Minus.png' class='image-minus'>\n</a>\n<div>");

    $(".button-remove-minus").click(function () {
         $(this).parent().remove();
    });
});
