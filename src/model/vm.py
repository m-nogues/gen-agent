class Vm:

    # Python native methods
    def __init__(self, ip):
        self.__ip, self.__services = ip, set()

    def __str__(self):
        ret = 'ip:\t' + self.__ip + '\nservices:'
        i = 0
        for service in self.__services:
            ret += '\n\tservice_' + str(i) + ':' + ''.join(['\n\t\t' + line for line in str(service).split('\n')])
            i += 1

        return ret

    # Attributes
    @property
    def ip(self): return self.__ip

    @property
    def services(self): return self.__services

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

    def to_csv(self):
        ret = {
            'ip': self.__ip,
            'services': ' '.join([service.name for service in self.__services])
        }
        return ret
