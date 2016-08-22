$(document).ready(function () {
    if (window.location.pathname == '/') {
        request_statuses('load_home');

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

        msg_list.on('click', '.cls-retw-msg', function () {
            var msg_box = $(this).parent().parent();
            var box_height = msg_box.height();
            var window_height = $(window).height();
            var margin_top = (window_height - box_height) / 3;
            var retw_box = msg_box.find('.cls-message-retw');
            retw_box.css('margin-top', margin_top)
        });

        msg_list.on('click', '.cls-retw-modal-confirm', function () {
            var id = $(this).closest('.cls-message-retw').prop('id').split('-')[3];
            var site = $(this).closest('.cls-message-retw').prop('id').split('-')[2];
            var input_box = $(this).parent().siblings('.modal-body').children('input');
            var reply_text = input_box.prop('value');
            var screen_name = $(this).parents('.cls-message-right').find('.cls-user-screen-name').eq(0).text();
            var is_original = $(this).parents('.cls-message-items').attr('class').split('is-original-')[1];
            var orig_text = $(this).parents('.cls-message-right').find('.cls-message-text').eq(0).text();
            if (site == 'weibo') {
                if (is_original == 'true' && !reply_text) {
                    reply_text = '转发微博';
                }
                else if (is_original == 'false') {
                    reply_text = reply_text + ' //@' + screen_name + ':' + orig_text;
                }
                site = 'weibo/retw_msg';
            }
            else {
                site = 'twitter/retw_msg'
            }

            $.post($SCRIPT_ROOT + site,
                {
                    id: id,
                    reply: reply_text,
                    screen_name: screen_name,
                    _xsrf: get_xsrf()
                }, function (data) {
                    data = $.parseJSON(data);
                    if (data.status == 200) {
                        window.location.replace('/')
                    }
                    else {
                        alert(data.msg)
                    }

                });
            input_box.prop('value', '');
            $(this).siblings('.cls-retw-modal-cancel').trigger('click')
        });

        msg_list.on('click', '.cls-reply-btn', function () {
            var id = $(this).closest('.cls-message-reply').prop('id').split('-')[3];
            var site = $(this).closest('.cls-message-reply').prop('id').split('-')[2];
            var input_box = $(this).closest('.cls-message-right').find('.cls-reply-text');
            var reply_text = input_box.prop('value');
            var reply_btn = $(this).closest('.cls-message-right').find('.cls-reply-msg');
            if (reply_text && reply_text.trim()) {

                if (site == 'weibo') {
                    site = 'weibo/reply_msg'
                }
                else {
                    site = 'twitter/reply_msg'
                }

                $.post($SCRIPT_ROOT + site,
                    {
                        id: id,
                        reply: reply_text.trim(),
                        screen_name: $(this).parents('.cls-message-right').find('.cls-user-screen-name').text(),
                        _xsrf: get_xsrf()
                    }, function (data) {
                        data = $.parseJSON(data);
                        if (data.status == 200) {
                        }
                        else {
                            alert(data.msg)
                        }

                    });
            }
            reply_btn.trigger('click');
            input_box.prop('value', '');
        })
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
        function gen_ret_item(template, source) {
            var ret_item = template.clone();
            ret_item.find('.cls-message-action').remove();
            ret_item.find('.cls-message-retw').remove();
            ret_item.find('.cls-message-reply').remove();

            var max_width = template.width() * 0.70;
            var max_height = template.width() * 0.70;
            set_general_attrs(ret_item, source, max_width, max_height);
            set_type_specific_attrs(ret_item, source, max_width);
            set_imgs_style(ret_item, source, max_width * 0.95, max_height * 0.95);
            ret_item.find('.cls-message-left').remove();
            ret_item.find('.cls-message-right').attr('class', 'col-md-12 col-sm-12 col-xs-12 cls-message-right');
            ret_item.find('.cls-message-target').css('width', max_width + 'px');

            return ret_item
        }

        function gen_msg_item(template, source) {
            var msg_item = template.clone();
            var max_width = template.width() * 0.80;
            var max_height = template.width() * 0.80;

            set_general_attrs(msg_item, source, max_width, max_height);
            set_type_specific_attrs(msg_item, source, max_width);
            set_imgs_style(msg_item, source, max_width, max_height);

            var retwed = item.retwed_msg;
            if (retwed) {
                msg_item.find('.cls-message-target').css('width', max_width - 10 + 'px');
                var retwed_msg = msg_item.find('.cls-message-target');
                var ret_item = gen_ret_item(template, retwed);
                retwed_msg.append(ret_item)

            }
            return msg_item

        }

        var msg_item = gen_msg_item(status_template, item);

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
    msg_item.find('.cls-user-screen-name').text(item.screen_name);
    msg_item.find('.cls-message-time').text(moment(item.time).fromNow());
    msg_item.find('.cls-message-text').text(item.text);
    msg_item.find('.cls-message-text').css("width", max_width);
}

// 设置消息的独特属性， 根据消息的来源和id而变化
function set_type_specific_attrs(msg_item, item, max_width) {
    msg_item.attr('id', 'id-' + item.type + '-' + item.id);
    msg_item.attr('class', 'container cls-message-items from-' + item.type + ' is-original-' + item.is_original);

    var like_action_icon = msg_item.find('.cls-like-msg');
    like_action_icon.addClass('is-liked-' + item.liked);
    if (item.type == 'weibo') {
        like_action_icon.attr('title', '微博无法点赞');
    }
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
                $(this).css("width", "auto");
                $(this).css("height", "100%")
            }
            else if (0 < width < height) {
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
    $('#id-load-more-text').text('正在加载...');
    $('#id-load-more').attr('style', 'background-color: rgb(245, 245, 245)');
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
        $('#id-load-more-text').text('加载更多');
        $('#id-load-more').attr('style', 'background-color: rgb(255, 255, 255)');
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

    if (type == 'weibo') {
        alert('微博无法点赞');
        return
    }

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