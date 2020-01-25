/* jshint esversion: 8 */

let HARDWARE_CTRL_VIEW = {
    'view': {
        'name': '#hardware-name',
        'buying_date': '#hardware-buying-date',
        'description': '#hardware-description',
        'owner': '#hardware-owner',
        'vendor': '#hardware-vendor',
        'model': '#hardware-model',
        'serial_number': '#hardware-serial-number',
        'inventory': '#hardware-inventory',
        'warranty': '#hardware-warranty',
        'mac_address': '#hw-interface-mac-address'
    }
};

//class HardwareCtrl {
//    constructor() {
//        console.log('Interface Ctrl')
//    }
//
//    check() {
//        var mac_address_regex = new RegExp('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])');
//        return (mac_address_regex.test(this.mac_address) || this.mac_address == '')
//    }
//}