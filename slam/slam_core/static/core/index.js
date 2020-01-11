/*jshint esversion: 8 */


class HostViewListener {
    constructor(){
        var self = this;
        this.hostname = $(HOST_CTRL_VIEW.view.name).val();
        this.domain = DomainsCtrl.get_selected();

        $(HOST_CTRL_VIEW.view.name).change(function(){
            self.check();
        });

        $(HARDWARE_CTRL_VIEW.view.mac_address).change(function(){
            self.check();
        });

        $(DOMAINS_CTRL_VIEW.select).change(function(){
            self.check();
        });

        $(HOST_CTRL_VIEW.add.btn).click(function(){
            self.add();
        });

        $('#commit').click(function(){
            self.commit();
        });

        $('#push').click(function(){
            self.push();
        });

        $('#alert-box').on('shown.bs.collapse',
            async function() {
                $('#alert-box').fadeTo(4000);
                await sleep(3000);
                $('#alert-box').collapse('hide');
            }
        );
    }

    async check (){
        var hostname = $(HOST_CTRL_VIEW.view.name).val();
        var domain = DomainsCtrl.get_selected();

        var mac_address = $(HARDWARE_CTRL_VIEW.view.mac_address).val();
        var mac_address_regex = new RegExp('([0-9A-F][0-9A-F]:){5}([0-9A-F][0-9A-F])');

        var name_regex = new RegExp("^(([a-z0-9-_\.])*)*$");

        this.hostname = hostname;
        this.domain = domain;

        $(HOST_CTRL_VIEW.add.btn).attr("disabled", true);
        if (hostname != '' && name_regex.test(hostname)) {
            var domain_record = new RecordCtrl(hostname, domain, null);
            var domain_record_exist = await domain_record.is_exist();
                if (domain_record_exist || (!mac_address_regex.test(mac_address) &&
                               mac_address != '')) {
                    var alert_message_hostname = '';
                    var alert_message_mac_address = '';
                    if (domain_record_exist) {
                        alert_message_hostname = $(
                            '<p/>', {
                                text: domain_record.name + ' is already used.'
                            }
                        );
                    }
                    if (! mac_address_regex.test(mac_address) && mac_address != '') {
                        alert_message_mac_address = $(
                            '<p/>', {
                                text: mac_address + ' is not a valid MAC address format.' +
                                'MAC address must be add with upper case characters like: ' +
                                'AA:BB:CC:DD:EE:FF'
                            }
                        );
                    }
                    $('#alert-message').text('');
                    $('#alert-message').append(alert_message_hostname);
                    $('#alert-message').append(alert_message_mac_address);
                    $('#alert-box').collapse('show');
                } else {
                    $(HOST_CTRL_VIEW.add.btn).attr('disabled', false);
                }
        }
    }

    add (){
        $(HOST_CTRL_VIEW.add.btn).attr("disabled", true);
        var csrftoken = $.cookie('csrftoken');
        this.hostname = $(HOST_CTRL_VIEW.view.name).val();
        this.domain = DomainsCtrl.get_selected();
        var options = {
            'domain': DomainsCtrl.get_selected(),
            'interface': $(HARDWARE_CTRL_VIEW.view.mac_address).val(),
            'ns': $(HOST_CTRL_VIEW.view.name).val()
        };
        if ($('#no-ip').is(':checked')) {
            options.no_ip = 'True'; // We must put a python like boolean
            options.network = NetworksCtrl.get_selected();
        } else if ($('#ip-address').val() == ''){
            options.network = NetworksCtrl.get_selected();
        } else {
            options.ip_address = $('#ip-address').val();
        }
        options.owner = $(HARDWARE_CTRL_VIEW.view.owner).val();
        if (! $('#dhcp').is(':checked')) {
            options.dhcp = 'False'; // We must put a python like boolean
        }
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/hosts/' + $(HOST_CTRL_VIEW.view.name).val() + '.' + DomainsCtrl.get_selected(),
            type: 'POST',
            data: options,
            success: function(data){
                        console.log(data);
                        if (data.status != 'done') {
                            $('#alert-message').text(data.message);
                             $('#alert-box').collapse('show');
                        } else {
                            $('#success-ip-address').text(data.addresses[0].ip);
                            $('#success-box').collapse('show');
                            $(HOST_CTRL_VIEW.view.name).empty();
                            $(HARDWARE_CTRL_VIEW.view.mac_address).val('');
                            $(HARDWARE_CTRL_VIEW.view.owner).val('');
                        }
                    }
        });
    }

     commit (){
        $(HOST_CTRL_VIEW.add.btn).attr("disabled", true);
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/commit/',
            type: 'POST',
            success: function(data){
                        $('#diff').text(data.data);
                        $('#push').attr("disabled", false);
                        $('#network').hide();
                        $('#hardware').hide();
                    }
        });
    }

     push (){
        $('#push').attr("disabled", true);
        $(HOST_CTRL_VIEW.add.btn).attr("disabled", true);
        var self = this;
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/publish/',
            type: 'POST',
            success: function(data){
                        $('#diff').text('');
                        $('#push').attr("disabled", true);
                        $('#success-box').collapse('hide');
                        $('#network').show();
                        $('#hardware').show();
                        $(location).attr('pathname', '/hosts/' + self.hostname + '.' + self.domain);
                    }
        });
    }
}

$(function(){
    new DomainsCtrl();
    new NetworksCtrl();
//    new NetworkCtrl();
    new HostCtrl();
    new HostViewListener();
});