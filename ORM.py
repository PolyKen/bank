from functools import reduce
import pymysql
from credentials import db_host, db_user, db_password
from utils import *


def join(attrs, pattern=','):
    return reduce(lambda x, y: '{}{}{}'.format(x, pattern, y), attrs)


@separate
def execute_sql(sql, *args):
    print(yellow("Execute SQL: {};".format(sql.replace('?', '{}').format(*args))))
    conn = pymysql.connect(host=db_host, user=db_user, passwd=db_password, db="bank")
    results = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.replace('?', '{}').format(*args) + ";")
            results = cursor.fetchall()
            for row in results:
                print(row)
            conn.commit()
            print(green('success with {} result(s)'.format(len(results))))
    except Exception as e:
        print(red("failed with error: {}".format(e)))
    finally:
        conn.close()
        return results


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
        print("initializing {}".format(name))
        if name == 'Model':
            print()
            return type.__new__(mcs, name, bases, attrs)

        mappings = dict()
        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                print("mapping: {} --> {}".format(k, v))
                mappings[k] = v
                fields.append(k)
        for k in mappings.keys():
            attrs.pop(k)

        print()

        attrs['__mappings__'] = mappings
        attrs['__fields__'] = fields
        attrs['__table__'] = attrs.get('__table__') or name

        attrs['__select__'] = 'SELECT ? FROM {}'.format(attrs['__table__'])
        attrs['__insert__'] = 'INSERT INTO {} (?) VALUES (?)'.format(attrs['__table__'])
        attrs['__update__'] = 'UPDATE {} SET ?'.format(attrs['__table__'])

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

    @classmethod
    def select(cls, column_list=None, clause=None):
        if column_list:
            if type(column_list) is str:
                column_list = [column_list]
            column_list = join(column_list)
        else:
            column_list = "*"

        if clause:
            select_sql = cls.__select__ + " " + clause
        else:
            select_sql = cls.__select__

        return execute_sql(select_sql, column_list)

    @classmethod
    def update(cls, clause, **kwargs):
        set_list = []
        for k, v in kwargs.items():
            set_list.append("{}={}".format(k, v))

        if clause:
            update_sql = cls.__update__ + " " + clause
        else:
            update_sql = cls.__update__

        execute_sql(update_sql, join(set_list))

    def insert(self):
        valid_fields = [f for f in self.__fields__ if self.get_value(f)]
        values = [self.get_value(f) for f in valid_fields]
        execute_sql(self.__insert__, join(valid_fields), join(values))


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
