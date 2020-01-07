/* jshint esversion: 8 */

HARDWARE_CTRL_VIEW = {
    'view': {
        'mac_address': '#hw-interface-mac-address'
    }
}

class HardwareCtrl {
    constructor() {
        console.log('Interface Ctrl')
    }

    check() {
        var mac_address_regex = new RegExp('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])');
        return (mac_address_regex.test(this.mac_address) || this.mac_address == '')
    }
}