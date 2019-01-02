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

    def __init__(self, _id, _name, _tel, _address, _city, _mobile, _email):
        super(User, self).__init__(id=_id, name=_name, tel=_tel, address=_address,
                                   city=_city, mobile=_mobile, email=_email)


class CreditCardUser(Model):
    __table__ = 'credit_card_users'
    id = IntegerField(11)
    level = IntegerField(11)
    contact_person = StringField(20)
    contact_tel = BigIntegerField(30)
    job = StringField(20)
    income = IntegerField(30)

    def __init__(self, _id, _level, _contact_person, _contact_tel, _job, _income):
        super(CreditCardUser, self).__init__(id=_id, level=_level, contact_person=_contact_person,
                                             contact_tel=_contact_tel, job=_job, income=_income)


class Account(Model):
    __table__ = 'accounts'
    id = IntegerField(11)
    branch_id = IntegerField(11)
    user_id = IntegerField(11)

    def __init__(self, _id, _branch_id, _user_id):
        super(Account, self).__init__(id=_id, branch_id=_branch_id, user_id=_user_id)

    def deposit(self, quantity, deposit_type, currency_type):
        deposit = Deposit(_id=None, _quantity=quantity, _deposit_type=deposit_type,
                          _currency_type=currency_type, _account_id=self.id, _start_time=None)
        deposit.insert()

    def withdraw(self, deposit_id, quantity):
        results = Deposit.select(["quantity", "account_id"], "where id={}".format(deposit_id))
        _quantity, _account_id = results[0][0], results[0][1]

        if _account_id != self.id:
            raise Exception("deposit {} doesn't belong to {}".format(deposit_id, self.id))

        if _quantity < quantity:
            raise Exception("deposit {} not enough".format(deposit_id))
        else:
            Deposit.update("where id={}".format(deposit_id), quantity=_quantity-quantity)


class Deposit(Model):
    __table__ = 'deposit'
    id = IntegerField(11)
    quantity = FloatField()
    deposit_type = IntegerField(11)
    currency_type = IntegerField(11)
    account_id = IntegerField(11)
    start_time = TimestampField()

    def __init__(self, _id, _quantity, _deposit_type, _currency_type, _account_id, _start_time):
        super(Deposit, self).__init__(id=_id, quantity=_quantity, deposit_type=_deposit_type,
                                      currency_type=_currency_type, account_id=_account_id,
                                      start_time=_start_time)


class Overdraft(Model):
    __table__ = 'overdraft'
    id = IntegerField(11)
    quantity = FloatField()
    currency_type = IntegerField(11)
    account_id = IntegerField(11)
    start_time = TimestampField()

    def __init__(self, _id, _quantity, _currency_type, _account_id, _start_time):
        super(Overdraft, self).__init__(id=_id, quantity=_quantity, currency_type=_currency_type,
                                        acccount_id=_account_id, start_time=_start_time)


class InterestRate(Model):
    __table__ = 'interest_rate'
    id = IntegerField(11)
    type = StringField(30)
    rate = FloatField()
    due_months = IntegerField(11)

    def __init__(self, _id, _type, _rate, _due_months):
        super(InterestRate, self).__init__(id=_id, type=_type, rate=_rate, due_months=_due_months)


class Currency(Model):
    __table__ = 'currency'
    id = IntegerField(11)
    name = StringField(20)
    exchange_rate = FloatField()

    def __init__(self, _id, _name, _exchange_rate):
        super(Currency, self).__init__(id=_id, name=_name, exchange_rate=_exchange_rate)


class FinancialProduct(Model):
    __table__ = 'financial_products'
    id = IntegerField(11)
    name = StringField(20)
    due_months = IntegerField(11)
    interest_rate = FloatField()
    guaranteed = IntegerField(1)

    def __init__(self, _id, _name, _due_months, _interest_rate, _guaranteed):
        super(FinancialProduct, self).__init__(id=_id, name=_name, due_months=_due_months,
                                               interest_rate=_interest_rate, guaranteed=_guaranteed)


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

    User.select(["id", "name"])
    account = Account(_id=10026, _branch_id=2001, _user_id=15003)
    account.deposit(quantity=1000, currency_type=1, deposit_type=1)
    account.withdraw(deposit_id=13, quantity=1000)
