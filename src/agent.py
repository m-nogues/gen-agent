import random
import socket
import subprocess
from copy import deepcopy

from src.model import behavior

AGENT_IP = ''


def format_parameter(parameter, vm):
    """Formats the parameter for a command

    Arguments:
        parameter {string} -- The parameter to format
        vm {vm} -- The VM targeted by the command

    Returns:
        string -- The formatted parameter
    """
    ret = parameter.replace('&ip', vm.ip).replace('&mac', vm.mac)
    return ret


def choose_vm(rand_service, vms):
    tmp = deepcopy(vms)
    rand_vm = random.choice(tmp)
    while True:
        for s in rand_vm.services:
            if rand_service in s.name:
                rand_service = s
                break
        else:
            tmp.pop(rand_vm)
            rand_vm = random.choice(tmp)
            continue
        break
    return rand_service, rand_vm


def rec_cmd():
    if AGENT_IP:
        while True:
            port = 10
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(())
    else:
        print('IP not set')


def set_ip(ip):
    global AGENT_IP
    AGENT_IP = ip


class Agent:

    # Python native methods
    def __init__(self, ip, bhvr, services):
        set_ip(ip)

        self.__behavior, self.__services = behavior.Behavior(ip + ' - ' + bhvr, services, bhvr), services

    def __str__(self):
        ret = 'ip:\t' + AGENT_IP + '\nservices:'
        i = 0
        for service in self.__services:
            ret += '\n\tservice_' + str(i) + ':' + ''.join(['\n\t\t' + line for line in str(service).split('\n')])
            i += 1

        ret += '\nbehavior:' + ''.join(['\n\t' + line for line in str(self.__behavior).split('\n')])

        return ret

    # Useful Methods
    def action(self, vms):
        # Choose biased service
        biased_list = list()
        for service, bias in self.__behavior.bias.items():
            biased_list += [service for _ in range(int(bias * 100))]

        rand_service = random.sample(biased_list, 1)[0]

        # Choose random VM to perform action on
        rand_service, rand_vm = choose_vm(rand_service, vms)

        # Choose random command and parameters
        rand_command = random.sample(rand_service.commands, 1)[0]
        rand_parameter = format_parameter(random.sample(rand_command.parameters, 1)[0], rand_vm)

        result = subprocess.run([rand_command, rand_parameter], stdout=subprocess.PIPE)

        for err in rand_command.errors:
            if err in result.stdout:
                self.action(vms)
                break

    def to_csv(self):
        ret = {
            'ip': AGENT_IP,
            'services': ' '.join([service.name for service in self.__services]),
            'behavior': self.__behavior.name
        }
        return ret

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

    # Attributes
    @property
    def services(self):
        return self.__services

    @property
    def behavior(self):
        return self.__behavior

    @property
    def started(self):
        return self.__started
