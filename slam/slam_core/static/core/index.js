/*jshint esversion: 6 */

class NetworksCtrl {
    constructor () {
        this.uri = '/networks';
        this.networks = [];
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
                    self.networks.push(item.name);
                });
            }
        });
    }
}