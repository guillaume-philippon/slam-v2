$(function() {
    var path = $(location).attr('pathname').split('/');
    var domain = path[2];
    new DomainCtrl(domain);
});