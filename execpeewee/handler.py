from time import time
import threading
import asyncio
import functools


def __loops(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        coro = func(*args, **kwargs)
        loop.run_until_complete(coro)
    return wrapper


class Bulk:
    def __init__(self, pw_table, fields: list, exec_rate=10):
        self.__table = pw_table
        self.__fields = fields
        self.exec_rate = exec_rate
        self.data_store = {}
        self.__lock = threading.Lock()

    def create(self, data: dict, action='create', batch_size=50):
        store_name, query = f'{self.__table.__name__}_{action}', None
        self.__check_store_table(store_name)
        if len(self.data_store[store_name]['data']) >= batch_size:
            query = self.__lock_data_store(store_name, action, batch_size)
        self.__store_fields_append(data, self.__fields, store_name, action, batch_size)
        return query

    def __check_store_table(self, store_name):
        if store_name not in self.data_store:
            self.data_store[store_name] = {'data': [], 'timestamp': 0}

    def __store_fields_append(self, data, fields, store_name, action, batch_size):
        if self.__fields == fields:
            self.data_store[store_name]['data'].append(self.__table(data))
            self.data_store[store_name]['timestamp'] = time()
        else:
            self.__lock_data_store(store_name, action, batch_size)
            raise Exception(f'Data fields not match data_store. Data: {data}')

    def loop_data_execution(self):
        while True:
            print(self.data_store)
            [self.__lock_data_store(k, k.split('_')[-1])
             for k, v in self.data_store.items() if v['timestamp'] + self.exec_rate <= time()]

    def __table_action(self, action):
        return {'create': self.__table.bulk_create, 'update': self.__table.bulk_update}[action]

    def __lock_data_store(self, store_name, action, batch_size=50):
        query = None
        self.__lock.acquire()
        if action == 'create':
            query = self.__table_action(action)(
                self.data_store[store_name].pop('data'), batch_size=batch_size)
        elif action == 'update':
            query = self.__table_action(action)(
                self.data_store[store_name].pop('data'), fields=self.__fields, batch_size=batch_size)
        self.data_store[store_name]['data'] = []
        self.__lock.release()
        return query
