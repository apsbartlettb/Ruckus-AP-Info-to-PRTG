import requests
import json
from dotenv import load_dotenv
import os
import urllib3
urllib3.disable_warnings()

load_dotenv()

# "https://0.0.0.0:8443/wsg/api/public/v11_1"
api_base_url = os.getenv("API_URL_BASE")

serviceTicket = ""
st_file = "serviceTicket.txt"

apsZoneUID = ""
    
def api_login():
    global serviceTicket
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "serviceTicket": serviceTicket
    }
    body = {
        # Must be admin account on Ruckus zd 144
        "username": os.getenv("API_USERNAME"),
        "password": os.getenv("API_PASSWORD")
    }
    try:
        response = requests.post(f"{api_base_url}/serviceTicket", headers=headers, json=body, verify=False)

        if response.status_code == 200:
            data = response.json()
            serviceTicket = data['serviceTicket']
            return True
        else:
            # Not logged in
            return False
    except:
        return False

def api_logoff():
    global serviceTicket
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "serviceTicket": serviceTicket
    }
    uri_params = {
        "serviceTicket": serviceTicket
    }
    response = requests.delete(f"{api_base_url}/serviceTicket", headers=headers, params=uri_params, verify=False)
    # Could write some code here to return a prtg error proper

def get_rkzones():
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    try:
        uri_params = {
            "serviceTicket": serviceTicket
        }
        response = requests.get(f"{api_base_url}/rkszones", headers=headers, params=uri_params, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return False
    except:
        return False

def ap_query():
    full_list = []
    current_page = 1

    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }

    while True:
        try:
            uri_params = {
                "serviceTicket": serviceTicket
            }
            body = {
                "filters": [
                    {
                        "type": "ZONE",
                        "value": apsZoneUID,
                        "operator": "eq"
                    }
                ],
                "page": current_page,
                "limit": 50
            }
            response = requests.post(f"{api_base_url}/query/ap", headers=headers, params=uri_params, data=json.dumps(body), verify=False)
            resp_json = response.json()
            full_list.extend(resp_json['list'])
            more = resp_json['hasMore']

            if more == True:
                current_page += 1
            else:
                break
        except:
            break

    return full_list

success = api_login()

final_json = {
    "prtg": {
        "result": [

        ]
    }
}
if success == True:
    zones = get_rkzones()
    for zone in zones['list']:
        if zone['name'] == "APS-Zone":
            apsZoneUID = zone['id']
    
    ap_query_response = ap_query()

    for device in ap_query_response:
        result_dict = {
                    "channel": f"{device['deviceName']} 5Ghz Airtime",
                    "value": device['airtime5G'],
                    "unit": "Percent",
                    "Mode": "Absolute"
                }
        
        final_json['prtg']['result'].append(result_dict)
    print(json.dumps(final_json))

api_logoff()