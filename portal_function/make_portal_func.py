from datadog import initialize, api
import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging


# connect to datadog
def init():
    # get .env variables
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # logging
    logging.basicConfig(filename='make_portal_health_checks.log',level=logging.DEBUG)

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

    portal_location = os.environ.get("portal_location")

    # loop through existing-portal.txt to find all portals

    # can be used to check if monitor exists:
    #       api.Monitor.get_all()

    # create a monitor for each portal
    with open(portal_location, 'r') as f:
        for portal in f:
            Portal_C = portal.capitalize()
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

            tags = [
                "portal"
            ],
            # creating monitor
            api.Monitor.create(
                type="service check",
                query="\"http.can_connect\".over(\"instance:{0}\",\"url:https://{0}.kwikeelabs.com/config/\").by(\"url\").last(3).count_by_status()".format(portal),
                name="{0}".format(Portal_C),
                message="Check {0} endpoint.".format(Portal_C),
                tags=tags,
                options=monitor_options
            )
        f.close


## create dashboard to display portal monitor summary
def make_portal_dashboard():
    # initialize access to datadog
    init()


    # set variables for creating the dashboard
    title = 'Portals - Demo'
    widgets = [{
        "definition":{
            "type":"manage_status",
            "summary_type":"monitors",
            "query":"","sort":"status,asc",
            "count":50,
            "start":0,
            "display_format":"countsAndList",
            "color_preference":"text",
            "hide_zero_counts":True,
            "title":"Portal Endpoint",
            "title_size":"13",
            "title_align":"left"
        },
        "layout":{
            "x":8,
            "y":2,
            "width":87,
            "height":60
        }
    }]
    layout_type = 'free'
    description = 'A dashboard with BP info.'
    is_read_only = False
    notify_list = []
    template_variables = []

    # get all dashboard to see if this dashboard already exists
    # if not, then create dashboard
    if [True for i in api.Dashboard.get_all()['dashboards']
            if i['title'] == title]:
        logging.info('Dashboard already exists')
    else:
        logging.info('Creating dashboard')
        api.Dashboard.create(title=title,
                             widgets=widgets,
                             layout_type=layout_type,
                             description=description,
                             is_read_only=is_read_only,
                             notify_list=notify_list,
                             template_variables=template_variables)

make_portal_dashboard()
