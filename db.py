from ORM import *


class User(Model):
    __table__ = 'users'
    id = IntegerField(11)
    name = StringField(20)
    tel = BigIntegerField(30)
    address = StringField(60)
    city = StringField(20)
    mobile = BigIntegerField(30)
    email = StringField(30)

    def __init__(self, id, name, tel, address, city, mobile, email):
        super(User, self).__init__(id=id, name=name, tel=tel, address=address,
                                   city=city, mobile=mobile, email=email)


class CreditCardUser(Model):
    __table__ = 'credit_card_users'
    id = IntegerField(11)
    level = IntegerField(11)
    contact_person = StringField(20)
    contact_tel = BigIntegerField(30)
    job = StringField(20)
    income = IntegerField(30)

    def __init__(self, id, level, contact_person, contact_tel, job, income):
        super(CreditCardUser, self).__init__(id=id, level=level, contact_person=contact_person,
                                             contact_tel=contact_tel, job=job, income=income)


class Account(Model):
    __table__ = 'accounts'
    id = IntegerField(11)
    branch_id = IntegerField(11)
    user_id = IntegerField(11)

    def __init__(self, id, branch_id, user_id):
        super(Account, self).__init__(id=id, branch_id=branch_id, user_id=user_id)

    @log
    def deposit(self, quantity, deposit_type, currency_type):
        deposit = Deposit(id=None, quantity=quantity, deposit_type=deposit_type,
                          currency_type=currency_type, account_id=self.id, start_time=None)
        deposit.insert()

    @log
    def withdraw(self, deposit_id, quantity):
        results = Deposit.select(["quantity", "account_id"], "where id={}".format(deposit_id))
        _quantity, _account_id = results[0]["quantity"], results[0]["account_id"]

        if _account_id != self.id:
            error("deposit {} doesn't belong to {}".format(deposit_id, self.id))
            return

        if _quantity < quantity:
            error("deposit {} not enough".format(deposit_id))
            return

        Deposit.update("where id={}".format(deposit_id), quantity=_quantity - quantity)

    @log
    def overdraft(self, quantity, currency_type=1):
        results = CreditCardUser.select(clause="where id={}".format(self.user_id))
        if len(results) == 0:
            error("non credit card user is not allowed to overdraft")
        else:
            Overdraft(id=None, quantity=quantity, currency_type=currency_type,
                      account_id=self.id, start_time=None).insert()

    @log
    def buy_financial_product(self, deposit_id, fp_id, quantity):
        fp = FinancialProduct.query(id=fp_id)
        if fp is None:
            error("financial products with id {} not found".format(fp_id))
        else:
            d = Deposit.query(id=deposit_id)
            if d["account_id"] != self.id:
                error("deposit with id {} doesn't belong to account {}".format(deposit_id, self.id))
                return
            else:
                if d["quantity"] < quantity:
                    error("deposit with id {} not enough".format(deposit_id))
                else:
                    Deposit.update(clause="where id={}".format(deposit_id),
                                   quantity=float(d["quantity"]) - float(quantity))
                    FPTransaction(id=None, account_id=self.id, type_id=fp_id, quantity=quantity).insert()


class Deposit(Model):
    __table__ = 'deposit'
    id = IntegerField(11)
    quantity = FloatField()
    deposit_type = IntegerField(11)
    currency_type = IntegerField(11)
    account_id = IntegerField(11)
    start_time = TimestampField()

    def __init__(self, id, quantity, deposit_type, currency_type, account_id, start_time):
        super(Deposit, self).__init__(id=id, quantity=quantity, deposit_type=deposit_type,
                                      currency_type=currency_type, account_id=account_id,
                                      start_time=start_time)

    @log
    def calc_interest(self, quantity):
        if self.quantity < quantity:
            error("deposit {} not enough".format(self.id))
            return 0

        if self.start_time is None:
            error("invalid start_time")
            return 0

        time_delta = "(select timestampdiff(day, \"{}\", now()))".format(self.start_time)
        sql = "SELECT calc_interest({}, {}, {})".format(quantity, self.deposit_type, time_delta)
        res = execute_sql(sql)
        return float(res[0][0])


class Overdraft(Model):
    __table__ = 'overdraft'
    id = IntegerField(11)
    quantity = FloatField()
    currency_type = IntegerField(11)
    account_id = IntegerField(11)
    start_time = TimestampField()

    def __init__(self, id, quantity, currency_type, account_id, start_time):
        super(Overdraft, self).__init__(id=id, quantity=quantity, currency_type=currency_type,
                                        account_id=account_id, start_time=start_time)


class InterestRate(Model):
    __table__ = 'interest_rate'
    id = IntegerField(11)
    interest_type = StringField(30)
    rate = FloatField()
    due_months = IntegerField(11)

    def __init__(self, id, interest_type, rate, due_months):
        super(InterestRate, self).__init__(id=id, type=interest_type, rate=rate, due_months=due_months)


class Currency(Model):
    __table__ = 'currency'
    id = IntegerField(11)
    name = StringField(20)
    exchange_rate = FloatField()

    def __init__(self, id, name, exchange_rate):
        super(Currency, self).__init__(id=id, name=name, exchange_rate=exchange_rate)


class FinancialProduct(Model):
    __table__ = 'financial_products'
    id = IntegerField(11)
    name = StringField(20)
    due_months = IntegerField(11)
    interest_rate = FloatField()
    guaranteed = IntegerField(1)

    def __init__(self, id, name, due_months, interest_rate, guaranteed):
        super(FinancialProduct, self).__init__(id=id, name=name, due_months=due_months,
                                               interest_rate=interest_rate, guaranteed=guaranteed)


class FPTransaction(Model):
    __table__ = 'fp_transaction'
    id = IntegerField(11)
    account_id = IntegerField(11)
    type_id = IntegerField(11)
    quantity = FloatField()

    def __init__(self, id, account_id, type_id, quantity):
        super(FPTransaction, self).__init__(id=id, account_id=account_id, type_id=type_id, quantity=quantity)


if __name__ == '__main__':
    # user = User(_id=19002, _name='Marina Abraham', _tel=35012251, _address='2204 Newton Rd.',
    #             _city='San Francisco', _mobile=90348201998, _email='marina.abraham@hotmail.com')
    # credit_card_user = CreditCardUser(_id=19002, _level=1, _contact_person='George Abraham',
    #                                   _contact_tel=23545365677, _job='Associate Professor',
    #                                   _income=80000)
    # deposit = Deposit(_id=12, _account_id=10010, _currency_type=3, _deposit_type=2,
    #                   _quantity=24000, _start_time=None)
    # user.insert()
    # credit_card_user.insert()
    # deposit.insert()

    # obj_list = User.select(["id", "name"])
    Account.query(id=10002).overdraft(quantity=10000, currency_type=2)
    Account.query(id=10026).buy_financial_product(deposit_id=13, fp_id=1, quantity=100)
    # Deposit.query(id=17).calc_interest(10000)
