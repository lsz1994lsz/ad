var create_project = function () {
  $('.create-project').on('click', function () {
    var server = $(this).parent().parent('.dropdown-menu').data("server");
    $('#server').val(server);
    var index_of_servers = $(this).parent().parent('.dropdown-menu').data("index_of_servers");
    $('#index_of_servers').val(index_of_servers);
  });
};

var main = function () {
    create_project()
};

main();