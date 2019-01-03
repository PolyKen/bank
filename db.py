from ORM import *

NotFound = Error("not found")
NotMatch = Error("not match")
NotEnough = Error("not enough")
InvalidParameter = Error("invalid parameter(s)")
PermissionDenied = Error("permission denied")


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
        d = Deposit.query(id=deposit_id)

        if d.account_id != self.id:
            NotMatch.print()
            return

        balance = d.get_balance()
        if balance < quantity:
            NotEnough.print()
            return

        interest = d.calc_interest()
        Deposit.update("where id={}".format(deposit_id), quantity=0)
        leftover = balance - quantity
        assert leftover >= 0
        if leftover > 0:
            Deposit(id=None, quantity=leftover, account_id=self.id, deposit_type=d.deposit_type,
                    currency_type=d.currency_type, start_time=None).insert()

        name = Currency.query(id=d.currency_type).name
        print(blue(">> withdraw {} {}".format(name, quantity)))
        return quantity

    @log
    def overdraft(self, quantity, currency_type=1):
        results = CreditCardUser.select(clause="where id={}".format(self.user_id))
        if len(results) == 0:
            PermissionDenied.print()
        else:
            Overdraft(id=None, quantity=quantity, currency_type=currency_type,
                      account_id=self.id, start_time=None).insert()

    @log
    def buy_financial_product(self, deposit_id, fp_id, quantity):
        fp = FinancialProduct.query(id=fp_id)
        if fp is None:
            NotFound.print()
        else:
            d = Deposit.query(id=deposit_id)
            if d["account_id"] != self.id:
                NotMatch.print()
            else:
                if d.get_balance() < quantity:
                    NotEnough.print()
                else:
                    self.withdraw(deposit_id=deposit_id, quantity=quantity)
                    FPTransaction(id=None, account_id=self.id, type_id=fp_id, quantity=quantity,
                                  start_time=None).insert()

    @log
    def exchange_currency(self, deposit_id, new_currency_type, new_currency_quantity):
        d = Deposit.query(id=deposit_id)
        if d.account_id != self.id:
            NotMatch.print()
            return

        old_currency_type = d.currency_type
        old_currency_rate = Currency.query(id=old_currency_type).exchange_rate
        new_currency_rate = Currency.query(id=new_currency_type).exchange_rate

        if d.get_balance() * old_currency_rate < new_currency_quantity * new_currency_rate:
            NotEnough.print()
            return

        self.withdraw(deposit_id=deposit_id, quantity=new_currency_quantity * new_currency_rate / old_currency_rate)
        Deposit(id=None, quantity=new_currency_quantity, deposit_type=1, currency_type=new_currency_type,
                account_id=self.id, start_time=None).insert()


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
    def calc_interest(self):
        if self.start_time is None:
            InvalidParameter.print()
            return 0

        time_delta = "(select timestampdiff(day, \"{}\", now()))".format(self.start_time)
        sql = "SELECT calc_interest({}, {}, {})".format(self.quantity, self.deposit_type, time_delta)
        res = execute_sql(sql)
        return float(res[0][0])

    @log
    def get_balance(self):
        if self.start_time is None:
            InvalidParameter.print()
            return 0
        sql = "SELECT get_balance({})".format(self.id)
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
    start_time = TimestampField()

    def __init__(self, id, account_id, type_id, quantity, start_time):
        super(FPTransaction, self).__init__(id=id, account_id=account_id, type_id=type_id,
                                            quantity=quantity, start_time=start_time)


if __name__ == '__main__':
    # test withdraw
    # Account.query(id=10026).withdraw(deposit_id=13, quantity=200)
    # Account.query(id=10007).withdraw(deposit_id=18, quantity=5000)

    # test buy financial products
    # Account.query(id=10026).buy_financial_product(fp_id=995, deposit_id=13, quantity=200)

    # test exchange currency
    # Account.query(id=10026).exchange_currency(deposit_id=13, new_currency_type=4, new_currency_quantity=10000)
