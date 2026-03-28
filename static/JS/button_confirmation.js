
// Button interactivty on the catalogue page

$(document).ready(function () {
    $(".dropdown-menu").on("submit", ".add-to-reading, .add-to-wishlist", function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        var form = $(this);
        var isReading = form.hasClass('add-to-reading');
        var actionURL = form.attr('action');
        var button = form.closest(".dropdown").find("button.button_two").first();

        $.ajax({
            type: 'POST',
            url: actionURL,
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    if (isReading) {
                        button.prop("disabled", true);
                        button.html('Reading');
                        button.addClass("added");
                    } else {
                        button.html('Wishlisted').addClass("wishlisted");
                        form.closest('li').toggle()
                    }
                    $("#response").text(response.message);
                }
            }
        });
    });
});