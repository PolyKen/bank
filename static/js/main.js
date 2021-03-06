$(document).ready(function () {
    reloadDataTable();
    bind_event();
    //render_table(["h1", "h2"], [["r1", "r2"], ["s1", "s2"]]);
});

let currency_type_dict = {"RMB": 1, "USD": 2, "EUR": 3, "JPY": 4, "GBP": 5, "HKD": 6};
let deposit_type_dict = {"活期": 1, "定期三个月": 2, "定期六个月": 3, "定期一年": 4, "定期两年": 5, "定期三年": 6, "定期五年": 7};
let empty_table = "<table id=\"table-display\" class=\"display\" style=\"width:100%\"><thead id=\"table-head\"></thead><tbody id=\"table-body\"></tbody><tfoot id=\"table-foot\"></tfoot></table>";

function reloadDataTable() {
    $("#table-display").DataTable();
}

function bind_event() {
    $("#tab-1").on("click", function () {
        $("#tab-1 a").tab('show');
        $("#tab-1").addClass('active');
        $("#tab-2").removeClass('active');
    });

    $("#tab-2").on("click", function () {
        $("#tab-2 a").tab('show');
        $("#tab-2").addClass('active');
        $("#tab-1").removeClass('active');
    });

    $("#btn-select-table").on("click", function () {
        let table_name = $("#table-name-to-select").val();
        $.get("/table/" + table_name, function (data) {
            if (data === "table not found") {
                alert("table not found");
                return;
            }
            let table = parse_table(data);
            let heads_list = table["heads_list"];
            let rows_list = table["rows_list"];
            render_table(heads_list, rows_list);
        })
    });

    $("ul.dropdown-menu a").on("click", function () {
        $(this).parents(".dropdown").children("button").text($(this).text() + " ");
        $(this).parents(".dropdown").children("button").append("<span class=\"caret\"></span>");
        $(this).parents(".dropdown").children(".hidden-value").text($(this).text());
    });

    $("#btn-deposit").on("click", function () {
        let user_id = $("#deposit_user_id").val();
        let account_id = $("#deposit_account_id").val();
        let quantity = $("#deposit_quantity").val();
        let currency_type = $("#deposit_currency_type").text();
        currency_type = currency_type_dict[currency_type];
        let deposit_type = $("#deposit_deposit_type").text();
        deposit_type = deposit_type_dict[deposit_type];
        let payload = {
            "user_id": user_id,
            "account_id": account_id,
            "quantity": quantity,
            "currency_type": currency_type,
            "deposit_type": deposit_type
        };
        $.get("/deposit", payload, function (data) {
            console.log("deposit");
            console.log(data);
            alert(data);
            $("#opt-deposit input").val("");
            $("#dropdown-currency_type").text("币种").append("<span class=\"caret\"></span>");
            $("#dropdown-deposit_type").text("存款类型").append("<span class=\"caret\"></span>");
        })
    });

    $("#btn-withdraw").on("click", function () {
        let user_id = $("#withdraw_user_id").val();
        let account_id = $("#withdraw_account_id").val();
        let quantity = $("#withdraw_quantity").val();
        let deposit_id = $("#withdraw_deposit_id").val();
        let payload = {
            "user_id": user_id,
            "account_id": account_id,
            "deposit_id": deposit_id,
            "quantity": quantity
        };
        $.get("/withdraw", payload, function (data) {
            console.log("withdraw");
            console.log(data);
            alert(data);
            $("#opt-withdraw input").val("");
        })
    });
}

function render_table(heads_list, rows_list) {
    $("#table-container").empty().append(empty_table);
    let thead = get_table_head(heads_list);
    let tbody = get_table_body(rows_list);
    $("#table-head").empty().append(thead);
    $("#table-body").empty().append(tbody);
    $("#table-foot").empty().append(thead);
    reloadDataTable();
    $("#table-name").text($("#table-name-to-select").val());
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
    for (let i = 0; i < rows_list.length; i++) {
        tbody += "<tr>";
        let row = rows_list[i];
        for (let j = 0; j < row.length; j++) {
            tbody += "<th>" + row[j] + "</th>";
        }
        tbody += "</tr>";
    }
    return tbody;
}

function parse_table(raw_data) {
    let json = JSON.parse(raw_data);
    let heads_list = json.heads_list;
    let rows_list = [];
    json = json.rows_list;
    for (let i = 0; i < json.length; i++) {
        let row = [];
        for (let j = 0; j < heads_list.length; j++) {
            row.push(json[i][heads_list[j]]);
        }
        rows_list.push(row);
    }
    return {"heads_list": heads_list, "rows_list": rows_list};
}