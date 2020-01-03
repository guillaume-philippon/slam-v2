/*jshint esversion: 6 */

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class DomainsCtrl {
    constructor (){
        this.uri = '/domains';
        this.domains = [];
        this._get();
    }

    _get() {
        var self = this;
        $.ajaxSetup({
            headers: {'Accept': 'application/json'}
        })
        $.ajax({
            url: self.uri,
            success: function(data){
                $.each(data, function(key, item){
                    self.domains.push(item.name);
                });
                self.show();
            }
        })
    }

    show() {
        var self = this;
        $.each(self.domains, function(key, domain){
            $('#domains').append(new Option(domain, domain))
        })
        $('#domains-load').fadeTo(2000, 0);
    }
}

class NetworkCtrl {
    constructor(){
        this.uri = '/networks';
        this.networks = [];
        this._get();
    }

    _get() {
        var self = this;
        $.ajaxSetup({
            headers: {'Accept': 'application/json'}
        })
        $.ajax({
            url: self.uri,
            success: function(data){
                $.each(data, function(key, item){
                    self.networks.push(item.name);
                });
                self.show();
            }
        })
    }

    show() {
        var self = this;
            $.each(self.networks, function(key, network){
                $('#networks').append(new Option(network, network))
            })
            $('#networks-load').fadeTo(2000, 0);
    }
}

class HostViewListener {
    constructor(){
        var self = this;
        $('#hostname').change(function(){
            self.check();
        });

        $('#interface').change(function(){
            self.check();
        });

        $('#domains').change(function(){
            self.check();
        });

        $('#add-host').click(function(){
            self.add();
        });

        $('#commit').click(function(){
            self.commit();
        })

        $('#push').click(function(){
            self.push();
        })

        $('#alert-box').on('shown.bs.collapse',
                    async function() {
                        $('#alert-box').fadeTo(4000)
                        await sleep(3000)
                        $('#alert-box').collapse('hide')
            })
    }

    check (){
        var network = $('#networks').val()
        var hostname = $('#hostname').val();
        var domain = $('#domains').val();
        var mac_address = $('#interface').val();
        var owner = $('#owner').val();
        var mac_address_regex = new RegExp('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])');

        $('#add-host').attr("disabled", true);
        if (hostname != ''){
            $.ajax({
                url: '/domains/' + $('#domains').val() + '/' + $('#hostname').val(),
                success: function(data){
                    if (data.status == 'failed' && mac_address_regex.test(mac_address)) {
                        $('#add-host').attr("disabled", false);
                    } else {
                        var alert_message_hostname = ''
                        var alert_message_mac_address = ''
                        if (data.status != 'failed') {
                            alert_message_hostname = $(
                                '<p/>', {
                                    text: hostname + '.' + domain + ' exist !'
                                }
                            );
                        }
                        if (! mac_address_regex.test(mac_address) && mac_address != '') {
                            alert_message_mac_address = $(
                                '<p/>', {
                                    text: mac_address + ' is not a valid MAC address'
                                }
                            );
                        }
                        if (mac_address != ''){
                            $('#alert-message').text('')
                            $('#alert-message').append(alert_message_hostname);
                            $('#alert-message').append(alert_message_mac_address);
                            $('#alert-box').collapse('show')
                        }
                    }
                }
            })
        }
    }

    add (){
        $('#add-host').attr("disabled", true);
        var self = this;
        var csrftoken = $.cookie('csrftoken')
        var options = {
            'domain': $('#domains').val(),
            'interface': $('#interface').val(),
            'ns': $('#hostname').val()
        }
        if ($('#no-ip').is(':checked')) {
            console.log('No IP');
            options.no_ip = 'True' // We must put a python like boolean
            options.network = $('#networks').val();
        } else if ($('#ip-address').val() == ''){
            console.log('Network')
            options.network = $('#networks').val();
        } else {
            console.log('IP ' + $('#ip-address').val());
            options.ip_address = $('#ip-address').val()
        }
        if (! $('#no-ip').is(':checked')) {
            options.dhcp = 'False' // We must put a python like boolean
        }
//        console.log(options)
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/hosts/' + $('#hostname').val() + '.' + $('#domains').val(),
            type: 'POST',
            data: options,
            success: function(data){
                        console.log(data)
                        if (data.status != 'done') {
                            console.log('here we are')
                            $('#alert-message').text(data.message)
                             $('#alert-box').collapse('show')
                        } else {
                            $('#success-box').collapse('show')
                            $('#hostname').val('')
                            $('#interface').val('')
                            $('#owner').val('')
                        }
                    }
        })
    }

     commit (){
        $('#add-host').attr("disabled", true);
        var self = this;
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/commit/',
            type: 'POST',
            success: function(data){
                        $('#diff').text(data.data);
                        $('#push').attr("disabled", false)
                        $('#network').hide()
                        $('#hardware').hide()
                    }
        })
    }

     push (){
        $('#add-host').attr("disabled", true);
        var self = this;
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/publish/',
            type: 'POST',
            success: function(data){
                        $('#diff').text('');
                        $('#push').attr("disabled", true)
                        $('#success-box').collapse('hide')
                        $('#network').show()
                        $('#hardware').show()
                    }
        })
    }


}

$(function(){
    var domains = new DomainsCtrl();
    var networks = new NetworkCtrl();
    var hostListener = new HostViewListener();
})