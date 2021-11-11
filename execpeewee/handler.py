from functools import reduce
from json import JSONEncoder, loads, dumps
from datetime import datetime, date
import operator


class ExecPeewee:

    @staticmethod
    def field_names(pw_table):
        return pw_table()._meta.sorted_field_names

    @classmethod
    def fields(cls, pw_table, include: set = None, exclude: set = None):
        """
        peewee select fields with include or exclude.
        """
        return [pw_table()._meta.fields[f] for f in (include or (set(cls.field_names(pw_table)) - (exclude or set())))]

    @classmethod
    def batch_insert(cls, pw_table, data: iter, batch_size=100):
        return sum([i['insert'] for i in [cls.upsert(pw_table, i, batch_size=batch_size, update=False)
                                          for i in cls.iter_data(data, batch_size)]])

    @classmethod
    def batch_update(cls, pw_table, data: iter, batch_size=100, primary='id'):
        return sum([i['update'] for i in [cls.upsert(pw_table, i, primary, batch_size, insert=False)
                                          for i in cls.iter_data(data, batch_size)]])

    @classmethod
    def batch_upsert(cls, pw_table, data: iter, batch_size=100, primary='id'):
        q_insert, q_update = 0, 0
        for i in [cls.upsert(pw_table, i, primary, batch_size) for i in cls.iter_data(data, batch_size)]:
            q_insert += i['insert']
            q_update += i['update']
        return {'insert': q_insert, 'update': q_update, 'total': q_insert + q_update}

    @classmethod
    def upsert(cls, pw_table, data: list, primary='id', batch_size=100, insert=True, update=True):
        metadata = cls.__fork_upsert(pw_table, data, primary, batch_size)
        with pw_table()._meta.database.atomic():
            q_insert = pw_table.insert_many(**metadata['insert']
                                            ).execute() if metadata['insert']['rows'] and insert else 0
            q_update = pw_table.bulk_update(**metadata['update']
                                            ) if metadata['update']['model_list'] and update else 0
            return {'insert': q_insert, 'update': q_update, 'total': q_insert + q_update}

    @staticmethod
    def select(pw_table, rule_fields: list):
        """
        :param pw_table: -> peeweetable
        :param rule_fields: -> list e.g: [['create_time', '==', '2020-04-05 17:00:00'], ['source_id', '>', 12]]
        :return: -> dict <generator>
        """
        clauses_rule, clauses_sel = [], []
        for rule in rule_fields:
            field, oper, value = rule[0], rule[1], f'"{rule[2]}"' if type(rule[2]) is str else rule[2]
            rule = (eval(f'pw_table.{field}{oper}{value}'))
            clauses_rule.append(rule)
        return pw_table.select().where(reduce(operator.and_, clauses_rule))

    @classmethod
    def iter_data(cls, data, batch_size=100):
        insert_data = []
        for i in data:
            if len(insert_data) >= batch_size:
                current_data = insert_data[:]
                insert_data.clear()
                yield current_data
            insert_data.append(i)
        yield insert_data

    @classmethod
    def date_encoder(cls, data):
        return loads(dumps(data, cls=DateEncoder))

    @classmethod
    def __clear_data(cls, insert_data: list):
        current_data = insert_data[:]
        insert_data.clear()
        return current_data

    @classmethod
    def __fork_upsert(cls, pw_table, data, primary, batch_size):
        rows, model_list = [], []
        dids = set(i[primary] for i in data if i.get(primary) or i.get(primary) == 0)
        exist_ids = cls.__record_exists(pw_table, dids)
        [model_list.append(i) if i.get(primary) in exist_ids else rows.append(i) for i in data]
        cls.__data_check(rows)
        cls.__data_check(model_list)
        return {
            'insert': {'rows': rows},
            'update': {'model_list': [pw_table(**i) for i in model_list], 'batch_size': batch_size,
                       'fields': list(model_list[0].keys()) if model_list else []}}

    @classmethod
    def __record_exists(cls, pw_table, ids: set):
        return set(i.id for i in pw_table.select(pw_table.id).where(pw_table.id.in_(ids)))

    @classmethod
    def __data_check(cls, data):
        [cls.__check_result(i, data[0]) for i in data] if data else []

    @classmethod
    def __check_result(cls, data: dict, simple: dict):
        if data.keys() != simple.keys():
            raise ValueError(f'keys not match: {data} VS {simple}')


class DateEncoder(JSONEncoder):
    """
    TypeError: Object of type 'datetime' is not JSON serializable
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return JSONEncoder.default(self, obj)
