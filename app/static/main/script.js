$(document).ready(function () {
    load_home('load_home');
    var load_more = $("#id-load-more");
    load_more.on('click', function () {
        request_statuses('load_more')
    });

});


function appendStatusesList(statuses, status_template) {
    $.each(statuses, function (index, item) {
        var msg_item = status_template.clone();
        msg_item.css("display", "block");
        if (item.type == 'wei') {
            msg_item.attr('class', 'cls-message-items from-wei panel panel-danger')
        }
        else if (item.type == 'twi') {
            msg_item.attr('class', 'cls-message-items from-twi panel panel-info')
        }
        msg_item.find('.cls-user-thumbnail').find('img').attr('src', item.profile);
        msg_item.find('.cls-user-name').text(item.writer);
        msg_item.find('.cls-message-time').text(moment(item.time).fromNow());
        msg_item.find('.cls-message-text').text(item.text);

        var imgs = msg_item.find('.cls-message-img');
        if (imgs) {
            imgs.remove()
        }
        var new_imgs = $('<div/>', {
            class: 'cls-message-img'
        });
        $.each(item.imgs, function (index, img) {
            $('<div/>', {
                class: 'cls-img-wrapper'
            }).append(
                $('<img/>', {
                    src: img.origi,
                    class: "cls-img-origi"
                })
            ).appendTo(new_imgs)
        });
        new_imgs.appendTo(msg_item.find('.cls-message-content'));

        msg_item.appendTo($('#id-message-list'))
    })
}

function request_statuses(url) {
    $.get($SCRIPT_ROOT + url, {}, function (data) {
        data = $.parseJSON(data);
        if (data.status == 200) {
            var statuses = data.content;
            var last_status = $('.cls-message-items').eq(-1);
            appendStatusesList(statuses, last_status);
        }
        else {
            alert(data.msg)
        }
    })
}

function load_home(url) {
    request_statuses(url)
}