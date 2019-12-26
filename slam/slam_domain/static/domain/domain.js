/*jshint esversion: 6 */

class DomainsViewListener {
    constructor (domains) {
        this.modified = [];
        this.domains = domains;

        var self = this;

        $('#domain-name').change(function(){
            self.modify('#domain-name');
        });
        $('#domain-description').change(function(){
            self.modify('#domain-description');
        });
        $('#domain-dns-master').change(function(){
            self.modify('#domain-dns-master');
        });
        $('#domain-contact').change(function(){
            self.modify('#domain-contact');
        });
        $('#domain-add').click(function(){
            self.domains.add();
            self.domains.active = 'example.com';
            self.fill_nav();
            self.fill_form();
        });
        $('#domain-update').click(function(){
            var values = {
                name: $('#domain-name').val(),
                description: $('#domain-description').val(),
                master: $('#domain-dns-master').val(),
                contact: $('#domain-contact').val()
            };
            if (values.name != self.domains.active) {
                $('#li-' + self.domains.active.replace(/\./g,'_')).remove();
            }
            self.domains.update(values);
            self.fill_nav();
            self.fill_form();
        });

        this.fill_nav();
        this.fill_form();
    }

    modify (field) {
        var self = this;
        if (! this.modified.includes(field)) {
            this.modified.push(field);
        }
        $('#domain-update').removeClass('btn-outline-secondary');
        $('#domain-update').addClass('btn-outline-primary');
        $('#domain-update').prop('disabled', false);
    }

    reset () {
        $('#domain-update').addClass('btn-outline-secondary');
        $('#domain-update').removeClass('btn-outline-primary');
        $('#domain-update').prop('disabled', true);
    }

    fill_nav () {
        var self = this;
        var classes = '';
        $.each(self.domains.domains, function(key, domain) {
            if (self.domains.active == domain.name) {
                classes = 'nav-link active';
            } else {
                classes = 'nav-link';
            }
            var link = $(
                '<a/>', {
                    href: '#',
                    id: 'a-' + domain.name.replace(/\./g,'_'),
                    text: domain.name,
                    class: classes
                }
            );
            var tab = $(
                '<li/>', {
                    class: 'nav-item',
                    id: 'li-' + domain.name.replace(/\./g,'_'),
                    click: function(){
                        self.domains.active = domain.name;
                        self.fill_nav();
                        self.fill_form();
                    }
                }
            );

            if ( $('#a-' + domain.name.replace(/\./g,'_')).length ) {
                if (self.domains.active == domain.name) {
                    $('#a-' + domain.name.replace(/\./g,'_')).addClass('active');
                } else {
                    $('#a-' + domain.name.replace(/\./g,'_')).removeClass('active');
                }
            } else {
                $('#nav-domains').append(tab.append(link));
            }
        });
        self.reset();
    }

    fill_form () {
        var self = this;

        $.each(this.domains.domains, function(key, domain){
            if (self.domains.active == domain.name){
                $('#domain-name').val(domain.name);
                $('#domain-description').val(domain.description);
                $('#domain-dns-master').val(domain.master);
                $('#domain-contact').val(domain.contact);
            }
        });
    }
}

class DomainsModelController {
    constructor () {
        this.uri = '/domains?format=json';
    }

    get() {
        var self = this;
        var result = [];
        $.ajax({
            url: self.uri,
            async: false,
            success: function(data){
                $.each(data, function(key, item){
                    var current_domain = new Domain(item.name);
                    current_domain.description = item.description;
                    current_domain.master = item.master;
                    current_domain.contact = item.contact;
                    result.push(current_domain);
                });
            }
        });
        return result;
    }
}

class Domain {
    constructor (name) {
        this.name = name;
        this.description = '';
        this.master = '';
        this.contact = '';
    }

    update(values) {
        this.name = values.name;
        this.description = values.description;
        this.master = values.master;
        this.contact = values.contact;
        this.post();
    }

    post () {
        var result = {};

        result.name = this.name;
        result.description = this.description;
        result.master = this.master;
        result.contact = this.contact;
    }
}

class Domains {
    constructor(domains) {
        this.domains = domains;
        this.active = domains[0].name;
    }

    update(values) {
        var self = this;
        $.each(self.domains, function(key, domain){
            if (domain.name == self.active) {
                domain.update(values);
            }
        });
    }

    add() {
        var new_domain_name = 'example.com';
        var new_domain;
        var self = this;
        var exist = false;

        $.each(self.domains, function(key, domain){
            if (domain.name == new_domain_name) {
                exist = true;
            }
        });
        if (! exist) {
            new_domain = new Domain(new_domain_name);
            this.domains.push(new_domain);
        }
    }
}

$(function(){
    var domains_ctrl = new DomainsModelController();
    var domains_dict = domains_ctrl.get()
    var domains = new Domains(domains_dict);
    var listener = new DomainsViewListener(domains);
});