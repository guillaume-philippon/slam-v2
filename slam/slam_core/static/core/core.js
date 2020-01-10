/*jshint esversion: 6 */


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


class CommitPublishCtrl{
    commit() {
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            headers: { "X-CSRFToken": csrftoken }
        });
        $.ajax({
            url: '/producer/commit/',
            type: 'POST',
            success: function(data){
                        $('#commit-publish-diff').text(data.data);
                        $('#commit-publish-publish').attr("disabled", false);
                    }
        });
    }

    publish() {
        $('#commit-publish-publish').attr("disabled", true);
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
        ctrl.commit();
    });
    $('#commit-publish-publish').on('click', function(){
        ctrl.publish();
    });
});