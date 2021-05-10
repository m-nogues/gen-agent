class Vm:

    # Python native methods
    def __init__(self, ip, behavior):
        self.__ip, self.__behavior, self.__services = ip, behavior, set()

    def __str__(self):
        ret = 'ip:\t' + self.__ip + '\nservices:'
        i = 0
        for service in self.__services:
            ret += '\n\tservice_' + str(i) + ':' + ''.join(['\n\t\t' + line for line in str(service).split('\n')])
            i += 1

        ret += '\nbehavior:' + ''.join(['\n\t' + line for line in str(self.__behavior).split('\n')])

        return ret

    # Attributes
    @property
    def ip(self): return self.__ip

    @property
    def services(self): return self.__services

    @property
    def behavior(self): return self.__behavior

    # Useful methods
    def add_service(self, service):
        try:
            self.__services.add(service)
        except:
            pass

    def del_service(self, service):
        try:
            self.__services.remove(service)
        except:
            pass

    def update_behavior(self, service, bias):
        self.__behavior.change_bias((service, bias))

    def to_csv(self):
        ret = {
            'ip': self.__ip,
            'services': ' '.join([service.name for service in self.__services]),
            'behavior': self.__behavior.name
        }
        return ret
