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
    widgets = [
        {
            "id": 0,
            "definition": {
                "type": "query_value",
                "requests": [
                    {
                        "q": "sum:postgresql.rows_fetched{*} \
                        / ( sum:postgresql.rows_fetched{*} \
                        + sum:postgresql.rows_returned{*} ) * 100",
                        "aggregator": "avg"
                    }
                ],
                "title": "Rows fetched / returned",
                "title_size": "16",
                "title_align": "left",
                "time": {
                    "live_span": "1h"
                },
                "autoscale": True,
                "custom_unit": "%",
                "precision": 1
            },
            "layout": {
                "x": 2,
                "y": 1,
                "width": 22,
                "height": 15
            }
        },
        {
            "id": 1,
            "definition": {
                "type": "query_value",
                "requests": [
                    {
                        "q": "max:postgresql.percent_usage_connections{*}*100",
                        "aggregator": "last",
                        "conditional_formats": [
                            {
                                "comparator": ">",
                                "value": 75,
                                "palette": "red_on_white"
                            },
                            {
                                "comparator": ">",
                                "value": 50,
                                "palette": "yellow_on_white"
                            },
                            {
                                "comparator": "<=",
                                "value": 50,
                                "palette": "green_on_white"
                            }
                        ]
                    }
                ],
                "title": "Max connections in use",
                "title_size": "16",
                "title_align": "left",
                "time": {
                    "live_span": "1h"
                },
                "autoscale": True,
                "custom_unit": "%",
                "precision": 0
            },
            "layout": {
                "x": 25,
                "y": 1,
                "width": 23,
                "height": 15
            }
        },
        {
            "id": 2,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "avg:postgresql.rows_fetched{*}"
                    },
                    {
                        "q": "avg:postgresql.rows_returned{*}"
                    },
                    {
                        "q": "avg:postgresql.rows_inserted{*}"
                    },
                    {
                        "q": "avg:postgresql.rows_updated{*}"
                    }
                ],
                "title": "Rows fetched / returned / inserted / updated (per sec)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 1,
                "y": 17,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 3,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "avg:postgresql.connections{*} by {db}"
                    }
                ],
                "title": "Connections",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 49,
                "y": 1,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 4,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "postgresql.rows_inserted{*}, \
                        postgresql.rows_deleted{*}, \
                        postgresql.rows_updated{*}"
                    }
                ],
                "title": "Inserts / updates / deletes (per sec)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 49,
                "y": 17,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 5,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "avg:system.io.util{*}"
                    }
                ],
                "title": "Disk utilization (%)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 1,
                "y": 33,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 6,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "avg:system.load.1{*}",
                        "display_type": "area",
                        "style": {
                            "palette": "dog_classic",
                            "line_type": "solid",
                            "line_width": "normal"
                        }
                    },
                    {
                        "q": "avg:system.load.5{*}",
                        "display_type": "area",
                        "style": {
                            "palette": "dog_classic",
                            "line_type": "solid",
                            "line_width": "normal"
                        }
                    },
                    {
                        "q": "avg:system.load.15{*}",
                        "display_type": "area",
                        "style": {
                            "palette": "dog_classic",
                            "line_type": "solid",
                            "line_width": "normal"
                        }
                    }
                ],
                "title": "System load",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 49,
                "y": 33,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 7,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "avg:system.cpu.idle{*}, \
                        avg:system.cpu.system{*}, \
                        avg:system.cpu.iowait{*}, \
                        avg:system.cpu.user{*}, \
                        avg:system.cpu.stolen{*}, \
                        avg:system.cpu.guest{*}",
                        "display_type": "area",
                        "style": {
                            "palette": "cool",
                            "line_type": "solid",
                            "line_width": "normal"
                        }
                    }
                ],
                "title": "CPU usage (%)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 1,
                "y": 65,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 8,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "max:system.cpu.iowait{*}"
                        }
                ],
                "title": "I/O wait (%)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 1,
                "y": 49,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 9,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "sum:system.mem.usable{*}, sum:system.mem.total{*}-sum:system.mem.usable{*}",
                        "display_type": "area",
                        "style": {
                            "palette": "cool",
                            "line_type": "solid",
                            "line_width": "normal"
                        }
                    }
                ],
                "title": "System memory",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 49,
                "y": 65,
                "width": 47,
                "height": 15
            }
        },
        {
            "id": 10,
            "definition": {
                "type": "timeseries",
                "requests": [
                    {
                        "q": "sum:system.net.bytes_rcvd{*}"
                    },
                    {
                        "q": "sum:system.net.bytes_sent{*}"
                    }
                ],
                "title": "Network traffic (per sec)",
                "title_size": "16",
                "title_align": "left",
                "show_legend": False,
                "legend_size": "0"
            },
            "layout": {
                "x": 49,
                "y": 49,
                "width": 47,
                "height": 15
            }
        }
    ]

    # free = screenboard, ordered = timeboard
    layout_type = 'free'
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
