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
            co = command.Command(c['name'], c['errors'])
            for p in c['parameters']:
                co.add_parameter(p)
            tmp.add_command(co)

        services.add(tmp)
    conf['network']['services'] = services

    vms = list()
    for v in conf['network']['vms']:
        tmp = vm.Vm(v['ip'])
        for s in v['services']:
            for srv in services:
                if s in srv.name:
                    tmp.add_service(srv)
        vms += [tmp]
    conf['network']['vms'] = vms

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
            "vms": [
                {"services": ["web", "mail", "social", "games", "technical"], "ip": "?"}
            ],
            "ip": "?",
            "max_actions": 5000,
            "behavior": "passenger",
            "services": [
                {
                    "name": "web",
                    "commands": [
                        {"name": "curl", "parameters": ["https://www.google.fr", "https://slashdot.org", "https://news.google.com"], "errors": []}
                    ]
                },
                {
                    "name": "mail",
                    "commands": [
                        {"name": "powershell", "parameters": ["& \"\"conf\\mail.ps1\"\""], "errors": []}
                    ]
                },
                {
                    "name": "social",
                    "commands": [
                        {"name": "curl", "parameters": ["https://www.facebook.com", "https://twitter.com", "https://www.youtube.com"], "errors": []}
                    ]
                },
                {
                    "name": "games",
                    "commands": [
                        {"name": "curl", "parameters": ["https://www.newgrounds.com", "https://www.absolu-flash.fr"], "errors": []}
                    ]
                },
                {
                    "name": "technical",
                    "commands": [
                        {"name": "curl", "parameters": ["https://stackoverflow.com", "https://wiki.archlinux.org", "https://docs.microsoft.com"], "errors": []}
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
