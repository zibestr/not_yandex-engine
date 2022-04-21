var num_minus = 0;
$('.settings_minus').each(function(){
  if($(this).find('.valid').length >= 0){
    num_minus++;
  }
});

var num_plus = 0;
$('.settings_plus').each(function(){
  if($(this).find('.valid').length >= 0){
    num_plus++;
  }
});


$('.button-remove').click(function() {
  $(this).parent().remove();
});


function process(){
    $(".load-text-settings").css("display", "block");
}


$('#add-minus').click(function () {

    $('#minuses').append("<div class='settings_minus'><input class='settings-input' placeholder='Введите ссылку-исключение' name='minus" + num_minus++ + "' type='text'>\n<a class='button-remove'>\n<img src='static/img/Minus.png' class='image-minus'>\n</a>\n<div>");

    $(".button-remove").click(function () {
         $(this).parent().remove();
    });

    const data = JSON.stringify({
        "num-minus": num_minus
    });
    $.ajax({
        url: "/get_response",
        type: "POST",
        contentType: "application/json",
        data: data
    });
});

$('#add-plus').click(function () {

    $('#pluses').append("<div class='settings_minus'><input class='settings-input' placeholder='Введите дополнительную ссылку' name='plus" + num_plus++ + "' type='text'>\n<a class='button-remove'>\n<img src='static/img/Minus.png' class='image-minus'>\n</a>\n<div>");

    $(".button-remove").click(function () {
         $(this).parent().remove();
    });

    const data = JSON.stringify({
        "num-plus": num_plus
    });
    $.ajax({
        url: "/get_response",
        type: "POST",
        contentType: "application/json",
        data: data
    });
});

$('.help').click(function () {
    var text = $(this).children('.help-text').text()
    $('#search-input').val(text);
    $(".helping").css("display", "none");
});


$('.help-result').click(function () {
    var text = $(this).children('.help-text').text()
    $('#search-input').val(text);
    $('.result-icon').css("display", "none");
    $(".helping-result").css("display", "none");
});
