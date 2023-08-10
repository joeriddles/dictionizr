class DictionizrProperty():
    def __init__(self, datatype):
        self.datatype = datatype


class Dictionizr():
    def serializer(self):
        props = vars(self)
        for prop in props:
            if isinstance(prop, DictionizrProperty):
                pass

    def deserialize(self, data: dict):
        for key, value in data.items():
            prop = getattr(self, key)
            if isinstance(prop, DictionizrProperty):
                datatype = prop.datatype
                # ...


class InheritedClass(Dictionizr):
    foo = DictionizrProperty(str)
