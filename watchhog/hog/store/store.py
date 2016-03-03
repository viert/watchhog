from collections import defaultdict, Counter

class Store(object):
    def __init__(self, index_fields=[]):
        self.table = []
        self.indexes = {}
        self.vars = {}
        for field in index_fields:
            self.add_index(field)

    def add_index(self, field):
        if not field in self.indexes:
            self.indexes[field] = {}
            self.clear_index(field)
            self.reindex(field)

    def remove_index(self, field):
        if field in self.indexes:
            del(self.indexes[field])

    def clear_index(self, field):
        keyparts = field.split('.')
        if len(keyparts) == 1:
            self.indexes[field]['index'] = defaultdict(list)
            self.indexes[field]['keys'] = []
            self.indexes[field]['counter'] = Counter()
        elif len(keyparts) == 2:
            self.indexes[field]['index'] = defaultdict(lambda: defaultdict(list))
            self.indexes[field]['counter'] = defaultdict(Counter)
        else:
            raise NotImplementedError('Complex indexes of more than two fields are not implemented')

    def clear_all_indexes(self):
        for field in self.indexes:
            self.clear_index(field)

    def fields(self):
        if len(self.table) == 0:
            return []
        else:
            return self.table[0].keys()

    def set_var(self, var_name, obj):
        self.vars[var_name] = obj

    def reindex(self, field):
        self.clear_index(field)
        keyparts = field.split('.')

        if len(keyparts) == 1:
            keys = set()

            for i, record in enumerate(self.table):
                try:
                    field_value = record[field]
                except KeyError:
                    continue
                self.indexes[field]['index'][field_value].append(i)
                self.indexes[field]['counter'][field_value] += 1
                keys.add(field_value)

            self.indexes[field]['keys'] = list(keys)
            self.indexes[field]['keys'].sort()

        else:
            (first, second) = keyparts
            for i, record in enumerate(self.table):
                try:
                    self.indexes[field]['index'][record[first]][record[second]].append(i)
                    self.indexes[field]['counter'][record[first]][record[second]] += 1
                except KeyError:
                    continue

    def __add_record_to_index(self, record, field, i):
        keyparts = field.split('.')
        if len(keyparts) == 1:
            try:
                field_value = record[field]
            except KeyError:
                return
            self.indexes[field]['index'][field_value].append(i)
            self.indexes[field]['counter'][field_value] += 1
            if not field_value in self.indexes[field]['keys']:
                self.indexes[field]['keys'].append(field_value)
                self.indexes[field]['keys'].sort()
        else:
            (first, second) = keyparts
            try:
                self.indexes[field]['index'][record[first]][record[second]].append(i)
                self.indexes[field]['counter'][record[first]][record[second]] += 1
            except KeyError:
                return

    def reindex_all(self):
        for field in self.indexes:
            self.reindex(field)

    def empty(self):
        self.clear_all_indexes()
        self.table = []

    def push(self, record, auto_index=True):
        i = len(self.table)
        self.table.append(record)
        if auto_index:
            for field in self.indexes:
                self.__add_record_to_index(record, field, i)

    def get_field_index(self, field):
        try:
            return self.indexes[field]['index']
        except KeyError:
            return None

    def get_field_counter(self, field):
        try:
            return self.indexes[field]['counter']
        except KeyError:
            return None

    def get_field_keys(self, field):
        try:
            return self.indexes[field]['keys']
        except KeyError:
            return None