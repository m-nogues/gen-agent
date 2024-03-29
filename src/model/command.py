class Command:

    # Python native methods
    def __init__(self, name, errors):
        self.__name, self.__parameters, self.__errors = name, set(), errors

    def __str__(self):
        ret = 'name:\t' + self.__name + '\nparameters:' + ''.join(['\n\t' + p for p in self.__parameters])
        return ret

    # Attributes
    @property
    def name(self): return self.__name

    @property
    def errors(self): return self.__errors

    @property
    def parameters(self): return self.__parameters

    def add_parameter(self, parameter):
        try:
            self.__parameters.add(parameter)
        except:
            pass

    def del_parameter(self, parameter):
        try:
            self.__parameters.remove(parameter)
        except:
            pass

    # Useful methods
