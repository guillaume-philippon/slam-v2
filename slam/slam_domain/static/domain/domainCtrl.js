/*jshint esversion: 8 */

DOMAIN_CTRL_VIEW = {
    'view': {
        'name': '#domain-name',
        'description': '#domain-description',
        'dns_master': '#domain-dns-master',
        'contact': '#domain-contact',
        'creation_date': '#domain-creation-date',
        'records': '#domain-records'
    },
    'edit': {
        'button': '#domain-edit-btn'
    }
};

DOMAINS_CTRL_VIEW = {
    'select': '#domains-select',
    'dashboard': '#domains-dashboard'
};

RECORD_CTRL = {
    'name': '#record-name',
    'type': '#record-type',
    'addresses': '#record-addresses',
};

class DomainCtrl {
    constructor(domain, data){
        this.name = domain;
        // If we don't have info about the domain, we get it
        if (data == null) {
            this.get();
        }
    }

    get() {
//        console.log('-- DomainCtrl get --');
        var self = this;
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/domains/' + self.name,
            type: 'GET',
            success: function(data) {
                self.description = data.description;
                self.dns_master = data.dns_master;
                self.contact = data.contact;
                self.creation_date = data.creation_date;
                self.records = [];

                $.each(data.entries,function(_, record) {
                    var result_record = [
                        record.name + '.' + record.domain.name,
                        record.type,

                    ];
                    var result_addresses = [];
                    $.each(record.addresses, function(_, address) {
                        result_addresses.push(address.ip);
                    });
                    var result_sub_entries = [];
                    $.each(record.entries, function(_, sub_entry) {
                        result_sub_entries.push(sub_entry.name);
                    });
                    result_record.push(result_addresses.join(', '));
                    result_record.push(result_sub_entries.join(', '));
                    self.records.push(result_record);
                });
                self.view();
                self.edit();
            }
        });
    }

    put() {
        var self = this;
        var options = {};
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
                'Accept': 'application/json'
            }
        });
        $.ajax({
            url: '/domains/' + self.name,
            type: 'GET',
            success: function(data) {
                self.view();
                self.edit();
            }
        });
    }

    view() {
        $(DOMAIN_CTRL_VIEW.view.name).text(this.name);
        $(DOMAIN_CTRL_VIEW.view.description).text(this.description);
        $(DOMAIN_CTRL_VIEW.view.dns_master).text(this.dns_master);
        $(DOMAIN_CTRL_VIEW.view.contact).text(this.contact);
        $(DOMAIN_CTRL_VIEW.view.creation_date).text(this.creation_date);

        var records = [];
        $(DOMAIN_CTRL_VIEW.view.records).DataTable({
            data: this.records,
            columns: [
                { title: 'name' },
                { title: 'type'},
                { title: 'addresses'},
                { title: 'pointer'},
            ]
        });
    }

    edit() {
        $(DOMAIN_CTRL_VIEW.view.name + '-edit').val(this.name);
        $(DOMAIN_CTRL_VIEW.view.description + '-edit').val(this.description);
        $(DOMAIN_CTRL_VIEW.view.dns_master + '-edit').val(this.dns_master);
        $(DOMAIN_CTRL_VIEW.view.contact + '-edit').val(this.contact);
        $(DOMAIN_CTRL_VIEW.view.creation_date + '-edit').val(this.creation_date);
    }
}

class DomainsCtrl {
    constructor() {
        this.domains = [];
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
            url: '/domains',
            type: 'GET',
            success: function(data) {
//                console.log('-- DomainsCtrl GET --');
//                console.log(data);
                self.domains = data;
                self.view();
//                self.edit();
            }
        });
    }

    view() {
        this.view_select();
        this.view_dashboard();
    }

    view_select() {
        var self = this;
        $.each(this.domains, function(_, domain){
            $(DOMAINS_CTRL_VIEW.select).append(new Option(domain.name, domain.name));
            $(DOMAINS_CTRL_VIEW.select + '-loader').hide();
        });
    }

    static get_selected() {
//        console.log($(DOMAINS_CTRL_VIEW.select).val());
        return $(DOMAINS_CTRL_VIEW.select).val();
    }
    view_dashboard() {
        var self = this;
        $.each(this.domains, function(_, domain) {
//            console.log(' -- dashboard --')
//            console.log(network)
            var card = $('<div/>', {
                class: 'card ml-2 mb-2',
                style: 'width: 18rem'
            });
            var card_body = $('<div/>', {
                class: 'card-body'
            });
            var card_title = $('<h5/>', {
                class: 'card-title',
                text: domain.name
            });
            var card_subtitle = $('<h6/>', {
                class: 'card-subtitle mb-2 text-muted',
                text: domain.address
            });
            var card_text = $('<p/>', {
                class: 'card-text',
                text: domain.description
            });
            var card_link = $('<a/>', {
                href: '/domains/' + domain.name,
                class: 'card-link',
                text: 'More info.'
            });
            var card_record_div = $('<p/>', {
                class: 'text-right'
            });
            var card_record = $('<span/>', {
                class: 'badge badge-primary',
                text: domain.entries_count
            });
            $(DOMAINS_CTRL_VIEW.dashboard).append(
                card.append(
                    card_body.append(
                        card_title,
                        card_record_div.append(
                            card_record,
                        ),
                        card_subtitle,
                        card_text,
                        card_link
                    )
                )
            );
        });
    }
}

class RecordCtrl {
    constructor(name, domain, type) {
        this.name = name;
        this.domain = domain;
        if (type != null) {
            this.type = type;
        }
        this.exist = false;
        this.get();
    }

    async get() {
        var self = this;
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': $.cookie('csrftoken'),
                'Accept': 'application/json'
            }
        });
        await $.ajax({
            url: '/domains/' + self.domain + '/' + self.name,
            type: 'GET',
            success: function(data) {
                if (data.status == null) {
                    self.exist = true;
                    self.type = data.type;
                    self.entries = data.entries;
                    self.description = data.description;
                    self.creation_date = data.creation_date;
                }
            }
        });
    }

    async is_exist() {
        var name_regex = new RegExp("^(([a-zA-Z0-9-_\.])*)*$");
        await this.get();
        return this.exist;
    }
}