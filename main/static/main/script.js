$(document).ready(function () {
    var load_more = $("#id-load-more");
    load_more.on('click', function () {
        $.get($SCRIPT_ROOT + 'load_more/', {}, function (data) {
            alert(data.content);
            if (data.status == 200) {
                var statuses = data.content;
                var last_status = $('.cls-message-items').eq(-1);
                appendStatusesList(statuses, last_status);
            }
            else {
                alert(data.msg)
            }
        })
    })
});

function appendStatusesList(statuses, status_template) {
    $.each(statuses, function (index) {
        var msg_item = status_template.clone();
        if ($(this).type == 'wei') {
            msg_item.attr('class', 'cls-message-items from-wei panel panel-danger')
        }
        else {
            msg_item.attr('class', 'cls-message-items from-wei panel panel-danger')
        }
        alert(msg_item.html());
        // msg_item.find('.cls-user-thumbnail').find('img').attr('src', $(this).profile);
        // msg_item.find('.cls-user-name').text($(this).writer);
        // msg_item.find('.cls-message-time').text($(this).time);
        // msg_item.find('.cls-message-text').text($(this).text);
        // msg_item.appendTo($('#id-message-list'))
    })
}