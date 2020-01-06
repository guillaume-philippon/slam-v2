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
                    var net = {
                        'name': item.name,
                        'address' : item.address + '/' + item.prefix,
                        'description': item.description,
                        'total': item.total,
                        'used': item.used_addresses
                    }
                    self.networks.push(net);
                });
                self.show();
                self.dashboard();
            }
        })
    }

    show() {
        var self = this;
            $.each(self.networks, function(key, network){
                $('#networks').append(new Option(network.name, network.name))
            })
            $('#networks-load').fadeTo(2000, 0);
    }

    dashboard() {
        var self = this;
        $.each(self.networks, function(key, network){
            var net = new NetworkView(network.name, network.address,
            network.description, network.total, network.used)
            net.show()
        })
    }
}

class HostViewListener {
    constructor(){
        var self = this;
        this.hostname = $('#hostname').val()
        this.domain = $('#domains').val()

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
        var hostname = $('#hostname').val();
        var domain = $('#domains').val();
        var mac_address = $('#interface').val();
        var name_regex = new RegExp("^(([a-zA-Z0-9-_\.])*)*$");
        var mac_address_regex = new RegExp('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])');

        this.hostname = hostname;
        this.domain = domain;

        $('#add-host').attr("disabled", true);
        if (hostname != '' && name_regex.test(hostname)){
            $.ajax({
                url: '/domains/' + $('#domains').val() + '/' + $('#hostname').val(),
                success: function(data){
                    if (data.status == 'failed' && (mac_address_regex.test(mac_address) || mac_address == '')) {
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
                            $('#alert-message').text('')
                            $('#alert-message').append(alert_message_hostname);
                            $('#alert-message').append(alert_message_mac_address);
                            $('#alert-box').collapse('show')
                    }
                }
            })
        }
    }

    add (){
        $('#add-host').attr("disabled", true);
        var csrftoken = $.cookie('csrftoken');
        this.hostname = $('#hostname').val();
        this.domain = $('#domains').val();
        var options = {
            'domain': $('#domains').val(),
            'interface': $('#interface').val(),
            'ns': $('#hostname').val()
        }
        if ($('#no-ip').is(':checked')) {
            options.no_ip = 'True' // We must put a python like boolean
            options.network = $('#networks').val();
        } else if ($('#ip-address').val() == ''){
            options.network = $('#networks').val();
        } else {
            options.ip_address = $('#ip-address').val()
        }
        options.owner = $('#owner').val()
        if (! $('#dhcp').is(':checked')) {
            options.dhcp = 'False' // We must put a python like boolean
        }
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
                            $('#alert-message').text(data.message)
                             $('#alert-box').collapse('show')
                        } else {
                            $('#success-ip-address').text(data.addresses[0].ip)
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
                        $(location).attr('pathname', '/hosts/' + self.hostname + '.' + self.domain)

                    }
        })
    }


}

class NetworkView {
    constructor(name, address, description, max, used) {
        this.name = name;
        this.address = address
        this.description = description
        this.max = max
        this.used = used
        this.per_cent = ( this.used * 100 ) / this.max
    }
    show(){
        var self = this;
        var card = $('<div/>', {
            class: 'card ml-2 mb2',
            style: 'width: 18rem'
         });
        var card_body = $('<div/>',{
            class: 'card-body'
        });
        var card_title = $('<h5/>',{
            class: 'card-title',
            text: self.name,
        });
        var card_subtitle = $('<h6/>',{
            class: 'card-subtitle mb-2 text-muted',
            text: self.address,
        });
        var card_text = $('<p/>',{
            class: 'card-text',
            text: self.description,
        });
        var card_link = $('<a/>', {
            href: '/networks/' + self.name,
            class: 'card-link',
            text: 'More info'
        })
        var progress = $('<div/>', {
            class: 'progress',
        })
        var progress_bar = $('<div/>', {
            class: 'progress-bar progress-bar-striped',
            role: 'progressbar',
            style: 'width: ' + self.per_cent + '%',
        })
        $('#network-cards').append(
         card.append(
                card_body.append(
                    card_title,
                    card_subtitle,
                    progress.append(
                        progress_bar
                    ),
                    card_text,
                    card_link,
                )
            )
        )
    }
}


$(function(){
    new DomainsCtrl();
    new NetworkCtrl();
    new HostViewListener();
})