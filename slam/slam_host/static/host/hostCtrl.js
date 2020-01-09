/*jshint esversion: 8 */

HOST_CTRL_VIEW = {
    'view': {
        'name': '#host-name',
        'dhcp': '#host-dhcp'
    },
    'add': {
        'btn': '#host-add-btn',
        'alert': '#host-add-alert'
    },
}

class HostCtrl {
    constructor(name, data) {
        this.name = name;
        if (data == null) {
//            this.get()
        }
    }

    check() {
        console.log(' HostCtrl check');
        var name = $(HOST_CTRL_VIEW.edit.name).val()
        var domain = DomainCtrl.get_selected();

        $(HOST_CTRL_VIEW.edit.add.btn).attr('disabled', true);
        var domain_record = new RecordCtrl(name, domain, null);
        if (domain_record.exist) {
            console.log('-- exist --');
        }
    }
}