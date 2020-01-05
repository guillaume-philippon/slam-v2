class Host {
    constructor() {
        this.uri = $(location).attr('pathname');
        this.address_index = 0;
        this.address = new AddressCtrl()
        this._get()
    }

    _get() {
        var self = this;
        $.ajaxSetup({
            headers: {'Accept': 'application/json'}
        })
        $.ajax({
            url: self.uri,
            success: function(data){
                self.name = data.name
                self.interface = data.interface
                self.addresses = data.addresses
                self.network = data.network
                self.creation_date = data.creation_date
                self.dhcp = data.dhcp
                $.each(self.addresses, function(key, address){
                    if (key == self.address_index) {
                        self.address.set(address)
                        $('#network-edit-add-button').on('click', function(){
                            self.address.add()
                        })
                        $('#network-edit-add-name').change(function(){
                            self.address.check()
                        })
                        $('#network-edit-remove-button').on('click', function(){
                            self.address.remove()
                        })
                    }
                })
                self.show();
                self.address.show()
//                console.log(self)
            }
        })
    }

    remove() {
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
//                console.log(data)
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
//                console.log(mac_address)
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
        $.ajax({
            url: '/hardware/' + $('#hardware-name').text(),
            type: 'PUT',
            data: options,
            success: function(data){
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

class AddressCtrl {
    constructor() {
        this.ip = ''
        this.ns_entries = null;
    }

    set(address){
        this.ip = address.ip;
        this.ns_entries = address.ns_entries;
    }

    show() {
        var self = this;
        self.removable = []
        $('#network-edit-record-remove').empty()
        $('#network-edit-address').text(self.ip)
        $.each(self.ns_entries, function(key, record){
            $.each(record.entries, function(key, entry){
                var label = entry.name.replace(' (CNAME)','')
                var form_check = $('<div/>', {
                    class: 'form-check'
                })
                var input_checkbox = $('<input/>', {
                    class: 'form-check-input',
                    type: 'checkbox',
                    id: entry.name.replace(/\./g,'_').replace(' (CNAME)',''),
                    value: entry.name.replace(' (CNAME)','')
                })
                var label_checkbox = $('<label/>', {
                    class: 'form-check-label',
                    text: label
                })
                self.removable.push(entry.name.replace(/\./g,'_').replace(' (CNAME)',''))
                $('#network-edit-record-remove').append(
                    form_check.append(
                        input_checkbox,
                        label_checkbox
                    )
                )
            })
            var select_target = null
            if (record.type == 'A') {
                $('#network-edit-add-target').append(
                    new Option(record.name + '.' + record.domain.name,
                               record.name + '.' + record.domain.name))
            }
        })
        console.log(self.removable)
    }

    check() {
        var name_regex = new RegExp("^(([a-zA-Z0-9-_\.])*)*$");
        var new_record_name = $('#network-edit-add-name').val()
        console.log("new_record_name")
        console.log(new_record_name)
        $('#network-edit-add-button').attr('disabled', true)
        if (name_regex.test(new_record_name)) {
            $('#network-edit-add-button').attr('disabled', false)
        }
    }

    add() {
        var new_record_name = $('#network-edit-add-name').val()
        var new_record_domain = $('#network-edit-add-domain').val()
        var new_record_target_name = $('#network-edit-add-target').val().split('.')[0]
        var new_record_target_domain = $('#network-edit-add-target').val().split('.').slice(1).join('.')
        var self = this;
        var options = {
            'name': new_record_name,
            'domain': new_record_domain,
            'ns_type': 'CNAME',
            'sub_entry_name': new_record_target_name,
            'sub_entry_domain': new_record_target_domain,
            'sub_entry_type': 'A'
        }
        var csrftoken = $.cookie('csrftoken')
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/domains/' + new_record_domain + '/' + new_record_name,
            type: 'POST',
            data: options,
            success: function(data){
                        console.log(data)
                        $('#network-edit').modal('hide')
                    }
        })
        console.log(options)
//        self.show()
//        $('#network-edit').modal('hide')
    }

    remove() {
        var self = this;
        $.each(self.removable, function(key, record){
            if ($('#' + record).is(':checked')) {
                var record_to_delete = $("#" + record).val()
                var record_to_delete_name = record_to_delete.split('.')[0]
                var record_to_delete_domain = record_to_delete.split('.').slice(1).join('.')
                console.log(record_to_delete_name)
                console.log(record_to_delete_domain)
                var csrftoken = $.cookie('csrftoken')
                var options = {
                    'type': 'CNAME'
                }
                $.ajaxSetup({
                    headers: { "X-CSRFToken": csrftoken }
                });
                $.ajax({
                    url: '/domains/' + record_to_delete_domain + '/' + record_to_delete_name,
                    type: 'DELETE',
                    data: options,
                    success: function(data){
                                console.log(data)
                                $('#network-edit').modal('hide')
                            }
                })
            }
        })
//        self.show()
    }
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
            $('#network-edit-add-domain').append(new Option(domain, domain))
        })
    }
}

$(function(){
    var host = new Host()
    $('#delete-host').on('click', function(){
        host.remove()
    })
    var hardwareCtrl = new HardwareCtrl()
    $('#hardware-edit-save').on('click', function(){
        hardwareCtrl.save()
    })

    var domains = new DomainsCtrl();

    $('#network-edit').on('hidden.bs.modal', function () {
        host._get()
    });
})