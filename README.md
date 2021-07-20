# gen-agent
Multi agent system for generating user behavior in network enabled machines

# Configuration
To configure the agent you must use the JSON files in the `conf/` folder.

The main configuration file is named `conf.json` and contains the following parameters :

```json
{
	"network": {
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
        },
	"experiment": {
		"start_date": "2021-07-08 16:00",
		"end_date": "2021-07-09 23:59"
	}
}
```

The behavioral bias are defined in files named as you wish, you can find exemples of these files in the `conf/` folder.

## Breakdown of the main configuration file

The main configuration file is split in 2 parts, the network part defining the work environment of the agent, and the experiment part defining parameters of the experiment like the start and end of the experiment.

### Network part

- vms : Defines the machines with whom the agent will be able to communicate during the experiment
    - services : Defines the list of services the machine hosts. The services in this list must be described in the subsequent `services` section
    - ip : The IP address of the machine, it is used when a service of the machine uses a parameter containing `&ip` which is a placeholder for the IP of the target machine
- ip : The IP of the agent, it is used to name it in its report file produced at the end of the experiment
- max_actions : Defines the number of actions you want the agent to be able to do at a maximum
- behavior : The name of the behavioral bias file you want the agent to use. For example, the `passenger` value will use the configuration file `conf/passenger.json`
- services : The list of available services and how to use them for the experiment
    - name : The name of the service
    - commands : The list of commands the agent will be able to use to execute actions on the service
        - name : The name of the command
        - parameters : A list of string parameters that can be used with the command for the defined service
        - errors : A list of string keywords contained in error messages returned by the command. This allows the agent to know if a command has failed so it can try something else if it does fail

### Experiment part

- start_date : The date and time at which your experiment is supposed to start. The agent can be started before this date, it will wait for the defined start to execute its firt actions
- end_date : The date and time at which your experiment is supposed to end. The agent will stop before doing anything if you try to start it after that date

The format used for the start and end date is `YYYY-MM-DD HH:MM`

## Breakdown of the behavioral bias configuration file format

The behavioral bias configuration file is a rather simple format where you only describe what you want to use.
Here is an exemple of a time block from `conf/passenger.json` : 

```json
{
  "10:00-12:00": {
    "web": {
      "bias": 0.59,
      "combo_max": 10,
      "wait_time": 30
    },
    "mail": {
      "bias": 0.1,
      "combo_max": 1,
      "wait_time": 1
    },
    "social": {
      "bias": 0.25,
      "combo_max": 10,
      "wait_time": 10
    },
    "games": {
      "bias": 0.05,
      "combo_max": 50,
      "wait_time": 1
    },
    "technical": {
      "bias": 0.01,
      "combo_max": 1,
      "wait_time": 10
    }
  }
}
```

We see here everything comprised in this declarative format :
- 10:00-12:00 : The time interval in which the bias is valid, any time interval of the day not declared is considered a non active time (no actions will be executed during the non declared intervals)
    - web : The name of the service for which the bias is applicable
        - bias : The bias you want for this service, this value must be between 0 and 1 but the total between all services can be more than 1
        - combo_max : The maximum number of consecutive actions on the same service
        - wait_time : The minimum time to wait between 2 consecutive actions on the same service

Note that you can declare, in the behavioral bias configuration, services that are not declared in the main configuration file. The services that are not declared in the main configuration file will simply be omitted.

You can also not declare some services in the behavioral bias configuration file, they will be considered as a bias of 0.