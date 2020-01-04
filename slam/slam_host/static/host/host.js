class Host {
    constructor() {
        this.uri = $(location).attr('pathname');
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

    show(){
        var selected_address = '';
        var self = this;
        $('#name').text(this.name)
        $('#network').text(this.network.name)
        $('#creation_date').text(this.creation_date)
        if (this.interface.hardware != null) {
            $('#hardware-name').val(this.interface.hardware.name)
            $('#hardware-mac-address').val(this.interface.mac_address)
            $('#hardware-owner').val(this.interface.hardware.owner)
            $('#hardware-buying-date').val(this.interface.hardware.buying_date)
            $('#hardware-description').val(this.interface.hardware.description)
        }

        $.each(this.addresses, function(key, address){
            var current_address = address
            $.each(address.ns_entries, function(key, record){
                if (record.type == 'PTR') {
                    selected_address = current_address
                }
            })
        })
        console.log(selected_address)
    }
}

$(function(){
    var host = new Host()
})