function selectStar(star, bookId) {
    var val = parseInt(star.getAttribute('data-value'));
    var container = star.parentElement;
    container.querySelectorAll('.star-icon').forEach(function(s) {
        var sv = parseInt(s.getAttribute('data-value'));
        s.classList.toggle('bi-star-fill', sv <= val);
        s.classList.toggle('bi-star', sv > val);
    });
    document.getElementById('ratingInput' + bookId).value = val;
}


$(document).ready(function () {
    $(document).on('mouseenter', '.star-rating .star-icon', function () {
        const val = parseInt($(this).data('value'));
        const container = $(this).closest('.star-rating');
        container.find('.star-icon').each(function () {
            $(this).toggleClass('bi-star-fill', parseInt($(this).data('value')) <= val)
                   .toggleClass('bi-star',      parseInt($(this).data('value')) >  val);
        });
    }).on('mouseleave', '.star-rating .star-icon', function () {
        const container = $(this).closest('.star-rating');
        const selected = parseInt(container.data('selected')) || 0;
        container.find('.star-icon').each(function () {
            $(this).toggleClass('bi-star-fill', parseInt($(this).data('value')) <= selected)
                   .toggleClass('bi-star',      parseInt($(this).data('value')) >  selected);
        });
    }).on('click', '.star-rating .star-icon', function () {
        const val = parseInt($(this).data('value'));
        const container = $(this).closest('.star-rating');
        container.data('selected', val);
        $('#ratingInput' + container.data('book-id')).val(val);
    });
});