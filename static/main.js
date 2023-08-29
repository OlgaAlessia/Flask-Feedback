const eyePassword = document.getElementById('eyePassword');
const pwd = document.getElementById("password");

var loginUrl = 'http://127.0.0.1:5000/login';
var registerUrl = 'http://127.0.0.1:5000/register';


if ( document.URL == loginUrl || document.URL == registerUrl ){
    eyePassword.addEventListener("click", showPassword, false);
}

function showPassword() {

    const type = pwd.getAttribute("type") === "password" ? "text" : "password";
    pwd.setAttribute("type", type);

    // toggle the eye icon
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
}


