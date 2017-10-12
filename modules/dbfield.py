class DbField(object):
    def __init__(self, name, type, primary_key=False, default=None, alias=None):
        self.value = default
        self.name = name
        self.options = {
            "type": type,
            "primary_key": primary_key
        }
        self.default = default
        self.alias = alias if alias else name

    def __repr__(self):
        if self.value:
            return str(self.value)
        return "Empty DBField object [{0}]".format(self.name)

    def __str__(self):
        if self.value:
            return str(self.value)
        return "Empty DBField object [{0}]".format(self.name)

    def __set__(self, instance, value):
        self.value = value

    def set(self, value):
        self.value = value

    def is_pk(self):
        return self.options["primary_key"]

    def get(self):
        return self.value

    def val(self, value=None):
        if value is not None:
            return self.set(value)
        return self.get()

    def get_type(self):
        return self.options["type"]

    def get_sql_create(self):
        return "{0} {1} {2}".format(self.name, self.options["type"], self.get_additional_params())

    def get_additional_params(self):
        string = ""
        if self.options["primary_key"]:
            string += "PRIMARY KEY "
        if self.default is not None:
            string += " DEFAULT '{0}'".format(self.default)
        return string
