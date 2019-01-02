function read_wish() {
    $.get("/read-wish/buy", function (data) {
        let buy_table = "";
        if (data != "[]") {
            buy_table = parse_wish_table(data);
        }
        console.log(buy_table);
        update_wish_table_from_db(".buy-list tbody", buy_table); 
        $.get("/read-wish/sell", function (data) {
            let sell_table = "";
            if (data != "[]") {
                sell_table = parse_wish_table(data);
            }
            console.log(sell_table);
            update_wish_table_from_db(".sell-list tbody", sell_table); 

            if (buy_table.length > 0) {
                start_price = buy_table[buy_table.length - 1].price;
                end_price = buy_table[0].price;
            }

            if (sell_table.length > 0) {
                end_price = max(end_price, sell_table[sell_table.length - 1].price);
                start_price = min(start_price, sell_table[0].price);
            }
            start_price = Math.floor(start_price);
            end_price = Math.ceil(end_price);
        
            let canvas = update_canvas();
            update_bid_on_canvas(canvas, buy_table, "red");
            update_bid_on_canvas(canvas, sell_table, "green");
        });
    });
}

function parse_wish_table(raw_data) {
    let obj_pattern = /\"(.*?)\"/g;
    let raw_obj_list = raw_data.match(obj_pattern);
    let obj_list = [];
    for (let i = 0; i < raw_obj_list.length; i++) {
        let raw_obj = raw_obj_list[i];
        let obj = parse_wish_obj(raw_obj);
        obj_list.push(obj);
    }
    return obj_list;
}

function parse_transaction_obj(obj_string) {
    //(32, datetime.datetime(2018, 11, 25, 10, 46, 33), 'Tom', 'Tom', 2, 1200.0)
    let obj = Object();
    let number_ptn = /\d+\.?\d*[,)]/g;
    let user_ptn = /'.*?'/g;
    let raw_numbers = obj_string.match(number_ptn);
    for (let i = 0; i < raw_numbers.length; i++) {
        raw_numbers[i] = raw_numbers[i].slice(0, -1);
    }
    let dt_array = [];
    for (let i = 1; i <= 6; i++) {
        dt_array.push(Number(raw_numbers[i]));
    }
    let users = obj_string.match(user_ptn);
    let buy_user = users[0].slice(1, -1);
    let sell_user = users[0].slice(1, -1);
    let id = Number(raw_numbers[0]);
    let quantity = Number(raw_numbers[7]);
    let price = Number(raw_numbers[8]);
    obj.buy_user = buy_user;
    obj.sell_user = sell_user;
    obj.id = id;
    obj.quantity = quantity;
    obj.price = price;
    obj.datetime = dt_array;
    return obj;
}

function parse_wish_obj(obj_string) {
    let obj = Object();
    //{'user': 'test_user', 'id': 3, 'price': 3.0, 'time…datetime(2018, 11, 14, 21, 1, 10), 'quantity': 2}
    //"(9, datetime.datetime(2018, 11, 24, 13, 16, 26), 'Tom', 1, 12345, 987654000.0)"
    let number_ptn = /\d+\.?\d*[,)]/g;
    let user_ptn = /'.*?'/;
    let raw_numbers = obj_string.match(number_ptn);
    for (let i = 0; i < raw_numbers.length; i++) {
        raw_numbers[i] = raw_numbers[i].slice(0, -1);
    }
    let dt_array = [];
    for (let i = 1; i <= 6; i++) {
        dt_array.push(Number(raw_numbers[i]));
    }
    let user = obj_string.match(user_ptn)[0].slice(1, -1);
    let id = Number(raw_numbers[0]);
    let mode = Number(raw_numbers[7]);
    let quantity = Number(raw_numbers[8]);
    let price = Number(raw_numbers[9]);
    obj.user = user;
    obj.id = id;
    obj.mode = mode;
    obj.quantity = quantity;
    obj.price = price;
    obj.datetime = dt_array;
    return obj;
}

function read_transaction() {
    $.get("/read-transaction", function (data) {
        let transaction_table = parse_wish_table(data);
        console.log(transaction_table);
    });
}

function add_wish(user, mode, quantity, price) {
    if (typeof quantity != "string") {
        quantity = quantity.toString();
    }
    if (typeof mode != "string") {
        mode = mode.toString();
    }
    if (typeof price != "string") {
        price = price.toString();
    }
    $.get(
        "/add-wish/" + user + "/" + mode + "/" + quantity + "/" + price,
        function (data) {
            console.log(data);
        }
    );
}