from datadog import initialize, api
import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging
import math


# connect to datadog
def init():
    # get .env variables
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # logging
    #logging.basicConfig(filename='make_portal_health_checks.log',level=logging.DEBUG)

    # set keys for datadog access
    options = {
        'api_key': os.environ.get("api_key"),
        'app_key': os.environ.get("app_key")
    }

    initialize(**options)


# create dashboard to display portal monitor summary
def make_psql_dashboard():
    # initialize access to datadog
    init()

    # set variables for creating the dashboard
    title = 'PostgreSQL - Demo'
    widgets = [{
            "id":0,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"avg:postgresql.rows_fetched{$scope}"
                    },
                    {
                        "q":"avg:postgresql.rows_returned{$scope}"
                    },
                    {
                        "q":"avg:postgresql.rows_inserted{$scope}"
                    },
                    {
                        "q":"avg:postgresql.rows_updated{$scope}"
                    }
                ],
                "title":"Rows fetched / returned / inserted / updated (per sec)",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":1,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"avg:postgresql.connections{$scope} by {db}"
                    }
                ],
                "title":"Connections",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":2,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"postgresql.rows_inserted{$scope},\
                        postgresql.rows_deleted{$scope}, \
                        postgresql.rows_updated{$scope}"
                    }
                ],
                "title":"Inserts / updates / deletes (per sec)",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":3,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"avg:system.io.util{$scope}"
                    }
                ],
                "title":"Disk utilization (%)",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":4,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"system.load.1{$scope}"
                    },
                    {
                        "q":"system.load.5{$scope}"
                    },
                    {
                        "q":"system.load.15{$scope}"
                    }
                ],
                "title":"System load",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":5,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"system.cpu.idle{$scope},\
                        system.cpu.system{$scope},\
                        system.cpu.iowait{$scope},\
                        system.cpu.user{$scope},\
                        system.cpu.stolen{$scope},\
                        system.cpu.guest{$scope}"
                    }
                ],
                "title":"CPU usage (%)",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":6,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"max:system.cpu.iowait{$scope}"
                    }
                ],
            "title":"I/O wait (%)",
            "show_legend":False,
            "legend_size":"0"}},
        {
            "id":7,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"sum:system.mem.usable{$scope},\
                        sum:system.mem.total{$scope}-sum:system.mem.usable{$scope}"
                    }
                ],
                "title":"System memory",
                "show_legend":False,
                "legend_size":"0"
            }
        },
        {
            "id":8,
            "definition":{
                "type":"timeseries",
                "requests":[
                    {
                        "q":"sum:system.net.bytes_rcvd{$scope}"
                    },
                    {
                        "q":"sum:system.net.bytes_sent{$scope}"
                    }
                ],
                "title":"Network traffic (per sec)",
                "show_legend":False,
                "legend_size":"0"
            }
        }
    ]

    # free = screenboard, ordered = timeboard
    layout_type = 'ordered'
    description = 'A dashboard with PostgreSQL info.'
    # set to False to enable edit, else set to True
    is_read_only = False
    # include emails for notifying changes to the board
    notify_list = ['@slack-SGSCO-datadog']
    # global variables to apply to all widgets
    template_variables = [{"name":"scope","default":"*","prefix":None}]

    # get all dashboard to see if this dashboard already exists
    # if it exists, update the dashboard, else, create new dashboard,
    dashboard_id = False
    ## later, we can create a rule for duplicates, if ever needed
    for i in api.Dashboard.get_all()['dashboards']:
        if i['title'] == title:
            # if there are duplicates, will update the last
            dashboard_id = i['id']
    if dashboard_id:
        # if the dashboard already exists, update regardless of anything else
        logging.info('Dashboard already exists, updating dashboard')
        api.Dashboard.update(dashboard_id,
                     title=title,
                     widgets=widgets,
                     layout_type=layout_type,
                     description=description,
                     is_read_only=is_read_only,
                     notify_list=notify_list,
                     template_variables=template_variables)
    else:
        # create new dashboard
        logging.info('Creating dashboard')
        api.Dashboard.create(title=title,
                             widgets=widgets,
                             layout_type=layout_type,
                             description=description,
                             is_read_only=is_read_only,
                             notify_list=notify_list,
                             template_variables=template_variables)
make_psql_dashboard()
