import requests
import json
from dotenv import load_dotenv
import os
import urllib3
urllib3.disable_warnings()

load_dotenv()

api_base_url = os.getenv("API_URL_BASE")

serviceTicket = ""
st_file = "serviceTicket.txt"

# if os.path.exists(st_file):
#     with open(st_file, 'r') as file:
#         serviceTicket = file.read().strip()
#     # print(f"Loaded serviceTicket {serviceTicket} from {st_file}")

# controllerVersion = ""
apsZoneUID = ""
    
def api_login():
    global serviceTicket
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "serviceTicket": serviceTicket
    }
    body = {
        "username": os.getenv("API_USERNAME"),
        "password": os.getenv("API_PASSWORD")
    }
    try:

        response = requests.post(f"{api_base_url}/serviceTicket", headers=headers, json=body, verify=False)

        if response.status_code == 200:
            data = response.json()
            serviceTicket = data['serviceTicket']

            # with open(st_file, 'w') as file:
            #     file.write(serviceTicket)
            # # print(f"Wrote serviceTicket {serviceTicket} to {st_file}")
            # # print(f"Logged In")

            # # print("Login / ServiceTicket Response Data")
            # # print(data)
            return True
        else:
            # # print(f"Not Logged In")
            # # print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        # # print(f"An error occured {e}")
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

    if response.status_code == 200:
        pass
        # # print("Logged off successfully.")
        # # print(response)
    else:
        pass
        # # print("Logoff unsuccessful.")


def get_rkzones():
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    try:
        uri_params = {
            "serviceTicket": serviceTicket
        }
        # # print(f"params: {uri_params}")
        response = requests.get(f"{api_base_url}/rkszones", headers=headers, params=uri_params, verify=False)

        if response.status_code == 200:
            data = response.json()
            # # print("# printing Zones")
            # # print(data)
            return data
        else:
            # print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        # print(f"An error occured {e}")
        return False

def ap_query():

    full_list = []
    current_page = 1
    first_index = 0

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

            total_count = resp_json['totalCount']
            more = resp_json['hasMore']
            ret_first_index = resp_json['firstIndex']
            this_count = len(resp_json['list'])

            if more == True:
                current_page += 1
                # first_index += this_count
                # # print(resp_json)
                # print(f"We've got more to get. Onto page {current_page}!")
            else:
                # print(more)
                # print("All done!")
                break

        except Exception as ex:
            # print("Exception")
            # print(ex)
            break

    return full_list

success = api_login()
# # print(serviceTicket)

final_json = {
    "prtg": {
        "result": [

        ]
    }
}
if success == True:
    zones = get_rkzones()
    # # print(zones)
    for zone in zones['list']:
        if zone['name'] == "APS-Zone":
            apsZoneUID = zone['id']
            # print(f"Zone Found: {apsZoneUID}")
    
    ap_query_response = ap_query()

    for device in ap_query_response:
        # # print(f"{device['deviceName']}\t{device['ip']}\t{device['apMac']}.")
        result_dict = {
                    "channel": f"{device['deviceName']} 5Ghz Airtime",
                    "value": device['airtime5G'],
                    "unit": "Percent",
                    "Mode": "Absolute"
                }
        
        final_json['prtg']['result'].append(result_dict)
    print(json.dumps(final_json))

api_logoff()