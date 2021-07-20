import json
import random
import subprocess
import threading
from copy import deepcopy
from datetime import datetime, time, timedelta

import pandas as pd

from src.model import action, behavior

AGENT_IP = ''


def format_parameter(parameter, vm):
    """Formats the parameter for a command

    Arguments:
        parameter {string} -- The parameter to format
        vm {vm} -- The VM targeted by the command

    Returns:
        string -- The formatted parameter
    """
    ret = parameter.replace('&ip', vm.ip)
    return ret


def choose_vm(rand_service, vms):
    tmp = deepcopy(vms)
    rand_vm = random.choice(tmp)
    while True:
        for s in rand_vm.services:
            if rand_service in s.name:
                return s, rand_vm
        else:
            tmp.remove(rand_vm)
            rand_vm = random.choice(tmp)


# def rec_cmd():
#     if AGENT_IP:
#         while True:
#             port = 10
#             sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             sock.bind(())
#     else:
#         print('IP not set')


def set_ip(ip):
    global AGENT_IP
    AGENT_IP = ip


def execute(command, parameter):
    result = subprocess.run([command.name, parameter], stdout=subprocess.PIPE)

    for err in command.errors:
        if err in result.stdout:
            return False

    return True


def note_action(timestamp, command, parameter):
    with open("actions.csv", "a") as f:
        f.write(timestamp + "," + command + "," + parameter + "\n")


class Agent:

    # Python native methods
    def __init__(self, ip, bhvr, services, network):
        set_ip(ip)
        self.__started = False

        self.__network, self.__actions = network, list()
        self.__behavior, self.__services = behavior.Behavior(ip + ' - ' + bhvr, services, bhvr), services

    def __str__(self):
        ret = 'ip:\t' + AGENT_IP + '\nservices:'
        i = 0
        for service in self.__services:
            ret += '\n\tservice_' + str(i) + ':' + ''.join(['\n\t\t' + line for line in str(service).split('\n')])
            i += 1

        ret += '\nbehavior:' + ''.join(['\n\t' + line for line in str(self.__behavior).split('\n')]) + '\nactions:'
        i = 0
        for action in self.__actions:
            ret += '\n\taction_' + str(i) + ':' + ''.join(['\n\t\t' + line for line in str(action).split('\n')])
            i += 1

        return ret

    # Useful Methods
    def action(self):
        # Find what bias to use at that time
        now = datetime.now().time()
        behavior = self.__behavior.bias

        for t in self.__behavior.bias.keys():
            start, end = t.split('-')
            start, end = time.fromisoformat(start), time.fromisoformat(end)

            if start < now < end:
                behavior = self.__behavior.bias[t]

        # No action if we are not in a defined time interval
        if 'bias' not in behavior[list(behavior.keys())[0]]:
            return

        # Choose biased service
        biased_list = list()
        for service, bias in behavior.items():
            biased_list += [service for _ in range(int(bias['bias'] * 100))]

        rand_service_name = random.sample(biased_list, 1)[0]

        # Choose random VM to perform action on
        rand_service, rand_vm = choose_vm(rand_service_name, self.__network)

        combo = random.randrange(behavior[rand_service.name]['combo_max'])
        self.repeat(behavior, rand_service, rand_vm, combo)

    def repeat(self, behavior, service, vm, combo):
        # Choose random command and parameters
        rand_command = random.sample(service.commands, 1)[0]
        rand_parameter = format_parameter(random.sample(rand_command.parameters, 1)[0], vm)

        if combo > 0:
            self.__actions += [action.Action(rand_command.name, datetime.now(), rand_parameter)]
            note_action(datetime.now(), rand_command.name, rand_parameter)
            if not execute(rand_command, rand_parameter):
                self.action()
                return

            combotimer = threading.Timer(random.randrange(behavior[service.name]['wait_time']), self.repeat,
                                         [behavior, service, vm, combo - 1])
            combotimer.start()
            combotimer.join()

    def to_json(self):
        ret = {
            'ip': AGENT_IP,
            'services': ' '.join([service.name for service in self.__services]),
            'behavior': self.__behavior.name,
            'actions': ';'.join(
                [str(action.timestamp) + ',' + action.name + ',' + action.parameters for action in self.__actions])
        }
        return ret

    def add_service(self, service):
        self.__services.add(service)

    def del_service(self, service):
        try:
            self.__services.remove(service)
        except KeyError:
            pass

    def update_behavior(self, service, bias):
        self.__behavior.change_bias(service, bias)

    @property
    def services(self):
        return self.__services

    def start(self, max_actions, start, end):
        if datetime.now() > end:
            raise ValueError("Wrong time of experiment set in configuration file")
        self.__started = True
        duration = end - start
        avg_between_action = duration.total_seconds() / max_actions
        action_threads = list()

        for i in range(max_actions):
            now = datetime.now()
            t_action = (start + timedelta(seconds=avg_between_action * i) - now).total_seconds()

            if now + timedelta(seconds=t_action) < end:
                # print("created timer at date : " + (now + timedelta(seconds=t_action)).strftime("%m/%d/%Y, %H:%M:%S"))
                action_threads += [threading.Timer(t_action, self.action)]
            else:
                # print("created timer at date : " + (now + timedelta(seconds=t_action)).strftime("%m/%d/%Y, %H:%M:%S"))
                action_threads += [threading.Timer((end - (now + timedelta(seconds=i))).total_seconds(), self.action)]

        with open("actions.csv", "w") as f:
            f.write("timestamp,command,parameters\n")

        now = datetime.now()
        stop_thread = threading.Timer((end - now).total_seconds(), self.stop)

        for t in action_threads:
            t.start()
        stop_thread.start()

        for t in action_threads:
            t.join()

        stop_thread.join()

    # Attributes
    @property
    def network(self):
        return self.__network

    @property
    def actions(self):
        return self.__actions

    @property
    def behavior(self):
        return self.__behavior

    @property
    def started(self):
        return self.__started

    def stop(self):
        report = self.to_json()
        with open('agent-report.json', 'w') as f:
            json.dump(report, f, indent='\t')

        list_actions = {'timestamp': [], 'command': [], 'parameters': []}
        for action in self.actions:
            list_actions['timestamp'] += [action.timestamp]
            list_actions['command'] += [action.name]
            list_actions['parameters'] += [action.parameters]

        df = pd.DataFrame(data=list_actions)
        with open('actions.csv', 'w') as f:
            df.to_csv(path_or_buf=f, sep=',', index=False, columns=list(list_actions.keys()))
