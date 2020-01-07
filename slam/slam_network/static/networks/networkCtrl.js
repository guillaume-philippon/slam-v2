/*jshint esversion: 8 */

NETWORK_CTRL_VIEW = {
    'view': {
        'name': '#network-name',
        'description': '#network-description',
    }
}

NETWORKS_CTRL_VIEW = {
    'select': '#networks-select',
    'dashboard': '#networks-dashboard'
}

class NetworkCtrl {
    constructor(network, data) {
        this.name = network;
        if (data == null) {
            this.get();
        }
    }

    get() {
        var self = this;
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/networks/' + self.name,
            type: 'GET',
            success: function(data) {
//                console.log('-- NetworkCtrl GET --');
//                console.log(data);
                self.view();
                self.edit();
            }
        });
    }
}

class NetworksCtrl {
    constructor() {
        this.networks = [];
        this.get();
    }

    get() {
        var self = this;
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/networks',
            type: 'GET',
            success: function(data) {
//                console.log('-- NetworksCtrl GET --');
//                console.log(data);
                self.networks = data;
                self.view();
            }
        });
    }

    view() {
        this.view_select();
        this.view_dashboard();
    }

    view_select() {
        var self = this;
        $.each(this.networks, function(_, network){
            $(NETWORKS_CTRL_VIEW.select).append(new Option(network.name, network.name));
            $(NETWORKS_CTRL_VIEW.select + '-loader').hide();
        });
    }

    view_dashboard() {
        var self = this;
        $.each(this.networks, function(_, network) {
//            console.log(' -- dashboard --')
//            console.log(network)
            var used_per_cent = network.used_addresses * 100 / network.total
            console.log(used_per_cent)
            var card = $('<div/>', {
                class: 'card ml-2 mb-2',
                style: 'width: 18rem'
            });
            var card_body = $('<div/>', {
                class: 'card-body'
            });
            var card_title = $('<h5/>', {
                class: 'card-title',
                text: network.name
            });
            var card_subtitle = $('<h6/>', {
                class: 'card-subtitle mb-2 text-muted',
                text: network.address + '/' + network.prefix
            });
            var card_text = $('<p/>', {
                class: 'card-text',
                text: network.description
            });
            var card_link = $('<a/>', {
                href: '/networks/' + network.name,
                class: 'card-link',
                text: 'More info.'
            });
            var progress = $('<div/>', {
                class: 'progress'
            });
            var progress_bar = $('<div/>', {
                class: 'progress-bar progress-bar-stripped',
                role: 'progressbar',
                style: 'width: ' + used_per_cent + '%'
            });
            $(NETWORKS_CTRL_VIEW.dashboard).append(
                card.append(
                    card_body.append(
                        card_title,
                        card_subtitle,
                        progress.append(
                            progress_bar
                        ),
                        card_text,
                        card_link
                    )
                )
            );
        });
    }

    static get_selected() {
//        console.log(' -- NetworkCtrl selected ---')
        return $(NETWORKS_CTRL_VIEW.select).val()
    }
}
