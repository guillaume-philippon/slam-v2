function search () {
    var csrftoken = $.cookie('csrftoken');
    $.ajaxSetup({
        headers: { "X-CSRFToken": csrftoken,
            "Accept": 'application/json'
         }
    });
    $.ajax({
        url: $(location).attr('href'),
        type: 'GET',
        success: function(data){
                    console.log(data);
                    $.each(data.hosts, function(_, record){
                        var addresses = [];
                        $.each(record.addresses,function(_, ip){
                            addresses.push(ip.ip)
                        });
                        var card_link = $('<a/>', {
                            href: '/hosts/' + record.name,
                            text: record.name
                        })
                        var card = $('<div/>', {
                            class: 'card ml-2 mb-2 col-sm-3'
                        });
                        var card_body = $('<div/>', {
                            class: 'card-body'
                        });
                        var card_title = $('<h5/>', {
                            class: 'card-title'
                        });
                        var card_interface = $('<p/>', {
                            class: 'card-text',
                            text: 'MAC Address: ' + record.interface.mac_address
                        });
                        var card_addresses = $('<p/>', {
                            class: 'card-text',
                            text: 'Address (es): ' + addresses.join(', ')
                        });
                        $('#results').append(
                            card.append(
                                card_body.append(
                                    card_title.append(
                                        card_link
                                    ),
                                    card_interface,
                                    card_addresses
                                )
                            )
                        )
                    })
        }
    });
}

$(function(){
    search();
})