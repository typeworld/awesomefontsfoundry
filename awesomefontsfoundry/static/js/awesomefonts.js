function login(username, password) {
    AJAX('#action', '/login', { 'username': username, 'password': password, 'inline': 'true' });
}

function logout() {
    AJAX('#action', '/logout');
}
