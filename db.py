from ORM import *


class User(Model):
    __table__ = 'users'
    id = IntegerField(10)
    name = StringField(20)
    tel = BigIntegerField(30)
    address = StringField(60)
    city = StringField(20)
    mobile = BigIntegerField(30)
    email = StringField(30)

    def __init__(self, _id, _name, _tel, _address, _city, _mobile, _email):
        super(User, self).__init__(id=_id,
                                   name=_name,
                                   tel=_tel,
                                   address=_address,
                                   city=_city,
                                   mobile=_mobile,
                                   email=_email)


if __name__ == '__main__':
    user = User(19001, 'John Smith', 15012265, '2115 Party Rd.', 'San Francisco', 79841274508, 'john.smith@hotmail.com')
    user.insert()

