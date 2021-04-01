class ExecPeewee:

    @staticmethod
    def ptable_fields(pw_table):
        return pw_table()._meta.sorted_field_names

    @classmethod
    def upsert(cls, pw_table, data: list, primary='id', batch_size=50):
        metadata = cls.__fork_upsert(pw_table, data, primary, batch_size)
        with pw_table()._meta.database.atomic():
            q_insert = pw_table.insert_many(**metadata['insert']).execute() if metadata['insert']['rows'] else 0
            q_update = pw_table.bulk_update(**metadata['update']) if metadata['update']['model_list'] else 0
            return {'insert': q_insert, 'update': q_update, 'total': q_insert+q_update}

    @classmethod
    def __fork_upsert(cls, pw_table, data, primary, batch_size):
        rows, model_list = [], []
        dids = set(i[primary] for i in data if i.get(primary))
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