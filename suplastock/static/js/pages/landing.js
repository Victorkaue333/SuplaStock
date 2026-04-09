document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll('.feature-card, .preview-card, .mini-metric');
    cards.forEach(function (card, idx) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(14px)';
        setTimeout(function () {
            card.style.transition = 'opacity 420ms ease, transform 420ms ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 70 * idx);
    });
});
