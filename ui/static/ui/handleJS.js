

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 
   
function loginclick(){
    //alert("testing: "+window.location.pathname);
    if(window.location.pathname == "/login/"){
        alert("you are already at login page, You can create a new account if you dont have an account yet.")
    }
    else    window.location = "/login"
}
function logoutclick(){
    window.location = "/logout"
}

window.setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
    }, 5000);