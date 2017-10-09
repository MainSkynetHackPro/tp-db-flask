class DbField:
    def __init__(self, name, type, primary_key=False):
        self.value = None
        self.name = name
        self.options = {
            "type": type,
            "primary_key": primary_key
        }

    def __repr__(self):
        if self.value:
            return self.value
        return "Empty DBField object [{0}]".format(self.name)

    def __str__(self):
        if self.value:
            return self.value
        return "Empty DBField object [{0}]".format(self.name)

    def __set__(self, instance, value):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def val(self, value=None):
        if value:
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
        return string
