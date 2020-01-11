/*jshint esversion: 8 */

$.urlParam = function(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	return results[1] || 0;
};

class Authentication {
    constructor () {
        this.username = '';
        this.password = '';
    }

    login () {
        var data = {
            username: this.username,
            password: this.password
        };
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        var next = $.urlParam('next');
        $.post('/login?next=' + next, data, function(result){
            console.log(result);
            if (result.status != null && result.status == 'failed' ) {
                $('#alert-box').text(result.message);
                $('#alert-box').collapse('show');
            } else {
                $(location).attr('href', result.next);
            }
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
        });
    }
}

$(function(){
    var authentication = new Authentication();
    new LoginViewListener(authentication);
        $('#alert-box').on('shown.bs.collapse',
            async function() {
                $('#alert-box').fadeTo(4000);
                await sleep(3000);
                $('#alert-box').collapse('hide');
            }
        );
});