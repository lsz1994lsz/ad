var input_form = $('input.form-control');
var url = input_form[0];
var time = input_form[1];
var button = $('button.btn-primary')[0];
var url_of_caifu = ['http://caifuhao.eastmoney.com', 'https://caifuhao.eastmoney.com',
                    'http://emcreative.eastmoney.com', 'https://emcreative.eastmoney.com'];
var url_of_sohu = ['http://www.sohu.com', 'https://www.sohu.com', 'http://m.sohu.com', 'https://m.sohu.com'];
var url_of_gelonghui = ['http://www.gelonghui.com', 'https://www.gelonghui.com',
                        'http://gelonghui.com', 'https://gelonghui.com',
                        'http://m.gelonghui.com', 'https://m.gelonghui.com'];
var url_of_zhongjin = ['http://mp.cnfol.com', 'https://mp.cnfol.com'];
var url_prefix = url_of_caifu.concat(url_of_sohu, url_of_gelonghui, url_of_zhongjin);

var judge_prefix = function (url, url_list) {
    var total = 0;
    for (var i=0; i<url_list.length; i++) {
        if (url.substr(0, url_list[i].length) === url_list[i]) {
            total += 1;
            break;
        }
    }
    if (total === 0) {
        alert('url错误: 必须为--->格隆汇, 中金, 东财, 搜狐');
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
    // else  {
    //     if (! (y.substr(0, 7) === 'http://' || y.substr(0, 8) === 'https://')) {
    //         alert('url格式错误: 必须以http://或者https://开头')
    //     }
    // }
};

var main = function () {
    $(button).click(function () {

        time_limit(time.value.trim());
        url_limit(url.value.trim(), url_prefix);

});
};

main();
