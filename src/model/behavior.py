import json
from copy import deepcopy


def load_bias(role, services):
    bias = dict()
    with open('conf/' + role + '.json', 'r') as f:
        tmp = json.load(f)

    for t in tmp.keys():
        bias[t] = dict()
        for s in services:
            if s.name in tmp[t].keys():
                bias[t][s.name] = tmp[t][s.name]

        total = 0
        for v in bias[t].values():
            total += v['bias']

        if total == 0.0:
            total = 1.0

        for b in bias[t]:
            bias[t][b]['bias'] /= total
    return bias


class Behavior:

    # Python native methods
    def __init__(self, name, services, role):
        self.__name, self.__bias = name, dict()

        try:
            self.__bias = load_bias(role, services)
        except OSError:
            print("Behavior for `{}` is not configured".format(role))

    def __str__(self):
        ret = 'name:\t' + self.__name + '\nbias:' + json.dumps(self.__bias, indent='t')

        return ret

    # Attributes
    @property
    def name(self): return self.__name

    @property
    def bias(self): return deepcopy(self.__bias)

    def change_bias(self, key, value):
        if not isinstance(value, float) or value > 1.0 or value < 0.0 or sum(self.bias.value()) > 1.0:
            raise TypeError('value must be between 0.0 and 1.0 and total must be less than 1.0')
        if key in self.__bias:
            self.__bias[key] = value
        else:
            raise KeyError(key + ' is not a valid service')

    def get_bias(self, key):
        if key in self.__bias:
            return self.__bias[key]
        else:
            raise KeyError(key + ' is not a valid service')
