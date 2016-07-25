$(document).ready(function () {
    if (window.location.pathname == '/') {
        load_home('load_home');

        var load_more = $("#id-load-more");
        load_more.on('click', function () {
            request_statuses('load_more')
        });

        focus_mode(".cls-img-wrapper img", 0.7, 1, true);

        $(window).on("resize", function () {
            resize_imgs();
        });

        var msg_list = $("#id-message-list");
        msg_list.on("click", ".cls-like-msg", function () {
            var msg = $(this).parents('.cls-message-items');
            like_or_unlike_msg(msg)
        });

        $('.image-link').magnificPopup({type: 'image'});
    }

    if (window.location.pathname == '/login') {
        var weibo_login = $("#id-login-by-wei");
        weibo_login.on("click", function () {
            window.location.replace('/login?site=weibo')
        });
        focus_mode("#id-login-by-wei", 1, 0.5);

        var twitter_login = $("#id-login-by-twi");
        twitter_login.on("click", function () {
            window.location.replace('/login?site=twitter')
        });
        focus_mode("#id-login-by-twi", 1, 0.5)
    }


});


function append_messages_list(statuses, status_template) {
    $.each(statuses, function (index, item) {
        var msg_item = status_template.clone();
        var max_width = status_template.width() * 0.80;
        var max_height = status_template.width() * 0.80;

        set_general_attrs(msg_item, item, max_width, max_height);
        set_type_specific_attrs(msg_item, item, max_width);
        set_imgs_style(msg_item, item, max_width, max_height);
        msg_item.appendTo($('#id-message-list'))
    });
    register_gallery();
}

function set_general_attrs(msg_item, item, max_width, max_height) {
    msg_item.css("display", "block");
    msg_item.find('.cls-user-thumbnail').find('img').attr('src', item.profile);
    msg_item.find('.cls-user-thumbnail').find('img').css("max-width", max_width * 0.1, "max-height", max_height * 0.1);
    msg_item.find('.cls-user-name').text(item.writer);
    msg_item.find('.cls-message-time').text(moment(item.time).fromNow());
    msg_item.find('.cls-message-text').text(item.text);
    msg_item.find('.cls-message-text').css("width", max_width);
}

function set_type_specific_attrs(msg_item, item, max_width) {
    msg_item.attr('id', 'id-' + item.type + '-' + item.id);
    msg_item.attr('class', 'container cls-message-items from-' + item.type);
    if (item.type != 'weibo') {
        msg_item.find('.cls-like-msg').addClass('is-liked-' + item.liked);
    }
    else {
        msg_item.find('.cls-like-msg').remove();
    }
}

function set_imgs_style(msg_item, item, max_width, max_height) {
    var imgs = msg_item.find('.cls-message-img');
    if (imgs) {
        imgs.remove()
    }
    var new_imgs = $('<div/>', {
        class: 'cls-message-img'
    });

    var cls = '';
    var style = '';
    imgs = item.imgs;
    if (imgs.length == 1) {
        $.each(item.imgs, function (index, img) {
            cls = "cls-img-wrapper img_1_0";
            $('<div/>',
                {
                    class: cls,
                    style: "width:" + max_width + "px;max-height:" + max_height * 0.60 + "px;"
                }).append($('<img/>', {
                src: img.middl,
                class: "cls-img-middl",
                href: img.middl
            })).appendTo(new_imgs)
        });
    }
    else if (imgs.length == 2) {
        $.each(item.imgs, function (index, img) {
            if (index == 0) {
                cls = "cls-img-wrapper img_1_1-l";
            }
            else {
                cls = "cls-img-wrapper img_1_1-r";
            }
            $('<div/>',
                {
                    class: cls,
                    style: "width:" + max_width * 0.48 + "px;height:" + max_height * 0.48 + "px;"
                }
            ).append($('<img/>', {
                src: img.middl,
                class: "cls-img-middl",
                href: img.middl
            })).appendTo(new_imgs)
        });
    }
    else if (imgs.length == 3) {
        $.each(item.imgs, function (index, img) {
            if (index == 0) {
                cls = "cls-img-wrapper img_1_2_l";
                style = "width:" + max_width * 0.64 + "px;height:" + max_height * 0.64 + "px;"
            }
            else {
                cls = "cls-img-wrapper img_1_2_r";
                style = "width:" + max_width * 0.32 + "px;height:" + max_height * 0.32 + "px;"
            }
            $('<div/>',
                {
                    class: cls,
                    style: style
                }
            ).append($('<img/>', {
                src: img.middl,
                class: "cls-img-middl",
                href: img.middl
            })).appendTo(new_imgs)
        });
    }
    else if (imgs.length > 3) {
        $.each(item.imgs, function (index, img) {
            if (index == 0) {
                cls = "cls-img-wrapper img_1_2_l";
                style = "width:" + max_width * 0.72 + "px;height:" + max_height * 0.72 + "px;";
                $('<div/>',
                    {
                        class: cls,
                        style: style
                    }
                ).append($('<img/>', {
                    src: img.middl,
                    class: "cls-img-middl",
                    href: img.middl
                })).appendTo(new_imgs)
            }
            else if (index <= 3) {
                cls = "cls-img-wrapper img_1_2_r";
                style = "width:" + max_width * 0.24 + "px;height:" + max_height * 0.24 + "px;";
                $('<div/>',
                    {
                        class: cls,
                        style: style
                    }
                ).append($('<img/>', {
                    src: img.middl,
                    class: "cls-img-middl",
                    href: img.middl
                })).appendTo(new_imgs)
            }
            else {
                $('<div/>',
                    {
                        style: "display:none"
                    }
                ).append($('<img/>', {
                    src: img.middl,
                    class: "cls-img-middl",
                    href: img.middl
                })).appendTo(new_imgs)
            }

        });
    }

    new_imgs.appendTo(msg_item.find('.cls-message-content'));
}

function request_statuses(url) {
    $.get($SCRIPT_ROOT + url, {}, function (data) {
        data = $.parseJSON(data);
        if (data.status == 200) {
            var statuses = data.content;
            var last_status = $('.cls-message-items').eq(-1);
            append_messages_list(statuses, last_status);
        }
        else {
            alert(data.msg)
        }
    });
}

function load_home(url) {
    request_statuses(url)
}

function resize_imgs() {
    var max_width, max_height = $(".cls-message-items").eq(0).width() * 0.8;

    var img_1_0 = $(".img_1_0");
    var img_1_1 = $(".img_1_1");
    var img_1_2_l = $(".img_1_2_l");
    var img_1_2_r = $(".img_1_2_r");
    var img_1_3_l = $(".img_1_3_l");
    var img_1_3_r = $(".img_1_3_r");

    $.each(img_1_0, function (index, item) {
        $(this).css("width", max_width, "max-height", max_height * 0.6)
    });
    $.each(img_1_1, function (index, item) {
        var side_length = max_width * 0.48;
        $(this).css("width", side_length, "height", side_length);
    });

    $.each(img_1_2_l, function (index, item) {
        var side_length = max_width * 0.64;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_2_r, function (index, item) {
        var side_length = max_width * 0.32;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_3_l, function (index, item) {
        var side_length = max_width * 0.72;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_3_r, function (index, item) {
        var side_length = max_width * 0.24;
        $(this).css("width", side_length, "height", side_length);
    });
}

function focus_mode(selector, on, out, dynamic) {
    if (!dynamic) {
        $(selector).on("mouseover", function () {
            $(this).css("opacity", on)
        });
        $(selector).on("mouseout", function () {
            $(this).css("opacity", out)
        });
    }
    else {
        body = $("body");
        body.on("mouseover", selector, function () {
            $(this).css("opacity", on)
        });
        body.on("mouseout", selector, function () {
            $(this).css("opacity", out)
        });
    }
}

function register_gallery() {
    $(".cls-message-img").each(function () {
        $(this).magnificPopup({
            delegate: '.cls-img-middl',
            type: 'image',
            gallery: {
                enabled: true,

                preload: [0, 2],

                navigateByImgClick: true,

                arrowMarkup: '<button title="%title%" type="button" class="mfp-arrow mfp-arrow-%dir%"></button>',

                tPrev: 'Previous',
                tNext: 'Next',
                tCounter: '<span class="mfp-counter">%curr% of %total%</span>'
            },
            mainClass: 'mfp-with-zoom',
            zoom: {
                enabled: true,

                duration: 300,
                easing: 'ease-in-out',
                opener: function (openerElement) {
                    return openerElement.is('img') ? openerElement : openerElement.find('img');
                }
            },
            callbacks: {
                elementParse: function (item) {
                    if (item.el.height() > $(window).height() * 1.5) {
                        item.el.css("max-height", item.el.height() + '! important;');
                    }
                    else {
                        item.el.css("max-height", $(window).height() + '! important;');
                    }

                    item.src = item.src.replace(/\/bmiddle\//, '/large/');
                }
            }
        })
    });
}

function like_or_unlike_msg(msg) {
    var identity = msg.attr('id').split('-');
    var type = identity[1];
    var id = identity[2];
    var cls = msg.find('.cls-like-msg').attr('class');
    var liked = cls.split('-').pop();
    var data = {
        type: type,
        id: id,
        liked: liked,
        _xsrf: get_xsrf()
    };

    if (liked == 'false') {
        temporally_like_action(msg, 'like');
        $.post($SCRIPT_ROOT + type + '/like_msg', data, function (data) {
            data = parseJSON(data);
            if (data.status != 200) {
                roll_back_like_action(msg, 'like')
            }
        })
    }
    else {
        temporally_like_action(msg, 'unlike');
        $.post($SCRIPT_ROOT + type + '/unlike_msg', data, function (data) {
            data = parseJSON(data);
            if (data.status != 200) {
                roll_back_like_action(msg, 'unlike')
            }
        })
    }
}

function temporally_like_action(msg, action) {
    var cls = msg.find('.cls-like-msg').attr('class');
    var new_cls = '';
    if (action == 'like') {
        new_cls = cls.replace('liked-false', 'liked-true')
    }
    else {
        new_cls = cls.replace('liked-true', 'liked-false')
    }
    msg.find('.cls-like-msg').attr('class', new_cls, 'style', 'color: #d9534f;');

}

function roll_back_like_action(msg, prev_action) {
    var cls = msg.find('.cls-like-msg').attr('class');
    var new_cls = '';
    if (prev_action == 'like') {
        new_cls = cls.replace('liked-true', 'liked-false')
    }
    else {
        new_cls = cls.replace('liked-false', 'liked-true')
    }
    msg.find('.cls-like-msg').attr('class', new_cls);
}

function get_xsrf() {
    return $("#xsrf").find("input").prop('value');
}