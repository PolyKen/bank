from functools import reduce
import pymysql
from credentials import db_host, db_user, db_password


def join(attrs, pattern=','):
    return reduce(lambda x, y: '{}{}{}'.format(x, pattern, y), attrs)


def execute_sql(sql, *args):
    print("SQL: {};".format(sql.replace('?', '{}').format(*args)))
    conn = pymysql.connect(host=db_host, user=db_user, passwd=db_password, db="bank")
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.replace('?', '{}').format(*args) + ";")
            results = cursor.fetchall()
            for row in results:
                print(row)
            conn.commit()
            print('success')
    except Exception as e:
        print(e)
    finally:
        conn.close()
    return 0


class Field(object):
    def __init__(self, column_type, max_length, **kwargs):
        self.column_type = column_type
        self.max_length = max_length
        self.default = None
        if kwargs:
            # override attributes
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)

    def __str__(self):
        return '<{}>'.format(self.__class__.__name__)


class StringField(Field):
    def __init__(self, max_length, **kwargs):
        super(StringField, self).__init__(column_type='varchar({})'.format(max_length),
                                          max_length=max_length, kwargs=kwargs)


class IntegerField(Field):
    def __init__(self, max_length, **kwargs):
        super(IntegerField, self).__init__(column_type='int({})'.format(max_length),
                                           max_length=max_length, kwargs=kwargs)


class BigIntegerField(Field):
    def __init__(self, max_length, **kwargs):
        super(BigIntegerField, self).__init__(column_type='bigint({})'.format(max_length),
                                              max_length=max_length, kwargs=kwargs)


class FloatField(Field):
    def __init__(self, **kwargs):
        super(FloatField, self).__init__(column_type='float', max_length=None, kwargs=kwargs)


class TimestampField(Field):
    def __init__(self, **kwargs):
        super(TimestampField, self).__init__(column_type='timestamp', max_length=None, kwargs=kwargs)


class ModelMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        print('using ModelMetaClass')
        print(name, attrs)
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)

        mappings = dict()
        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                fields.append(k)
        for k in mappings.keys():
            attrs.pop(k)

        attrs['__mappings__'] = mappings
        attrs['__fields__'] = fields
        attrs['__table__'] = attrs.get('__table__') or name

        attrs['__insert__'] = 'INSERT INTO {} (?) VALUES (?)'.format(attrs['__table__'])

        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kwargs):
        # construct dict
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("'Model' object has no attribute named '{}'".format(key))

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, field):
        try:
            if self.__mappings__[field].__class__ == StringField:
                return '\"{}\"'.format(self[field])
            else:
                return self[field]
        except KeyError:
            for key in self:
                print("{}: {}".format(key, self[key]))
            raise KeyError

    def insert(self):
        valid_fields = [f for f in self.__fields__ if f]
        values = [self.get_value(f) for f in valid_fields]
        execute_sql(self.__insert__, join(self.__fields__), join(values))


if __name__ == '__main__':
    tst = StringField(max_length=20)
    print(tst)
    H = type('Hello', (object,), {"att1": lambda o: print("att1"), "att2": 13})
    h = H()
    h.att1()
    print(h.att2)
    print(dir(h))
    lst = [1, 2, 3, 6, 1, 4, 2]
    print(join(lst))
