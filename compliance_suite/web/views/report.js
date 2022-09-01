function load() {
    $.getJSON("web_report.json", function (data) {

        // JSON Tab

        var json_container = $('#json_div');
        json_container
            .jsonPresenter('destroy')
            .jsonPresenter({
                    json: data, // JSON objects here
                });

        var data_str = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
        $('<a href="data:' + data_str + '" download="TES Compliance Report.json"><button style="margin:10px; width:100%" class="downbtn"><i class="fa fa-download"></i> Download Report</button></a>').prependTo('#json_div');

    });

}
