/*jshint esversion: 6 */


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


class CommitPublishCtrl{
    commit() {
        console.log('commit')
        var csrftoken = $.cookie('csrftoken');
        $('#commit-publish-commit').attr("disabled", true);
        $('#commit-publish-diff').text('Please Wait...');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/commit/',
            type: 'POST',
            success: function(data){
                        console.log(data)
                        $('#commit-publish-diff').text(data.data);
                        $('#commit-publish-publish').attr("disabled", false);
                    }
        });
    }

    publish() {
        $('#commit-publish-publish').attr("disabled", true);
        $('#commit-publish-commit').attr("disabled", false);
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/publish/',
            type: 'POST',
            success: function(data){
                        $('#commit-publish-diff').text('');
                        $('#commit-publish').modal('hide');
                    }
        });
    }
}

$(function(){
    var ctrl = new CommitPublishCtrl();
    $('#commit-publish-commit').on('click', function(){
        console.log('clicked')
        ctrl.commit();
    });
    $('#commit-publish-publish').on('click', function(){
        ctrl.publish();
    });
});