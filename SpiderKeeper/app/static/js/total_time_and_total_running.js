var button = $('button.btn-primary')[0];
var input_form = $('input.form-control');
var time = input_form[1];
var boxes = $('table.table-striped');
var next_boxes = boxes[0];
var running_boxes = boxes[1];
var next_jobs_table = $(next_boxes).find('tr');
var running_jobs_table = $(running_boxes).find('tr');

var total_time = function(jobs_table) {
    var total = 0;
    if (jobs_table.length > 1) {
        for(var j=1; j<jobs_table.length; j++) {
            var url_time = parseInt($(jobs_table[j]).find('td')[5].innerText);
            total += url_time;
        }
    }
    return total;
};


var all_total_time = function () {
    var input_value = parseInt(time.value);
    var pending_time = total_time(next_jobs_table);
    var running_time = total_time(running_jobs_table);
    var total_before = pending_time + running_time;
    var total = input_value + pending_time + running_time;
    return [total, total_before];
};

var main = function () {
    $(button).click(function () {
        var time_limit = 100000;
        var job_limit = 4;
        var pending = next_jobs_table.length - 1;
        var running = running_jobs_table.length - 1;
        var pending_and_running = pending + running;
        var total = all_total_time()[0];
        var total_before = all_total_time()[1];
        if (pending_and_running >= job_limit) {
            alert('最多同时只能跑' + job_limit + '个任务')
        }
        if (total > time_limit) {
            var last_time = time_limit - total_before;
            alert('总次数不能超过10万, 还能添加的次数为: ' + last_time)
        }
});
};

main();
