var run_limit = function () {
    var count = 10;
            var countdown = setInterval(CountDown, 1000);
            function CountDown() {
                var x = $("#btn_run");
                x.attr("disabled", true);
                x.text("请等待" + count + "秒");
                if (count === 0) {
                    $("#btn_run").text("RunOnce").removeAttr("disabled");
                    clearInterval(countdown);
                }
                count--;
            }
};

var create_limit = function () {
    var count = 10;
            var countdown = setInterval(CountDown, 1000);
            function CountDown() {
                var y = $("#btn")
                y.attr("disabled", true);
                y.text("请等待" + count + "秒");
                if (count === 0) {
                    $("#btn").text("Create").removeAttr("disabled");
                    clearInterval(countdown);
                }
                count--;
            }
};

var main = function () {
    run_limit();
    create_limit();
};

main();
