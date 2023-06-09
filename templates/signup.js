function signup() {
    var nombre = document.getElementById("nombre").value;
    var apellido = document.getElementById("apellido").value;
    var username = document.getElementById("username").value;
    var correo = document.getElementById("correo").value;
    var password = document.getElementById("password").value;

    if (nombre === '' || password === '' || apellido === '' || correo === '' ||username=='') {
        alert("Por favor rellene todos los campos.");
        return;
    }

    // Restricciones de contraseña
    //var passwordRegex = /^(?=.*[A-Z])(?=.*\d.*\d)(?=.*[#$%&/]).{8,}$/;
    //if (!passwordRegex.test(password)) {
    //    alert("La contraseña no cumple con los requisitos:\n" +
    //        "- Al menos 8 caracteres\n" +
    //        "- Al menos 2 números\n" +
    //        "- Al menos 1 mayúscula\n" +
     //       "- Al menos 2 caracteres entre #$%&/");
     //   return;
   // }

    var data = { "nombre": nombre, "apellido": apellido,"username":username ,"correo":correo, "password":password };

    fetch('/users', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.text())
        .then(text => {
            if (text === "SUCCESS") {
                window.location.href = "/login_menu";
            }
        });
}
