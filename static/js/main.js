$(document).ready(function () {
    $("#table-display").DataTable();
    $("#btn-select-table").on("click", function(){
        let table_name = $("#table-name-to-select").val();
        $.get("/table/" + table_name, function(data){
            console.log(data);
        })
    })
    //render_table(["h1", "h2"], [["r1", "r2"], ["s1", "s2"]]);
});

function render_table(heads_list, rows_list) {
    let thead = get_table_head(heads_list);
    let tbody = get_table_body(rows_list);
    $("#table-head").empty().append(thead);
    $("#table-body").empty().append(tbody);
    $("#table-foot").empty().append(tbody);
    $("#table-display").DataTable();
}

function get_table_head(heads_list) {
    let thead = "<tr>";
    for (let i = 0; i < heads_list.length; i++) {
        thead += "<th>" + heads_list[i] + "</th>";
    }
    thead += "</tr>";
    return thead;
}

function get_table_body(rows_list) {
    let tbody = "";
    for (let i=0; i < rows_list.length; i++) {
        tbody += "<tr>";
        let row = rows_list[i];
        for (let j = 0; j < row.length; j++) {
            tbody += "<th>" + row[j] + "</th>";
        }
        tbody += "</tr>";
    }
    return tbody;
}