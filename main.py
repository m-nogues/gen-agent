#!/usr/bin/python
import argparse
import json
import random
from datetime import datetime, timedelta

from src import agent
from src.model import command, service, vm, behavior


def convert_to_objects(conf):
    services = set()
    for s in conf['network']['services']:
        tmp = service.Service(s['name'])
        for c in s['commands']:
            co = command.Command(c['name'])
            for p in c['parameters']:
                co.add_parameter(p)
            tmp.add_command(co)

        services.add(tmp)
    conf['network']['services'] = services

    vms = set()
    for v in conf['network']['vms']:
        tmp = vm.Vm(v['ip'], v['behavior'])
        for s in v['services']:
            for srv in services:
                if s in srv.name:
                    v.add_service(srv)

    conf['experiment']['start_date'] = datetime.strptime(conf['experiment']['start_date'], '%Y-%m-%d %H:%M')
    conf['experiment']['end_date'] = datetime.strptime(conf['experiment']['end_date'], '%Y-%m-%d %H:%M')


def configure(config_file):
    """Read the configuration file or creates the default one if it does not exist.

    Arguments:
        config_file {string} -- The configuration file

    Returns:
        dict -- The dictionary containing the configuration
    """
    conf = {}
    try:
        with open(config_file, 'r') as f:
            conf = json.load(f)

    except OSError:
        conf['network'] = {
            'vms': [
                {'behavior': 'user', 'services': ['ftpd'], 'ip': '192.168.10.11'},
                {'behavior': 'server', 'services': ['sshd', 'ftpd', 'httpd'], 'ip': '192.168.10.12'},
                {'behavior': 'admin', 'services': ['sshd'], 'ip': '192.168.10.13'}
            ],
            'ip': '192.168.10.10',
            'max_actions': 5000,
            'behavior': 'user',
            'services': [
                {
                    'name': 'sshd',
                    'commands': [
                        {'name': '22', 'parameters': ['tester@&ip']},
                        {'name': 'sftp', 'parameters': ['tester@&ip']}
                    ]
                },
                {
                    'name': 'ftpd',
                    'commands': [
                        {'name': 'ftp', 'parameters': ['&ip']}
                    ]
                },
                {
                    'name': 'httpd',
                    'commands': [
                        {'name': 'wget', 'parameters': [
                            'http://&ip', '-r http://&ip']},
                        {'name': 'curl', 'parameters': ['http://&ip']}
                    ]
                }
            ]
        }
        conf['experiment'] = {
            'start_date': (datetime.now() + timedelta(1)).strftime('%Y-%m-%d %H:%M'),
            'end_date': (datetime.now() + timedelta(8)).strftime('%Y-%m-%d %H:%M')
        }

        with open(config_file, 'w') as f:
            json.dump(conf, f, indent='\t')

    convert_to_objects(conf)
    return conf


def main(file):
    conf = configure(file)

    agt = agent.Agent(conf['network']['ip'], conf['network']['behavior'], conf['network']['services'],
                      conf['network']['vms'])

    max_actions = conf['network']['max_actions']
    agt.start(random.randrange(int(max_actions / 2), max_actions), conf['experiment']['start_date'],
              conf['experiment']['end_date'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Python framework for an easy creation of a network model for scientific pcap creation.')
    parser.add_argument('-c', '--conf', nargs='?', default='conf/config.json',
                        help='specify an alternative configuration file')

    args = parser.parse_args()

    main(args.conf)
