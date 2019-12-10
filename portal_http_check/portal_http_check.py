import os
import json
import logging
import copy
import yaml

### READ BEFORE RUNNING ###
# 1) You must have the azure cli for kubernetes installed on your laptop.
# 2) You must have deploy.yaml and map.yaml in this folder.  
# 3) A log file and some text files will be generated 
# during the run so be prepared for that. 
# 4) You need to have a file called existing-portals.txt 
# that contains the portals already being checked.
### END ###

def main():
    if os.path.exists('portal_http_check.log'):
            os.remove('portal_http_check.log')
    logging.basicConfig(filename='portal_http_check.log',level=logging.DEBUG)

    # replace the strings below with env variables
    instance_string = "\n  - name: 'k8es-xxx'\n    url: 'https://xxx.kwikeelabs.com/config/'\n    content_match: 'header-copy'\n    headers: {'x-purge-cache': 'true'}\n"

    # replace this 
    try:
        logging.info("Trying: Azure Log In.")
        os.system("az login --service-principal -u 514af15e-539b-48a5-a98e-802bfcb38049 -p 6G4bHajKx4D1bd9vHqUQIjBLWK3icTomTIP8Bdjq+LI= --tenant 8714a216-0445-4269-b96b-7d84bddb6da1")
        logging.info("Success: Logged into Azure.")
    except:
        logging.error('Failed: Azure Log In. Exiting.')
        return

    # this command can stay
    try:
        logging.info('Trying: List Portals')
        if os.path.exists('portals.txt'):
            os.remove('portals.txt')
        os.system("az aks list --query '[?(tags.adopter)].{Name:name,Environment:tags.adopter}' >> portals.txt")
        logging.info('Sucess: Portals List in portals.txt')
    except:
        logging.error('Failed: List Portals. Exiting.')
        return
    
    try:
        logging.info('Trying: Loading portals.txt as JSON')
        with open('portals.txt', 'r') as f:
            datastore = json.load(f)
            f.close()
        logging.info('Success: Loaded portals.txt as JSON')
    except:
        logging.error('Failed: Loading portals.txt as JSON. Exiting.')
        return
    
    try:
        logging.info('Trying: Existing Health Checks?')
        if os.path.exists('existing-portals.txt'):
            with open('existing-portals.txt', 'r') as f:
                existing_portals = [current_place.rstrip() for current_place in f.readlines()]
                f.close()
            logging.info('Success: Existing Health Checks!')
        else:
            logging.info('Moving on: No existing Health Checks!')
            existing_portals = []
    except:
        logging.error('Failed: Unable to get existing Health Checks. Exiting.')
        return
    
    try:
        logging.info('Trying: Generate New Config String')
        with open('map.yaml', 'r') as f:
            yaml_object = yaml.load(f, Loader=yaml.FullLoader)
            existing_config = yaml_object['data']['http-config']
            new_portals = []
            for item in datastore:
                if (item['Environment'] not in existing_portals):
                    new_portals.append(item['Environment'])
                    new_portal_string = copy.deepcopy(instance_string)
                    new_portal_string = new_portal_string.replace('xxx', item['Environment'])
                    existing_config = existing_config + new_portal_string

            yaml_object['data']['http-config'] = existing_config
            f.close()
            logging.info('Success: Generated New Config String.')
    except:
        logging.error('Failed: Did not generate new string. Exiting.')
        return
    
    try:
        logging.info('Trying: Change map.yaml and existing-portals.txt')
        with open('map.yaml', 'w') as f:
            documents = yaml.dump(yaml_object, f)
            f.close()
        logging.info('Success: Changed map.yaml')

        with open('existing-portals.txt', 'a') as f:
            for item in new_portals:
                f.write(item)
                f.write('\n')
            f.close()
        logging.info('Success: Changed existing-portals.txt')

        if os.path.exists('portals.txt'):
            os.remove('portals.txt')
    except:
        logging.error('Failed: Did not change files. Exiting.')
        return
    
    try:
        logging.info('Trying: Switch kubectl context.')
        os.system('az aks get-credentials --resource-group kamino --name datadog-5')
        logging.info('Success: Switched kubectl context.')
    except:
        logging.error('Failed: Unable to switch kubectl context. Exiting.')
        return
    
    try:
        logging.info('Trying: Delete existing resources.')
        os.system('kubectl delete configmap dd-agent-config')
        logging.info('Success: Deleted configmap.')
        os.system('kubectl delete deploy datadog-agent')
        logging.info('Sucess: Deleted deploy')
    except:
        logging.error('Failed: Unable to delete resources. Attempting to reset.')
    
    try:
        logging.info('Trying: Recreate configmap')
        os.system('kubectl apply -f map.yaml')
        logging.info('Success: Configmap recreated.')

        logging.info('Trying: Recreate deploy')
        os.system('kubectl apply -f deploy.yaml')
        logging.info('Success: Deploy recreated.')
    except:
        logging.error('Failed: Unable to recreate kubectl resources') 

    

if __name__ == "__main__":
    main()
    



        
    
