/*jshint esversion: 6 */

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

        $('#add-host').click(function(){
            self.check();
        });
    }

    check (){
        var network = $('#networks').val()
        var hostname = $('#hostname').val();
        var domain = $('#domains').val();
        var mac_address = $('#interface').val();
        var owner = $('#owner').val();
        var mac_address_regex = new RegExp('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])');

        if (hostname != '' && mac_address_regex.test(mac_address)){
            $('#add-host').attr("disabled", false);
        } else {
            $('#add-host').attr("disabled", true);
        }
    }


}

$(function(){
    var domains = new DomainsCtrl();
    var networks = new NetworkCtrl();
    var hostListener = new HostViewListener();
})