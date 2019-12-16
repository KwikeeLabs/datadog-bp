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

# create monitor for each portal
def make_portal_monitor():
    # initialize access to datadog
    init()

    # location of existing-portal.txt
    portal_location = os.environ.get("portal_location")

    # get all the existing monitor names:
    list = [i['name'] for i in api.Monitor.get_all()]
    counter = 1
    # the number of rows per widget
    widget_row_len = int(os.environ.get("widget_length"))

    # create a monitor for each portal
    with open(portal_location, 'r') as f:
        # get each portal name
        for portal in f:
            # strip portal name of extra space and capitalize
            Portal_C = portal.capitalize().strip()
            if Portal_C not in list:
                # setting variables for monitor
                monitor_options = {
                    "notify_audit": True,
                    "locked": False,
                    "timeout_h": 0,
                    "silenced": {},
                    "include_tags": True,
                    "thresholds": {
                        "critical": 2,
                        "ok": 2
                    },
                    "new_host_delay": 300,
                    "notify_no_data": True,
                    "renotify_interval": 360,
                    "escalation_message": "{0} is still down.".format(Portal_C),
                    "no_data_timeframe": 2
                }
                # portal for all portal related Monitors
                # section number increments depending on length set in .env
                tags = [
                    "portal",
                    "section:{0}".format(math.ceil(counter/widget_row_len))
                ]
                # creating monitor
                api.Monitor.create(
                    type="service check",
                    query="\"http.can_connect\".over(\"instance:k8es_{0}\",\"url:https://{0}.kwikeelabs.com/config/\").by(\"url\").last(3).count_by_status()".format(portal),
                    name="{0}".format(Portal_C),
                    message="Check {0} endpoint. @slack-SGSCO-datadog-test".format(Portal_C),
                    tags=tags,
                    options=monitor_options
                )
                counter += 1
            else:
                # do nothing if monitor already exists
                logging.info('Monitor {0} already exists'.format(Portal_C))
        f.close


## create dashboard to display portal monitor summary
def make_portal_dashboard():
    # initialize access to datadog
    init()

    # the number of rows per widget
    widget_row_len = int(os.environ.get("widget_length"))

    # set variables for creating the dashboard
    title = 'Portals - Demo'
    widgets = [{
        "id":0,
        "definition":{
            "type":"manage_status",
            "summary_type":"monitors",
            "query":"tag:(portal)",
            "sort":"status,asc",
            "count":50,
            "start":0,
            "display_format":"counts",
            "color_preference":"text",
            "hide_zero_counts":True,
            "title":"Portal Endpoints",
            "title_size":"13",
            "title_align":"center"
        },
        "layout":{
            "x":0,
            "y":1,
            "width":20,
            "height":10
        }
    }]
    # create a new widget for a certain number of monitors,
    # depending on widget_row_leng set in .env
    # increment id, x, y, tag
    m_len = len([i['name'] for i in api.Monitor.get_all()])
    counter = 0
    for x in range(1, math.ceil(m_len/widget_row_len)+1):
        widget_template ={
            "id":x,
            "definition":{
                "type":"manage_status",
                "summary_type":"monitors",
                "query":"tag:(section:{0})".format(x),
                "sort":"status,asc",
                "count":50,
                "start":0,
                "display_format":"list",
                "color_preference":"text",
                "hide_zero_counts":True
                },
            "layout":{
                "x":20+x+(x-1)*24,
                "y":1,
                "width":24,
                "height":60
            }
        }
        widgets.append(widget_template)
    # free = screenboard, ordered = timeboard
    layout_type = 'free'
    description = 'A dashboard with BP info.'
    # set to False to enable edit, else set to True
    is_read_only = False
    # include emails for notifying changes to the board
    notify_list = []
    # global variables to apply to all widgets
    template_variables = []

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
