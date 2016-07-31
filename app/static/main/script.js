$(document).ready(function () {
    if (window.location.pathname == '/') {
        load_home('load_home');

        var load_more = $("#id-load-more");
        load_more.on('click', function () {
            request_statuses('load_more')
        });

        focus_mode(".cls-img-wrapper img", 0.7, 1, true);

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


// 根据 json 来添加时间线消息
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

// 设置消息的通用属性
function set_general_attrs(msg_item, item, max_width, max_height) {
    msg_item.css("display", "block");
    msg_item.find('.cls-user-thumbnail').find('img').attr('src', item.profile);
    msg_item.find('.cls-user-thumbnail').find('img').css("max-width", max_width * 0.1, "max-height", max_height * 0.1);
    msg_item.find('.cls-user-name').text(item.writer);
    msg_item.find('.cls-message-time').text(moment(item.time).fromNow());
    msg_item.find('.cls-message-text').text(item.text);
    msg_item.find('.cls-message-text').css("width", max_width);
}

// 设置消息的独特属性， 根据消息的来源和id而变化
function set_type_specific_attrs(msg_item, item, max_width) {
    msg_item.attr('id', 'id-' + item.type + '-' + item.id);
    msg_item.attr('class', 'container cls-message-items from-' + item.type);

    msg_item.find('.cls-like-msg').addClass('is-liked-' + item.liked);

    var reply_div_id = "id-reply-" + item.type + "-" + item.id;
    msg_item.find('.cls-message-reply').attr('id', reply_div_id).css('max-width', max_width);
    msg_item.find('.cls-reply-msg').attr('data-target', '#' + reply_div_id);

    var retw_div_id = "id-retw-" + item.type + "-" + item.id;
    msg_item.find('.cls-message-retw').attr('id', retw_div_id);
    msg_item.find('.cls-retw-msg').attr('data-target', '#' + retw_div_id)
}

// 设置消息的图片风格, 根据图片的数量而变化
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
            style = "width:" + max_width + "px;max-height:" + max_height * 0.60 + "px;";
            create_new_img(cls, style, img, new_imgs, true)
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
            style = "width:" + max_width * 0.48 + "px;height:" + max_height * 0.48 + "px;";
            create_new_img(cls, style, img, new_imgs)
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
            create_new_img(cls, style, img, new_imgs)
        });
    }
    else if (imgs.length > 3) {
        $.each(item.imgs, function (index, img) {
            if (index == 0) {
                cls = "cls-img-wrapper img_1_3_l";
                style = "width:" + max_width * 0.72 + "px;height:" + max_height * 0.72 + "px;";
                create_new_img(cls, style, img, new_imgs)
            }
            else if (index <= 3) {
                cls = "cls-img-wrapper img_1_3_r";
                style = "width:" + max_width * 0.24 + "px;height:" + max_height * 0.24 + "px;";
                create_new_img(cls, style, img, new_imgs)
            }
            else {
                cls = "cls-img-wrapper img_1_3_h";
                style = "display:none";
                create_new_img(cls, style, img, new_imgs)
            }
        });
    }
    new_imgs.appendTo(msg_item.find('.cls-message-content'));
}

// 创建新的图片元素， 插入到每个消息的图片容器中
//    该函数被 set_img_style 调用
function create_new_img(cls, style, img_object, imgs_container, is_single_img) {
    var new_img_wrapper = $('<div/>', {
        class: cls,
        style: style
    });
    var new_img = $('<img/>', {
        class: "cls-img-middl",
        href: img_object.middl,
        src: img_object.middl
    }).one("load", function () { //以下部分是根据图片的长和宽自适应 img_wrapper
        var width = $(this).width();
        var height = $(this).height();
        if (is_single_img == true) {
            $(this).css("width", "100%")
        }
        else if (width >= height > 0) {
            $(this).css("height", "100%")
        }
        else if (0 < width < height) {
            $(this).css("width", "100%")
        }
    }).each(function () {
        if (this.complete) {
            var width = $(this).naturalWidth;
            var height = $(this).naturalHeight;
            if (is_single_img == true) {
                $(this).css("width", "100%")
            }
            else if (width >= height > 0) {
                alert('w>h');
                $(this).css("width", "auto");
                $(this).css("height", "100%")
            }
            else if (0 < width < height) {
                alert('w<h');
                $(this).css("height", "auto");
                $(this).css("width", "100%")
            }
        }
    });
    new_img.appendTo(new_img_wrapper);
    new_img_wrapper.appendTo(imgs_container)
}

// 向特定 url 通过 ajax 请求时间线消息的 json 数据
function request_statuses(url) {
    $.get($SCRIPT_ROOT + url, {}, function (data) {
        data = $.parseJSON(data);
        if (data.status == 200) {
            var statuses = data.content;
            var last_status = $('.cls-message-items').eq(0);
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
        var body = $("body");
        body.on("mouseover", selector, function () {
            $(this).css("opacity", on)
        });
        body.on("mouseout", selector, function () {
            $(this).css("opacity", out)
        });
    }
}

function register_gallery() {
    function changeImgSize() {
        var img = this.content.find('img');
        var height = img[0].naturalHeight;
        var width = img[0].naturalWidth;
        if (height > width * 2) {
            img.css('max-height', '100%');
            img.css('width', 'auto');
            img.css('max-width', 'auto');
        }
    }

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
                    item.src = item.src.replace(/\/bmiddle\//, '/large/');
                },
                imageLoadComplete: changeImgSize
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
            data = $.parseJSON(data);
            if (data.status != 200) {
                roll_back_like_action(msg, 'like')
            }
        })
    }
    else {
        temporally_like_action(msg, 'unlike');
        $.post($SCRIPT_ROOT + type + '/unlike_msg', data, function (data) {
            data = $.parseJSON(data);
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