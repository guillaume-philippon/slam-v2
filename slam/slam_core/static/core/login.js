$.urlParam = function(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	return results[1] || 0;
}

class Authentication {
    constructor () {
        this.username = '';
        this.password = '';
    }

    login () {
        var data = {
            username: this.username,
            password: this.password
        }
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        var next = $.urlParam('next')
        $.post('/login?next=' + next, data, function(result){
            $(location).attr('href', result.next)
        });
    }
}

class LoginViewListener {
    constructor (authentication) {
        this.authentication = authentication;
        var self = this;
        $('#auth-request').click(function(){
            self.authentication.username = $('#username').val();
            self.authentication.password = $('#password').val();
            self.authentication.login();
        })
    }
}

$(function(){
    var authentication = new Authentication();
    var listener = new LoginViewListener(authentication);
})