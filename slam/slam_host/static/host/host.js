class Host {
    constructor() {
        this.uri = $(location).attr('pathname');
        this._get()
        this.address_index = 0;
    }

    _get() {
        var self = this;
        $.ajaxSetup({
            headers: {'Accept': 'application/json'}
        })
        $.ajax({
            url: self.uri,
            success: function(data){
                console.log(data)
                self.name = data.name
                self.interface = data.interface
                self.addresses = data.addresses
                self.network = data.network
                self.creation_date = data.creation_date
                self.dhcp = data.dhcp
                self.show();
            }
        })
    }

    switch_index(new_index) {
        this.address_index = new_index;
        this.show_record()
        this.show_ip_address()
    }

    show_record() {
        var self = this;
        $('#records').text('')
        $.each(this.addresses, function(key, address){
            var records = $('<ul/>', {})
            if (key == self.address_index) {
                $.each(address.ns_entries, function(record_key, record){
                    records.append($('<li/>', {
                        text: record.name + '.' + record.domain.name + ' (' + record.type + ')'
                    }))
                    $.each(record.entries, function(entry_key, entry) {
                        records.append($('<li>', {
                            text: entry.name
                        }))
                    })
                })
                $('#records').append(records)
            }
        })
    }

    show_ip_address() {
        var self = this;
        $('#addresses').text('')
        $.each(this.addresses, function(key, address){
            var current_address = address
            var color = ''
            var body = $('<p/>',{})
            if (key == self.address_index) {
                color = 'btn-outline-primary'
            } else {
                color = 'btn-outline-secondary'
            }
            var ip_address = $('<button/>', {
                text: address.ip,
                class: 'btn btn-sm ml-1 ' + color,
                click: function(){
                    self.switch_index(key)
                }
            })
            $('#addresses').append(ip_address)
        })
    }

    show_interfaces() {
        var self = this;
        $('#interfaces').text('')
        if (this.interface != null && this.interface.hardware != null) {
            $.each(this.interface.hardware.interfaces, function(key, mac_address){
                var color = ''
                var disabled = true
                if (mac_address.mac_address == self.interface.mac_address) {
                    color = 'btn-primary'
                    disabled = false
                } else {
                    color = 'btn-outline-secondary'
                }
                var result_interface = $('<button/>', {
                    text: mac_address.mac_address,
                    class: 'btn btn-sm ml-1 mb-1 ' + color,
                    disabled: disabled
                })
                console.log(mac_address)
                $('#interfaces').append(result_interface)
            })
        }
    }

    show(){
        var selected_address = '';
        var self = this;
        $('#name').text(this.name)
        $('#network').text(this.network.name)
        $('#creation_date').text(this.creation_date)
        if (this.interface.hardware != null) {
            $('#hardware-name').text(this.interface.hardware.name)
            $('#hardware-mac-address').text(this.interface.mac_address)
            $('#hardware-owner').text(this.interface.hardware.owner)
            $('#hardware-buying-date').text(this.interface.hardware.buying_date)
            $('#hardware-description').text(this.interface.hardware.description)
        }
        self.show_record()
        self.show_ip_address()
        self.show_interfaces()
    }
}

$(function(){
    var host = new Host()
})