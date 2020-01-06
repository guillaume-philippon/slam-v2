/*jshint esversion: 6 */

class Network {
    constructor() {
        this.uri = $(location).attr('pathname');
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
                console.log(data);
                self.name = data.name;
                self.address = data.address;
                self.prefix = data.prefix;
                self.description = data.description;
                self.total = data.total;
                self.used = data.used_addresses;
                self.addresses = data.addresses;
                self.show();
            }
        });
    }

    show() {
        var self = this;
        var used_per_cent = (this.used * 100) / this.total;
        $('#name').text(this.name);
        $('#address').text(this.address + '/' + this.prefix);
        $('#description').text(this.description);
        var progress_bar = $('<div/>',{
            class: 'progress-bar progress-bar-striped',
            role: 'progressbar',
            style: 'width: ' + used_per_cent + '%'
        });
        $('#progress').append(progress_bar);
        var datatable_addresses = [];
        $.each(self.addresses, function(key, address){
            var ptr_record = '';
            $.each(address.ns_entries, function(key, record){
                if (record.type == 'PTR') {
                    ptr_record = record.name + '.' + record.domain.name;
                }
            });
            datatable_addresses.push([
                address.ip,
                ptr_record,
                address.creation_date,
            ]);
        });
        $('#addresses').DataTable({
            data: datatable_addresses,
            columns: [
                { title: 'address' },
                { title: 'reverse DNS'},
                { title: 'creation date'}
            ]
        });
    }
}

$(function(){
    new Network();
});