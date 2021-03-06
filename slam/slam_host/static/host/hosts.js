/*jshint esversion: 6 */

class Hosts {
    constructor() {
        this.uri = '/hosts';
        this.hosts = [];
        this._get();
    }

    _get() {
        var self = this;
        $.ajaxSetup({
            headers: {'Accept': 'application/json'}
        });
        $.ajax({
            url: self.uri,
            success: function(data){
                $.each(data, function(key, host){
                    var name = host.name;
                    var mac_address = '';
                    if (host.interface.mac_address != null){
                        mac_address = host.interface.mac_address;
                    }
                    var network = '';
                    if (host.network.name != null) {
                        network = host.network.name;
                    }
                    var ip_addresses = '';
                    var result_ip_addresses = [];
                    $.each(host.addresses, function(address_key, address){
                        result_ip_addresses.push(address.ip);
                    });
                    ip_addresses = result_ip_addresses.join(', ');
                    var result = [
                        name,
                        mac_address,
                        network,
                        ip_addresses
                    ];
                    self.hosts.push(result);
                });
                self.show();
            }
        });
    }

    show() {
        var self = this;
//        console.log(self.hosts);
        $('#hosts').DataTable({
            data: self.hosts,
            columnDefs: [
                { type: 'ip-address', targets: 3}
            ],
            columns: [
                { title: 'name' ,
                    "fnCreatedCell": function (nTd, sData, oData, iRow, iCol) {
                        $(nTd).html("<a href='/hosts/"+sData+"'>"+sData+"</a>");
                    }
                },
                { title: 'MAC address'},
                { title: 'network'},
                { title: 'IP addresses'},
            ]
        });
    }

}

$(function(){
    new Hosts();
});