$(document).ready(function () {
    add_log("start");
    update_canvas();
    $("#read-wish").on("click", function () {
        process();
        setTimeout(read_wish, 200);
    });

    $("#confirm").on("click", confirm_wish);

    $("#user-1").prop("checked", true);
    user_id = "Tom";

    $("#buy").on("click", function () {
        $("#sell").prop("checked", false);
    });

    $("#sell").on("click", function () {
        $("#buy").prop("checked", false);
    });

    $("#user-1").on("click", function () {
        $("#user-2").prop("checked", false);
        user_id = "Tom";
    });

    $("#user-2").on("click", function () {
        $("#user-1").prop("checked", false);
        user_id = "Jerry";
    });
});

var user_id = "admin";

const INF = 999999999;
var start_price = INF;
var start_pos = 0;
var end_price = 0;
var end_pos = 0;

var buy_table = [];
var sell_table = [];
var log_wish_id = [];
var log_transaction_id = [];
var log_start_date = (new Date()).valueOf();

function confirm_wish() {
    let mode = $("#buy").prop("checked");
    mode = mode ? "0" : "1";
    let price = $("#price").val();
    let num = $("#num").val();
    let url = "/add-wish" + "/" + user_id + "/" + mode + "/" + num + "/" + price;
    $.get(url, function () {
        console.log("add wish");
        process();
        setTimeout(read_wish, 200);
        setTimeout(show_history, 200);
    })

}

function format_dt_text(dt_array){
    let year = dt_array[0].toString();
    let month = dt_array[1].toString();
    let day = dt_array[2].toString();
    let hour = dt_array[3].toString();
    let minute = dt_array[4].toString();
    let second = dt_array[5].toString();
    let text = year + "." + month + "." + day + " " + hour + ":" + minute + ":" + second;
    return text;
}

function show_history() {
    $.get("/history/wish", function (data) {
        console.log("latest wish:", data);
        let obj = parse_wish_obj(data);
        let mode = obj.mode == 0 ? "buy" : "sell";
        let color = obj.mode == 0 ? "red" : "green";
        let text = obj.user + " want to " +
            mode + " " + obj.quantity.toString() +
            " hand(s) with price " + obj.price.toString() +
            ", time: " + format_dt_text(obj.datetime);
        if (log_wish_id.indexOf(obj.id) == -1) {
            add_log(text, color);
            log_wish_id.push(obj.id);
        }
    })
    $.get("/history/transaction", function (data) {
        console.log("latest transaction:", data);
        let obj = parse_transaction_obj(data);
        let buy_user = obj.buy_user;
        let sell_user = obj.sell_user;
        let text = "<b>TRANSACTION: </b><br>" + "BUYER: " +
            buy_user + ", SELLER: " + sell_user +
            ", PRICE: " + obj.price.toString() +
            ", QUANTITY: " + obj.quantity.toString() +
            "， time: " + format_dt_text(obj.datetime);
        if (log_transaction_id.indexOf(obj.id) == -1) {
            add_log(text, "yellow");
            log_transaction_id.push(obj.id);
        }
    })
}

function process() {
    $.get("/process", function (data) {
        console.log(data);
    })
}

function confirm() {
    let mode = $("#buy").prop("checked");
    let color_class = mode ? "red" : "green";

    if (mode) {
        mode = "buy ";
    } else {
        mode = "sell ";
    }

    let price = $("#price").val();
    let num = $("#num").val();
    if (price == "" || num == "") {
        alert("Invalid input!");
        return;
    }

    let text = num + " hand(s) with price = ¥" + price;
    add_log("<i>" + user_id + "</i> want to " + mode + " " + text, color_class);
    num = parseInt(num);
    price = parseFloat(price);

    if (mode == "buy ") {
        buy_table.push(new Array(user_id, num, price));
        sort(buy_table, 2, "decline");
    } else {
        sell_table.push(new Array(user_id, num, price));
        sort(sell_table, 2, "rise");
    }

    /* processing transaction */
    process_transaction(mode.slice(0, -1));
    update_table(".buy-list tbody", buy_table);
    update_table(".sell-list tbody", sell_table);

    /* update lowest and highest price */
    if (buy_table.length > 0) {
        start_price = buy_table[buy_table.length - 1][2];
        end_price = buy_table[0][2];
    }
    if (sell_table.length > 0) {
        end_price = max(end_price, sell_table[sell_table.length - 1][2]);
        start_price = min(start_price, sell_table[0][2]);
    }
    start_price = Math.floor(start_price);
    end_price = Math.ceil(end_price);

    let canvas = update_canvas();
    update_bid_on_canvas(canvas, buy_table, "red");
    update_bid_on_canvas(canvas, sell_table, "green");
}

function max(a, b) {
    return a > b ? a : b;
}

function min(a, b) {
    return a < b ? a : b;
}

function process_transaction(buy_or_sell) {
    while (true) {
        if (buy_table.length == 0 || sell_table.length == 0) {
            return;
        }

        let highest_buy_price = buy_table[0][2];
        let lowest_sell_price = sell_table[0][2];
        if (highest_buy_price < lowest_sell_price) {
            return;
        } else {
            if (buy_or_sell == "buy") {
                let buy_hand = buy_table[0][1];
                for (let i = 0; i < sell_table.length; i++) {
                    let sellor = sell_table[i][0];
                    let sell_hand = sell_table[i][1];
                    let sell_price = sell_table[i][2];
                    if (buy_hand < sell_hand) {
                        sell_table[i][1] -= buy_hand;
                        buy_table.shift();
                        let info =
                            "<b>TRANSACTION</b>: <i>" +
                            user_id +
                            "</i> buy " +
                            buy_hand.toString() +
                            " hand(s) from <i>" +
                            sellor +
                            "</i> with price = ¥" +
                            sell_price.toString();
                        add_log(info, "red");
                        return;
                    } else {
                        buy_hand -= sell_hand;
                        let info =
                            "<b>TRANSACTION</b>: <i>" +
                            user_id +
                            "</i> buy " +
                            sell_hand.toString() +
                            " hand(s) from <i>" +
                            sellor +
                            "</i> with price = ¥" +
                            sell_price.toString();
                        add_log(info, "red");
                        sell_table.shift();
                        if (buy_hand > 0) {
                            buy_table[0][1] = buy_hand;
                        } else {
                            buy_table.shift();
                            return;
                        }
                    }
                }
            }
            if (buy_or_sell == "sell") {
                let sell_hand = sell_table[0][1];
                for (let i = 0; i < buy_table.length; i++) {
                    let buyer = buy_table[i][0];
                    let buy_hand = buy_table[i][1];
                    let buy_price = buy_table[i][2];
                    if (sell_hand < buy_hand) {
                        buy_table[i][1] -= sell_hand;
                        sell_table.shift();
                        let info =
                            "<b>TRANSACTION</b>: <i>" +
                            user_id +
                            "</i> sell " +
                            sell_hand.toString() +
                            " hand(s) from <i>" +
                            buyer +
                            "</i> with price = ¥" +
                            buy_price.toString();
                        add_log(info, "green");
                        return;
                    } else {
                        sell_hand -= buy_hand;
                        let info =
                            "<b>TRANSACTION</b>: <i>" +
                            user_id +
                            "</i> buy " +
                            buy_hand.toString() +
                            " hand(s) from <i>" +
                            buyer +
                            "</i> with price = ¥" +
                            buy_price.toString();
                        add_log(info, "green");
                        buy_table.shift();
                        if (sell_hand > 0) {
                            sell_table[0][1] = sell_hand;
                        } else {
                            sell_table.shift();
                            return;
                        }
                    }
                }
            }
        }
    }
}

function sort(table, sort_ind, order) {
    if (order == "decline") {
        for (let i = 0; i < table.length; i++) {
            let max_value = -INF,
                max_ind = i;
            for (let j = i; j < table.length; j++) {
                if (max_value < table[j][sort_ind]) {
                    max_value = table[j][sort_ind];
                    max_ind = j;
                }
            }
            let temp1 = table[i][1],
                temp2 = table[i][2];
            table[i][1] = table[max_ind][1];
            table[i][2] = table[max_ind][2];
            table[max_ind][1] = temp1;
            table[max_ind][2] = temp2;
        }
    }

    if (order == "rise") {
        for (let i = 0; i < table.length; i++) {
            let min_value = INF,
                min_ind = i;
            for (let j = i; j < table.length; j++) {
                if (min_value > table[j][sort_ind]) {
                    min_value = table[j][sort_ind];
                    min_ind = j;
                }
            }
            let temp1 = table[i][1],
                temp2 = table[i][2];
            table[i][1] = table[min_ind][1];
            table[i][2] = table[min_ind][2];
            table[min_ind][1] = temp1;
            table[min_ind][2] = temp2;
        }
    }
}

function update_wish_table_from_db(tbody_selector, table_array) {
    let tbody = $(tbody_selector);
    tbody.empty();
    for (let i = 0; i < table_array.length; i++) {
        let each_row = "<tr>";
        let obj = table_array[i];
        each_row += "<td>" + obj.id + "</td>";
        each_row += "<td>" + obj.user + "</td>";
        each_row += "<td>" + obj.quantity + "</td>";
        each_row += "<td>" + obj.price + "</td>";
        each_row += "</tr>";
        tbody.append(each_row);
    }
}

function update_table(tbody_selector, table_array) {
    let tbody = $(tbody_selector);
    tbody.empty();
    for (let i = 0; i < table_array.length; i++) {
        let each_row = "<tr>";
        each_row += "<td>" + (i + 1).toString() + "</td>";
        for (let j = 0; j < table_array[i].length; j++) {
            each_row += "<td>" + table_array[i][j] + "</td>";
        }
        each_row += "</tr>";
        tbody.append(each_row);
    }
}

function add_log(text, color_class = "") {
    let selector = $(".logger-text-area");
    selector.append('<p class="' + color_class + '">> ' + text + "</p>");
    let height = selector[0].scrollHeight;
    selector.scrollTop(height);
}

function add_scale(x_pos, base_height, length, color = "black") {
    let scale_line = new fabric.Rect({
        left: x_pos,
        top: base_height - length,
        fill: color,
        width: 2,
        height: length * 2 + 2,
        lockMovementX: true,
        lockMovementY: true,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockScalingFlip: true,
        lockSkewing: true
    });
    return scale_line;
}

function add_triangle(x_pos, base_height, color) {
    let tri = new fabric.Triangle({
        width: 10,
        height: 7.5,
        fill: color,
        left: x_pos - 4,
        top: base_height
    });
    return tri;
}

function add_scale_text(text, size, x_pos, y_pos) {
    let scale_text = new fabric.Text(text, {
        left: x_pos,
        top: y_pos,
        hasControls: false,
        fill: "black",
        fontSize: size,
        lockMovementX: true,
        lockMovementY: true,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockScalingFlip: true,
        lockSkewing: true
    });
    return scale_text;
}

function draw_scale(
    canvas,
    base_width,
    base_height,
    scale_length = 8,
    scale_num = 10
) {
    let space = base_width / (scale_num + 1);
    let price_space = (end_price - start_price) / scale_num;
    if (start_price == INF) {
        return;
    }
    if (price_space == 0) {
        scale_num = 0;
        space = base_width;
    }
    start_pos = space / 2;
    for (let i = 0; i < scale_num + 1; i++) {
        let pos = start_pos + i * space;
        end_pos = pos;
        canvas.add(add_scale(pos, base_height, scale_length));
        let price = Math.round((start_price + price_space * i) * 100) / 100;
        canvas.add(
            add_scale_text(
                price.toString(),
                16,
                pos - 3,
                base_height - scale_length - 18
            )
        );
    }
}

function update_canvas() {
    $("#canv").empty();
    return draw();
}

function draw() {
    /* init base line */
    let width = $("#jumbotron-canv").css("width");
    let height = $("#jumbotron-canv").css("height");
    width = width.slice(0, -2);
    height = height.slice(0, -2);
    $("#canv").prop("width", width);
    $("#canv").prop("height", height);
    let base_height = parseInt(height) / 2;
    let base_width = parseInt(width) - 20;

    let canvas = new fabric.Canvas("canv");

    let rect = new fabric.Rect({
        left: 0,
        top: base_height,
        fill: "black",
        width: base_width,
        height: 2,
        lockMovementX: true,
        lockMovementY: true,
        lockRotation: true,
        lockScalingX: true,
        lockScalingY: true,
        lockScalingFlip: true,
        lockSkewing: true
    });
    canvas.add(rect);

    /* draw scale */
    draw_scale(
        canvas,
        base_width,
        base_height,
        (scale_length = 6),
        (scale_num = 10)
    );
    return canvas;
}

function update_bid_on_canvas(canvas, table, color) {
    if (start_price > end_price) {
        return;
    }
    let height = $("#jumbotron-canv").css("height");
    height = height.slice(0, -2);
    let base_height = parseInt(height) / 2;
    console.log(table);
    for (let i = 0; i < table.length; i++) {
        let row = table[i];
        let user_id = row[0];
        let hand = row[1];
        let price = row[2];
        let pos;
        if (start_pos < end_pos) {
            pos =
                start_pos +
                ((end_pos - start_pos) * (price - start_price)) /
                (end_price - start_price);
        } else {
            pos = (start_pos + end_pos) / 2;
        }
        canvas.add(add_triangle(pos, base_height + 5, color));
        //let user_text = add_scale_text(user_id, 14, pos - 3, base_height + 20, color);
        //let quantity_text = add_scale_text(hand.toString() + "手", 14, pos - 3, base_height + 40, color);
        //let price_text = add_scale_text(price.toString() + "元", 14, pos - 3, base_height + 60, color);
        //canvas.add(user_text);
        //canvas.add(quantity_text);
        //canvas.add(price_text);
    }
}