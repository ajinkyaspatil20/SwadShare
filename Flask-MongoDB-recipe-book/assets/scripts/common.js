'use strict';
import M from 'materialize-css/dist/js/materialize.js';

// mobile menu handler
$('#menuOpener').click(() => {
    const _body = $('body');
    const ico = (_body.hasClass('navRolled')) ? 'menu' : 'close';

    $('#menuOpener i').text(ico);
    _body.toggleClass('navRolled');
});

$('button.voteForRecipe').click(function (e) {
    e.preventDefault();

    const _this = $(this);

    const recipe_id = _this.attr('data-recipe-id');

    if (typeof recipe_id === 'undefined') {
        alert('You need to login to vote for the recipe');
        return false;
    }

    $.ajax({
        type: 'post',
        url: '/api/recipe-vote',
        data: {
            id: recipe_id
        },
        async: true,
        dataType: 'json',
        success: function (response) {
            if (response.status === 'error') {
                alert(response.message);
                return false;
            }
            _this.toggleClass('voted');
            _this.find('span').text(response.votes);
        },
    });
});

document.addEventListener('DOMContentLoaded',  () => {
    const elems = document.querySelectorAll('.modal');
    M.Modal.init(elems, {});
});