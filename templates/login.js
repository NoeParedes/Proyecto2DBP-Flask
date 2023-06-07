function login() {
    var correo = document.getElementById("correo").value;
    var password = document.getElementById("password").value;
    var data = { "correo": correo, "password": password };
    fetch('/login', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.text())
        .then(html => {
            document.body.innerHTML = html;
        });
}