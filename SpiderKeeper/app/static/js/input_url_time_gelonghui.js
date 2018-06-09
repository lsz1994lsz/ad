var input_form = $('input.form-control');
var url = input_form[0];
var time = input_form[1];
var button = $('button.btn-primary')[0];

var url_prefix = ['http://www.gelonghui.com', 'https://www.gelonghui.com',
                    'http://gelonghui.com', 'https://gelonghui.com'];

var judge_prefix = function (url, url_list) {
    var total = 0;
    for (var i=0; i<url_list.length; i++) {
        if (url.substr(0, url_list[i].length) === url_list[i]) {
            total += 1;
            break;
        }
    }
    if (total === 0) {
        alert('url错误: 必须为格隆汇官网');
    }
};
var time_limit = function (x) {
    if (isNaN(x)) {
        alert('time格式错误: 必须全为数字')
    }
    else {
        if (parseInt(x) <= 0) {
            alert('time数值错误: 不能为负数或零')
        }
        else if ('' === x) {
            alert('time格式错误: 不能为空')
        }
        else if (x.indexOf('.') > -1) {
            alert('time格式错误: 不能有小数点')
        }
        else if (x[0] === '0') {
            alert('time格式错误: 开头不能为零')
        }
    }
};

var url_limit = function (url, url_list) {
    if (url === '') {
        alert('url格式错误: 不能为空')
    }
    else if (url.indexOf(' ') > -1) {
        alert('url格式错误: 中间不能有空格')
    }
    // judge_prefix(url, url_list);
};

var main = function () {
    $(button).click(function () {
        time_limit(time.value.trim());
        url_limit(url.value.trim(), url_prefix);

});
};

main();
