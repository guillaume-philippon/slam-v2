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

    delete() {
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/hosts/' + $('#name').text(),
            type: 'DELETE',
            success: function(data){
                console.log(data)
                if (data.status == 'done') {
                    $(location).attr('pathname', '/hosts')
                }
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
        $('#host-delete-confirm-name').text(this.name)
        $('#network').text(this.network.name)
        $('#creation_date').text(this.creation_date)
        if (this.interface.hardware != null) {
            $('#hardware-name').text(this.interface.hardware.name)
            $('#hardware-mac-address').text(this.interface.mac_address)
            $('#hardware-owner').text(this.interface.hardware.owner)
            $('#hardware-buying-date').text(this.interface.hardware.buying_date)
            $('#hardware-description').text(this.interface.hardware.description)

            $('#hardware-name-edit').val(this.interface.hardware.name)
//            $('#hardware-mac-address').text(this.interface.mac_address)
            $('#hardware-owner-edit').val(this.interface.hardware.owner)
            $('#hardware-buying-date-edit').val(this.interface.hardware.buying_date)
            $('#hardware-description-edit').val(this.interface.hardware.description)
        }
        self.show_record()
        self.show_ip_address()
        self.show_interfaces()
    }
}

class HardwareCtrl {
    constructor(){
        this.name = $('#hardware-name-edit').val()
        this.owner = $('#hardware-owner-edit').val()
        this.buying_date = $('#hardware-buying-date-edit').val()
        this.description = $('#hardware-description-edit').val()
    }

    save() {
        var new_name = $('#hardware-name-edit').val()
        var new_owner = $('#hardware-owner-edit').val()
        var new_buying_date = $('#hardware-buying-date-edit').val()
        var new_description = $('#hardware-description-edit').val()
        var options = {}
        if ( new_name != this.name ) {
            options['name'] = new_name
        }
        if ( new_owner != this.owner ) {
            options['owner'] = new_owner
        }
        if ( new_buying_date != this.buying_date ) {
            options['buying_date'] = new_buying_date
        }
        if ( new_name != this.description ) {
            options['description'] = new_description
        }
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        console.log(options)
        $.ajax({
            url: '/hardware/' + $('#hardware-name').text(),
            type: 'PUT',
            data: options,
            success: function(data){
                console.log(data)
                if (data.status != 'failed') {
                    $('#hardware-name').text(data.name)
                    $('#hardware-owner').text(data.owner)
                    $('#hardware-buying-date').text(data.buying_date)
                    $('#hardware-description').text(data.description)
                    $('#hardware-edit').modal('hide')
                }
            }
        })
    }
}

$(function(){
    var host = new Host()
    $('#delete-host').on('click', function(){
        host.delete()
    })
    var hardwareCtrl = new HardwareCtrl()
    $('#hardware-edit-save').on('click', function(){
        hardwareCtrl.save()
    })
})