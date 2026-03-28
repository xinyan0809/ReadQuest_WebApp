// When clicking on like button, it toggles the icon
$(document).ready(function () {

    // Toggle the fill in
    $(".like_button_box").click(function () {
        $(this).find("i").toggleClass("bi-hand-thumbs-up bi-hand-thumbs-up-fill");
    });
 });

