import inspect


class RegisterMethodsMeta(type):
    def __new__(mcs, class_name, bases, class_dict, collection_name, method_pattern):
        class_dict[collection_name] = set()
        _class = super().__new__(mcs, class_name, bases, class_dict)

        def _insert_2_methods_seq(_cls, _items):
            for key, value in _items:
                if key.startswith(method_pattern):
                    if inspect.isroutine(value) and not isinstance(value, classmethod):
                        getattr(_cls, collection_name).add(value)

        _insert_2_methods_seq(_class, _class.__dict__.items())
        for base in _class.__mro__:
            _insert_2_methods_seq(_class, base.__dict__.items())

        return _class

