$(document).ready(function () {
    if (window.location.pathname == '/') {
        load_home('load_home');
        var load_more = $("#id-load-more");
        load_more.on('click', function () {
            request_statuses('load_more')
        });
        focuse_mode(".cls-img-wrapper img", 0.7, 1, true);

        $('.image-link').magnificPopup({type: 'image'});
    }

    if (window.location.pathname == '/login') {
        var weibo_login = $("#id-login-by-wei");
        weibo_login.on("click", function () {
            window.location.replace('/login?site=weibo')
        });
        focuse_mode("#id-login-by-wei", 1, 0.5);

        var twitter_login = $("#id-login-by-twi");
        twitter_login.on("click", function () {
            window.location.replace('/login?site=twitter')
        });
        focuse_mode("#id-login-by-twi", 1, 0.5)
    }

    $(window).on("resize", function () {
        resize_imgs();
    });

});


function appendStatusesList(statuses, status_template) {
    $.each(statuses, function (index, item) {
        var msg_item = status_template.clone();
        msg_item.css("display", "block");
        if (item.type == 'wei') {
            msg_item.attr('class', 'container cls-message-items from-wei')
        }
        else if (item.type == 'twi') {
            msg_item.attr('class', 'container cls-message-items from-twi')
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
        var max_width = $("#id-top-nav").width() * 0.85;
        var max_height = $("#id-top-nav").width() * 0.85;
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
                        style: "width:" + max_width * 0.49 + "px;height:" + max_height * 0.49 + "px;"
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
                    style = "width:" + max_width * 0.62 + "px;height:" + max_height * 0.62 + "px;"
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
                    style = "width:" + max_width * 0.74 + "px;height:" + max_height * 0.75 + "px;";
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
                    style = "width:" + max_width * 0.24 + "px;height:" + max_height * 0.25 + "px;";
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
        msg_item.appendTo($('#id-message-list'))
    });
    register_gallery();
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
    });
}

function load_home(url) {
    request_statuses(url)
}

function resize_imgs() {
    var max_width = $("#id-top-nav").width() * 0.8;

    var img_1_0 = $(".img_1_0");
    var img_1_1 = $(".img_1_1");
    var img_1_2_l = $(".img_1_2_l");
    var img_1_2_r = $(".img_1_2_r");
    var img_1_3_l = $(".img_1_3_l");
    var img_1_3_r = $(".img_1_3_r");

    $.each(img_1_0, function (index, item) {
        $(this).css("width", max_width, "max-height", max_width)
    });
    $.each(img_1_1, function (index, item) {
        var side_length = max_width * 0.5;
        $(this).css("width", side_length, "height", side_length);
    });

    $.each(img_1_2_l, function (index, item) {
        var side_length = max_width * 0.66;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_2_r, function (index, item) {
        var side_length = max_width * 0.33;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_3_l, function (index, item) {
        var side_length = max_width * 0.75;
        $(this).css("width", side_length, "height", side_length);
    });
    $.each(img_1_3_r, function (index, item) {
        var side_length = max_width * 0.25;
        $(this).css("width", side_length, "height", side_length);
    });
}

function focuse_mode(selector, on, out, dynamic) {
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
