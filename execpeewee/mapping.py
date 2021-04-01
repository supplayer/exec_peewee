class PeeweeFields:
    pw_fields = {
        'bigint': 'BigIntegerField()',
        'binary': 'CharField()',
        'bit': 'UnknownField()',  # bit
        'blob': 'TextField()',
        'char': 'CharField()',
        'date': 'DateField()',
        'datetime': 'DateTimeField()',
        'decimal': 'DecimalField()',
        'double': 'FloatField()',
        'enum': 'CharField()',
        'float': 'FloatField()',
        'geometry': 'UnknownField()',  # geometry
        'geometrycollectigeometrycollection': 'UnknownField()',  # geometrycollection
        'int': 'IntegerField()',
        'integer': 'IntegerField()',
        'json': 'UnknownField()',  # json
        'linestring': 'UnknownField()',  # linestring
        'longblob': 'TextField()',
        'longtext': 'TextField()',
        'mediumblob': 'TextField()',
        'mediumint': 'IntegerField()',
        'mediumtext': 'TextField()',
        'multilinestring': 'UnknownField()',  # multilinestring
        'multipoint': 'UnknownField()',  # multipoint
        'multipolygon': 'UnknownField()',  # multipolygon
        'numeric': 'DecimalField()',
        'point': 'UnknownField()',  # point
        'polygon': 'UnknownField()',  # polygon
        'real': 'FloatField()',
        'set': 'CharField()',
        'smallint': 'IntegerField()',
        'text': 'TextField()',
        'time': 'TimeField()',
        'timestamp': 'TimestampField()',
        'tinyblob': 'TextField()',
        'tinyint': 'IntegerField()',
        'tinytext': 'TextField()',
        'varbinary': 'CharField()',
        'varchar': 'CharField()',
        'year': 'UnknownField()',  # year
        }

    @classmethod
    def update(cls, **kwargs):
        cls.pw_fields.update(**kwargs)
