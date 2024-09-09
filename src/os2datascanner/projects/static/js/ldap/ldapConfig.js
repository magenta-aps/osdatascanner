// test connection and authentication

var btnConnection = document.querySelector('#button-connection');
var btnAuth = document.querySelector('#button-auth');
var textConnection = document.querySelector('#responseConnection');
var textAuth = document.querySelector('#responseAuth');
var responseSuccessCon = document.querySelector('#responseSuccessCon');
var responseErrorCon = document.querySelector('#responseErrorCon');
var responseSuccessAuth = document.querySelector('#responseSuccessAuth');
var responseErrorAuth = document.querySelector('#responseErrorAuth');

// button - test connection
btnConnection.addEventListener('click', testConnection);

function testConnection(e) {
    e.preventDefault();

    // Get values from connection protocol and connection url
    var connectionProtocol = document.getElementById("id_connection_protocol").value;
    var connectionUrl = document.getElementById("id_connection_url").value;

    var oReq = new XMLHttpRequest();

    // Get Http request with params
    oReq.open("POST", urlConnection);

    // Set CSRFToken in header
    oReq.setRequestHeader("X-CSRFToken", csrfToken);
    oReq.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    oReq.onreadystatechange = function () {
        if (oReq.readyState === 4) {
            // if connection succeeded
            if (oReq.status === 200) {
                responseSuccessCon.style.display = "block";
                responseErrorCon.style.display = "none";
                textConnection.innerText = gettext('Connection succeeded');
            } else {
            // else connection failed
                responseErrorCon.style.display = "block";
                responseSuccessCon.style.display = "none";
                textConnection.innerText = gettext('Connection failed');
            }
        }
    };

    oReq.send("url=" + connectionProtocol + connectionUrl);
}


// button - test auth
btnAuth.addEventListener('click', testAuth);

function testAuth(e) {
    e.preventDefault();

    // Get values from connection protocol, connection url, bind_dn and credential
    var connectionProtocol = document.getElementById("id_connection_protocol").value;
    var connectionUrl = document.getElementById("id_connection_url").value;
    var bindDn = document.getElementById("id_bind_dn").value;
    var credential = document.getElementById("id_ldap_password").value;

    var oReq = new XMLHttpRequest();

    // Get Http request with params
    oReq.open("POST", urlAuth);

    // Set CSRFToken in header
    oReq.setRequestHeader("X-CSRFToken", csrfToken);
    oReq.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    oReq.onreadystatechange = function () {
        if (oReq.readyState === 4) {
            if (oReq.status === 200) {
                // if connection succeeded
                responseSuccessAuth.style.display = "block";
                responseErrorAuth.style.display = "none";
                textAuth.innerText = gettext('Authentication succeeded');
            } else {
                // else connection failed
                responseErrorAuth.style.display = "block";
                responseSuccessAuth.style.display = "none";
                textAuth.innerText = gettext('Authentication failed');
            }
        }
    };

    oReq.send("url=" + connectionProtocol + connectionUrl + "&bind_dn=" + bindDn  + "&bind_credential=" + credential);
}

// hide checkbox if import is not by group
const importInto = document.getElementById("id_import_into");
importInto.addEventListener("change", () => {
    const importManagers = document.getElementById("id_import_managers");
    if (importInto.value === "group") {
        importManagers.disabled = false;
        importManagers.closest(".form__group").style.display = "block";
    } else {
        importManagers.disabled = true;
        importManagers.closest(".form__group").style.display = "none";
    }
});
