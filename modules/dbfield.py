class DbField:
    def __init__(self, name, type, primary_key=False):
        self.value = None
        self.name = name
        self.options = {
            "type": type,
            "primary_key": primary_key
        }

    def get_sql_create(self):
        return "{0} {1} {2}".format(self.name, self.options["type"], self.get_additional_params())

    def get_additional_params(self):
        string = ""
        if self.options["primary_key"]:
            string += "PRIMARY KEY "
        return string
