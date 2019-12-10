import os
import json
import logging
import copy
import yaml
import os
from os.path import join, dirname
from dotenv import load_dotenv

import make_portal_func as portal_func

### READ BEFORE RUNNING ###
# 1) You must have the datadog-agent downloaded on your laptop.
# 2) Change the location of the config file below to where it is on your laptop.
# 3) A log file and some text files will be generated
# during the run so be prepared for that.
# 4) You need to have a file called existing-portals.txt
# that contains the portals already being checked
### END ###


def main():
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    if os.path.exists('make_portal_health_checks.log'):
            os.remove('make_portal_health_checks.log')
    logging.basicConfig(filename='make_portal_health_checks.log',level=logging.DEBUG)

    # replace the strings below with env variables
    url_string = 'https://xxx.kwikeelabs.com/config/'
    instance_entry = {'name': '', 'url': '', 'headers':
        {'x-purge-cache': 'true'}, 'method': 'get',
            'content_match': 'header-copy'}

    try:
        logging.info('Trying: Stopping the agent first')
        os.system('launchctl stop com.datadoghq.agent')
        logging.info('Success: System agent stopped')
    except:
        logging.error('Failed: Was unable to stop the agent.')


    # replace the commands below with an env variable
    try:
        logging.info('Trying: Logging in the user to Azure.')
        os.system('az login --service-principal -u {0} -p {1} --tenant {2}'.format(os.environ.get("azure_u"), os.environ.get("azure_p"), os.environ.get("azure_tenant")))
        logging.info('Success: User logged into Azure.')
    except:
        logging.error('Failed: User not able to login to Azure.')
        return

    try:
        logging.info('Trying: Getting list of portals')
        if os.path.exists('portals.txt'):
            os.remove('portals.txt')
        os.system("az aks list --query '[?(tags.adopter)].{Name:name,Environment:tags.adopter}' >> portals.txt")
        logging.info('Success: Got list of portals into portals.txt')
    except:
        logging.error('Failed: Not able to get list of portals.')
        return

    try:
        with open('portals.txt', 'r') as f:
            datastore = json.load(f)
            f.close()
    except:
        logging.error('Unable to create JSON Object from portals.txt')

    try:
        logging.info('Trying: Checking which portals already have health checks.')
        with open('existing-portals.txt', 'r') as f:
            existing_portals = [current_place.rstrip() for current_place in f.readlines()]
            f.close()
        logging.info('Success: Obtained existing health checks.')
    except:
        logging.error('Failed: Unable to get existing health checks')
        existing_portals = []

    try:
        logging.info('Trying: Modifying the http_check yaml file and the existing')
        # change this below to be the location of your config file
        config_location = os.environ.get("config_location")
        with open(config_location, 'r') as f:
            yaml_object = yaml.load(f, Loader=yaml.FullLoader)
            if (yaml_object['instances'] == None):
                yaml_object['instances'] = []
            new_portals = []
            for item in datastore:
                if (item['Environment'] not in existing_portals):
                    new_portals.append(item['Environment'])
                    new_portal_entry = copy.deepcopy(instance_entry)
                    new_portal_entry['name'] = item['Environment']
                    new_portal_string = copy.copy(url_string)
                    new_portal_string = new_portal_string.replace('xxx', item['Environment'])
                    new_portal_entry['url'] = new_portal_string
                    yaml_object['instances'].append(new_portal_entry)
            f.close()
        with open(config_location, 'w') as f:
            documents = yaml.dump(yaml_object, f)
            f.close()

        with open('existing-portals.txt', 'a') as f:
            for item in new_portals:
                f.write(item)
                f.write('\n')
            f.close()

        if os.path.exists('portals.txt'):
            os.remove('portals.txt')

        logging.info('Success: Amended both yaml and txt files')
    except:
        logging.error('Failed: Unable to amend files.')

    try:
        logging.info('Trying: Starting up the agent again')
        os.system('launchctl start com.datadoghq.agent')
        logging.info('Success: System agent started')
    except:
        logging.error('Failed: Was unable to start the agent.')

    try:
        logging.info('Trying: Create new monitors for each portal')
        portal_func.make_portal_monitor()
        logging.info('Success: Monitors created.')
    except:
        logging.error('Failed: Was unable to create new monitors')

    try:
        logging.info('Trying: Create new dashboard for http monitors')
        portal_func.make_portal_dashboard()
        logging.info('Success: dashboard created.')
    except:
        logging.error('Failed: Was unable to create new dashboard')


if __name__ == "__main__":
    main()
