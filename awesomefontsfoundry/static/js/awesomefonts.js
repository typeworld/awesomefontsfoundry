function login(url, client_id, redirect_uri, scope, state) {
    window.location.href = url + "?client_id=" + client_id + "&response_type=code&redirect_uri=" + redirect_uri + "&scope=" + scope + "&state=" + state;
}

function edit(url, redirect_uri) {
    window.location.href = url.replace("__place_for_redirect_uri__", redirect_uri);
}

function logout() {
    AJAX('#action', '/logout');
}

function buy(name) {
    AJAX('#action', '/cart/add', { "products": name });
}

function remove(name) {
    AJAX('#action', '/cart/remove', { "products": name });
}

function checkout() {
    AJAX('#action', '/cart/checkout');
}

$(document).ready(function () {
    tippy('[title]', {
        content(reference) {
            const title = reference.getAttribute('title');
            reference.removeAttribute('title');
            return title;
        },
        allowHTML: true,
        interactive: true,
        showOnCreate: true,
        delay: 1000,
        placement: "bottom",
        theme: 'tomato',
    });

    tippy('[alt]', {
        content(reference) {
            const title = reference.getAttribute('alt');
            reference.removeAttribute('alt');
            return title;
        },
        allowHTML: true,
        interactive: true,
        placement: "bottom",
        theme: 'tomato',
    });
});