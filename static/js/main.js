$(document).ready(function () {
    $("#btn-select-table").on("click", function(){
        let table_name = $("#table-name-to-select").val();
        $.get("/table/" + table_name, function(data){
            if (data === "table not found") {
                alert("table not found");
                return;
            }
            let table = parse_table(data);
            let heads_list = table["heads_list"];
            let rows_list = table["rows_list"];
            render_table(heads_list, rows_list);
        })
    })
    //render_table(["h1", "h2"], [["r1", "r2"], ["s1", "s2"]]);
});

function render_table(heads_list, rows_list) {
    let thead = get_table_head(heads_list);
    let tbody = get_table_body(rows_list);
    $("#table-head").empty().append(thead);
    $("#table-body").empty().append(tbody);
    $("#table-foot").empty().append(thead);
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

function parse_table(raw_data){
    let json = JSON.parse(raw_data);
    let heads_list = [];
    let rows_list = [];
    for (let key in json[0]){
        heads_list.push(key);
    }
    for (let i=0;i<json.length;i++){
        let row = [];
        for (let j=0; j<heads_list.length;j++){
            row.push(json[i][heads_list[j]]);
        }
        rows_list.push(row);
    }
    return {"heads_list":heads_list, "rows_list":rows_list};
}