/*jshint esversion: 8 */

class Host {
    constructor() {
        this.uri = $(location).attr('pathname');
        this.address_index = 0;
        this.address = new AddressCtrl();
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
                $('#network-edit-add-button').unbind();
                $('#network-edit-remove-button').unbind();
                self.name = data.name;
                self.interface = data.interface;
                self.addresses = data.addresses;
                self.network = data.network;
                self.creation_date = data.creation_date;
                self.dhcp = data.dhcp;
                $.each(self.addresses, function(key, address){
                    if (key == self.address_index) {
                        self.address.set(address);
                        $('#network-edit-add-button').on('click', function(){
                            self.address.add();
                        });
                        $('#network-edit-add-name').change(function(){
                            self.address.check();
                        });
                        $('#network-edit-remove-button').on('click', function(){
                            self.address.remove();
                        });
                    }
                });
                self.show();
                self.address.show();
            }
        });
    }

    save () {
        var self = this;
        var options = {};
        var csrftoken = $.cookie('csrftoken');
        options['dhcp'] = $('#host-dhcp').is(':checked');
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/hosts/' + $('#name').text(),
            type: 'PUT',
            data: options,
            success: function(data){
                    self._get();
                }
        });
    }

    remove() {
        var csrftoken = $.cookie('csrftoken');
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
                if (data.status == 'done') {
                    $(location).attr('pathname', '/hosts');
                }
            }
        });
    }

    switch_index(new_index) {
        this.address_index = new_index;
        this._get();
    }

    show_record() {
        var self = this;
        $('#records').empty();
        $.each(this.addresses, function(key, address){
            var records = $('<ul/>', {});
            if (key == self.address_index) {
                $.each(address.ns_entries, function(record_key, record){
                    records.append($('<li/>', {
                        text: record.name + '.' + record.domain.name + ' (' + record.type + ')'
                    }));
                    $.each(record.entries, function(entry_key, entry) {
                        records.append($('<li>', {
                            text: entry.name
                        }));
                    });
                });
                $('#records').append(records);
            }
        });
    }

    show_ip_address() {
        var self = this;
        $('#addresses').empty();
        $.each(this.addresses, function(key, address){
            var color = '';
            if (key == self.address_index) {
                color = 'btn-success';
            } else {
                color = 'btn-outline-secondary';
            }
            var ip_address = $('<button/>', {
                text: address.ip,
                class: 'btn btn-sm ml-1 ' + color,
                click: function(){
                    self.switch_index(key);
                }
            });
            $('#addresses').append(ip_address);
        });
    }

    show_interfaces() {
        var self = this;
        $('#interfaces').empty();
        if (this.interface != null && this.interface.hardware != null) {
            $('#interface-add-btn').hide();
            $('#interface-remove-confirm-btn').show();
            $.each(this.interface.hardware.interfaces, function(key, mac_address){
                var color = '';
                var disabled = true;
                if (mac_address.mac_address == self.interface.mac_address) {
                    color = 'btn-primary';
                    disabled = false;
                } else {
                    color = 'btn-outline-secondary';
                }
                var result_interface_div = $('<div/>', {});
                var result_interface = $('<button/>', {
                    text: mac_address.mac_address,
                    class: 'btn btn-sm ml-1 mb-1 ' + color,
                    disabled: disabled
                });
                $('#interfaces').append(result_interface);
            });
        } else {
            $('#interface-remove-confirm-btn').hide();
            $('#interface-add-btn').show();
        }
    }

    show(){
        var self = this;
        $('#hardware').hide();
        $('#hardware-add').show();
        $('#name').text(this.name);
        $('#host-delete-confirm-name').text(this.name);
        $('#network').text(this.network.name);
        $('#creation_date').text(this.creation_date);
        $('#host-dhcp').prop('checked', this.dhcp)
        if (this.interface.hardware != null) {
            $('#hardware-add').hide();
            $('#hardware').show();
            $('#hardware-name').text(this.interface.hardware.name);
            $('#hardware-mac-address').text(this.interface.mac_address);
            $('#hardware-owner').text(this.interface.hardware.owner);
            $('#hardware-buying-date').text(this.interface.hardware.buying_date);
            $('#hardware-description').text(this.interface.hardware.description);

            $('#hardware-name-edit').val(this.interface.hardware.name);
//            $('#hardware-mac-address').text(this.interface.mac_address);
            $('#hardware-owner-edit').val(this.interface.hardware.owner);
            $('#hardware-buying-date-edit').val(this.interface.hardware.buying_date);
            $('#hardware-description-edit').val(this.interface.hardware.description);
        }
        self.show_record();
        self.show_ip_address();
        self.show_interfaces();
    }
}

class HardwareCtrl {
    constructor(){
        this.name = $(HARDWARE_CTRL_VIEW.view.name + '-edit').val();
        this.owner = $(HARDWARE_CTRL_VIEW.view.owner + '-edit').val();
        this.buying_date = $(HARDWARE_CTRL_VIEW.view.buying_date + '-edit').val();
        this.description = $(HARDWARE_CTRL_VIEW.view.description + '-edit').val();
        this.vendor = $(HARDWARE_CTRL_VIEW.view.vendor + '-edit').val();
        this.model = $(HARDWARE_CTRL_VIEW.view.model + '-edit').val();
        this.serial_number = $(HARDWARE_CTRL_VIEW.view.serial_number + '-edit').val();
        this.inventory = $(HARDWARE_CTRL_VIEW.view.inventory + '-edit').val();
        this.warranty = $(HARDWARE_CTRL_VIEW.view.warranty + '-edit').val();
//        'vendor': '#hardware-vendor',
//        'model': '#hardware-model',
//        'serial_number': '#hardware-serial-number',
//        'inventory': '#hardware-inventory',
//        'warranty': '#hardware-warranty',
    }

    save() {
        var new_name = $(HARDWARE_CTRL_VIEW.view.name + '-edit').val();
        var new_owner = $(HARDWARE_CTRL_VIEW.view.owner + '-edit').val();
        var new_buying_date = $(HARDWARE_CTRL_VIEW.view.buying_date + '-edit').val();
        var new_description = $(HARDWARE_CTRL_VIEW.view.description + '-edit').val();
        var new_vendor = $(HARDWARE_CTRL_VIEW.view.vendor + '-edit').val();
        var new_model = $(HARDWARE_CTRL_VIEW.view.model + '-edit').val();
        var new_serial_number = $(HARDWARE_CTRL_VIEW.view.serial_number + '-edit').val();
        var new_inventory = $(HARDWARE_CTRL_VIEW.view.inventory + '-edit').val();
        var new_warranty = $(HARDWARE_CTRL_VIEW.view.warranty + '-edit').val();
        var options = {};
        if ( new_name != this.name ) {
            options.name = new_name;
        }
        if ( new_owner != this.owner ) {
            options.owner = new_owner;
        }
        if ( new_buying_date != this.buying_date ) {
            options.buying_date = new_buying_date;
        }
        if ( new_description != this.description ) {
            options.description = new_description;
        }
        if ( new_vendor != this.vendor ) {
            options.vendor = new_vendor;
        }
        if ( new_model != this.model ) {
            options.model = new_model;
        }
        if ( new_serial_number != this.serial_number ) {
            options.serial_number = new_serial_number;
        }
        if ( new_inventory != this.inventory ) {
            options.inventory = new_inventory;
        }
        if ( new_warranty != this.warranty ) {
            options.warranty = new_warranty;
        }
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/hardware/' + $(HARDWARE_CTRL_VIEW.view.name).text(),
            type: 'PUT',
            data: options,
            success: function(data){
                if (data.status != 'failed') {
                    $(HARDWARE_CTRL_VIEW.view.name).text(data.name);
                    $(HARDWARE_CTRL_VIEW.view.owner).text(data.owner);
                    $(HARDWARE_CTRL_VIEW.view.buying_date).text(data.buying_date);
                    $(HARDWARE_CTRL_VIEW.view.description).text(data.description);
                    $(HARDWARE_CTRL_VIEW.view.vendor).text(data.vendor);
                    $(HARDWARE_CTRL_VIEW.view.model).text(data.model);
                    $(HARDWARE_CTRL_VIEW.view.serial_number).text(data.serial_number);
                    $(HARDWARE_CTRL_VIEW.view.inventory).text(data.inventory);
                    $(HARDWARE_CTRL_VIEW.view.warranty).text(data.warranty);

                    this.name = $(HARDWARE_CTRL_VIEW.view.name + '-edit').val();
                    this.owner = $(HARDWARE_CTRL_VIEW.view.owner + '-edit').val();
                    this.buying_date = $(HARDWARE_CTRL_VIEW.view.buying_date + '-edit').val();
                    this.description = $(HARDWARE_CTRL_VIEW.view.description + '-edit').val();
                    this.vendor = $(HARDWARE_CTRL_VIEW.view.vendor + '-edit').val();
                    this.model = $(HARDWARE_CTRL_VIEW.view.model + '-edit').val();
                    this.serial_number = $(HARDWARE_CTRL_VIEW.view.serial_number + '-edit').val();
                    this.inventory = $(HARDWARE_CTRL_VIEW.view.inventory + '-edit').val();
                    this.warranty = $(HARDWARE_CTRL_VIEW.view.warranty + '-edit').val();
                    // $('#hardware-edit').modal('hide');
                    $('#hardware').show();
                    $('#hardware-add').hide();
                }
            }
        });
    }

    async add_interface() {
        var options = {
            'interface': $('#hardware-add-interface').val()
        };
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/hosts/' + $('#name').text(),
            type: 'PUT',
            data: options,
            success: function(data){
                if (data.status != 'failed') {
                    $(HARDWARE_CTRL_VIEW.view.name).text(data.name);
                    $(HARDWARE_CTRL_VIEW.view.owner).text(data.owner);
                    $(HARDWARE_CTRL_VIEW.view.buying_date).text(data.buying_date);
                    $(HARDWARE_CTRL_VIEW.view.description).text(data.description);
                    // $('#hardware-edit').modal('hide');
                }
            }
        });
    }
}

class AddressCtrl {
    constructor() {
        this.ip = '';
        this.ns_entries = null;
    }

    set(address){
        this.ip = address.ip;
        this.ns_entries = address.ns_entries;
    }

    show() {
        var self = this;
        self.removable = [];
        $('#network-edit-record-remove').empty();
        $('#network-edit-add-target').empty();
        $('#network-edit-address').text(self.ip);
        $.each(self.ns_entries, function(key, record){
            $.each(record.entries, function(record_key, entry){
                var label = entry.name.replace(' (CNAME)','');
                var form_check = $('<div/>', {
                    class: 'form-check'
                });
                var input_checkbox = $('<input/>', {
                    class: 'form-check-input',
                    type: 'checkbox',
                    id: entry.name.replace(/\./g,'_').replace(' (CNAME)',''),
                    value: entry.name.replace(' (CNAME)','')
                });
                var label_checkbox = $('<label/>', {
                    class: 'form-check-label',
                    text: label
                });
                self.removable.push(entry.name.replace(/\./g,'_').replace(' (CNAME)',''));
                $('#network-edit-record-remove').append(
                    form_check.append(
                        input_checkbox,
                        label_checkbox
                    )
                );
            });
            if (record.type == 'A') {
                $('#network-edit-add-target').append(
                    new Option(record.name + '.' + record.domain.name,
                               record.name + '.' + record.domain.name));
            }
        });
//        console.log(self.removable);
    }

    check() {
        var name_regex = new RegExp("^(([a-zA-Z0-9-_\.])*)*$");
        var new_record_name = $('#network-edit-add-name').val();
        $('#network-edit-add-button').attr('disabled', true);
        if (name_regex.test(new_record_name)) {
            $('#network-edit-add-button').attr('disabled', false);
        }
    }

    add() {
        var new_record_name = $('#network-edit-add-name').val();
        var new_record_domain = $('#network-edit-add-domain').val();
        var new_record_target_name = $('#network-edit-add-target').val().split('.')[0];
        var new_record_target_domain = $('#network-edit-add-target').val().split('.')
                                                                    .slice(1).join('.');
        var options = {
            'name': new_record_name,
            'domain': new_record_domain,
            'ns_type': 'CNAME',
            'sub_entry_name': new_record_target_name,
            'sub_entry_domain': new_record_target_domain,
            'sub_entry_type': 'A'
        };
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/domains/' + new_record_domain + '/' + new_record_name,
            type: 'POST',
            data: options,
            success: function(data){
                        $('#network-edit').modal('hide');
                    }
        });
    }

    remove() {
        var self = this;
        $.each(self.removable, function(key, record){
            if ($('#' + record).is(':checked')) {
                var record_to_delete = $("#" + record).val();
                var record_to_delete_name = record_to_delete.split('.')[0];
                var record_to_delete_domain = record_to_delete.split('.').slice(1).join('.');
                var csrftoken = $.cookie('csrftoken');
                var options = {
                    'type': 'CNAME'
                };
                $.ajaxSetup({
                    headers: { "X-CSRFToken": csrftoken }
                });
                $.ajax({
                    url: '/domains/' + record_to_delete_domain + '/' + record_to_delete_name,
                    type: 'DELETE',
                    data: options,
                    success: function(data){
                                console.log(data);
//                                $('#network-edit').modal('hide');
                            }
                });
                $(document).ajaxStop(function(){
                    $('#network-edit').modal('hide');
                });
            }
        });
//        self.show();
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
        });
        $.ajax({
            url: self.uri,
            success: function(data){
                $.each(data, function(key, item){
                    self.domains.push(item.name);
                });
                self.show();
            }
        });
    }

    show() {
        var self = this;
        $('#network-edit-add-domain').empty();
        $.each(self.domains, function(key, domain){
            $('#network-edit-add-domain').append(new Option(domain, domain));
        });
    }
}

class InterfaceCtrl {
    unlink() {
        var csrftoken = $.cookie('csrftoken');
        var options = {
            'interface': ''
        };
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/hosts/' + $('#name').text(),
            type: 'PUT',
            data: options,
            success: function(data){
                if (data.status != 'failed') {
                    console.log(data);
                    $('#interface-remove-confirm').modal('hide');
                }
            }
        });
    }

    link(mac_address) {
        var csrftoken = $.cookie('csrftoken');
        var options = {
            'interface': ''
        };
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": csrftoken,
                'Accept': 'application/json'
            }
        });
//        $.ajax({
//            url: '/hosts/' + $('#name').text(),
//            type: 'PUT',
//            data: options,
//            success: function(data){
//                if (data.status != 'failed') {
//                    console.log(data);
//                    $('#unlink-interface-confirm').modal('hide');
//                }
//            }
//        });
    }
}

$(function(){
//    console.log('load host');
    var host = new Host();
    $('#delete-host').on('click', function(){
        host.remove();
    });
    $('#host-save-confirm').on('click', function(){
        host.save();
    });
//    console.log('load hardware');
    var hardwareCtrl = new HardwareCtrl();
    $('#hardware-edit-save').on('click', function(){
        hardwareCtrl.save();
    });
//    console.log('load domain');
    new DomainsCtrl();
//    console.log('load interface');
    var mac_address = new InterfaceCtrl();

//    console.log('bind unlink-interface-btn')
//    console.log(mac_address)
    $('#unlink-interface-btn').on('click', function(){
        mac_address.unlink();
        host._get();
    });
    $('#hardware-add-btn').on('click', function(){
        hardwareCtrl.add_interface();
        host._get();
    });

//    console.log('bind network-edit')
    $('#network-edit').on('hidden.bs.modal', function () {
        host._get();
    });

//    console.log('bind unlink-interface-confirm')
    $('#interface-remove-confirm').on('hidden.bs.modal', function () {
        host._get();
    });
});