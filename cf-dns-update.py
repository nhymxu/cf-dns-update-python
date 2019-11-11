import configparser
import json
import urllib.error
import urllib.parse
import urllib.request
from os import path


def make_request(method="GET", url="", request_body=None):
    headers = {
        'Authorization': "Bearer {}".format(CF_API_TOKEN),
        'Content-Type': 'application/json'
    }

    data = None
    if request_body:
        # data = urllib.parse.urlencode(request_body)
        data = request_body.encode('ascii')

    try:
        req = urllib.request.Request(url, headers=headers, data=data, method=method)
        with urllib.request.urlopen(req) as response:
            resp_content = response.read()
            return resp_content
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
    except urllib.error.URLError as e:
        print(e.reason)

    return False


def get_local_ip():
    """
    Get current public IP of server
    :return: string
    """
    endpoint = "https://checkip.amazonaws.com/"

    return make_request(url=endpoint).strip().decode('utf-8')


def get_old_ip():
    """

    :return:
    """
    old_ip = None

    if path.exists("old_ip.txt"):
        with open('old_ip.txt', 'r') as fp:
            old_ip = fp.read().strip()

    return old_ip


def save_old_ip(ip):
    with open('old_ip.txt', 'w+') as fp:
        fp.write(ip)


def get_record_id(zone_id, record_name):
    """
    Get CloudFlare record id from domain/sub-domain name
    :return:
    """
    endpoint = "https://api.cloudflare.com/client/v4/zones/{}/dns_records?name={}&type=A".format(
        zone_id,
        record_name
    )
    response = make_request("GET", endpoint)
    data = json.loads(response)
    if not data['success']:
        return False

    for record in data['result']:
        if record['name'] == record_name:
            return record['id']

    return False


def update_host(zone_id, record_name):
    record_id = get_record_id(zone_id, record_name)

    if not record_id:
        return False

    endpoint = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(
        zone_id,
        record_id
    )

    payload = {
        "type": "A",
        "name": record_name,
        "content": public_ip
    }

    response = make_request(
        method="PUT",
        url=endpoint,
        request_body=json.dumps(payload)
    )
    data = json.loads(response)

    if not data['success']:
        print("Failed to update {}:{}".format(record_name, public_ip))
        return False

    print("Success update {}:{}".format(record_name, public_ip))

    return True


config_file = 'config.ini'

if not path.exists(config_file):
    raise RuntimeError("config file not found")

config = configparser.ConfigParser()
config.read(config_file)

if "common" not in config:
    raise Exception("Common config not found.")

if "CF_API_TOKEN" not in config['common'] or not config['common']['CF_API_TOKEN']:
    raise Exception("Missing CloudFlare API Token on config file")

CF_API_TOKEN = config['common']['CF_API_TOKEN']

config_sections = config.sections()
config_sections.remove("common")

if not config_sections:
    raise Exception("Empty site to update DNS")

public_ip = get_local_ip()
print("Public IP: {}".format(public_ip))
if public_ip == get_old_ip():
    print("Skip update")
    exit()

for domain in config_sections:
    print("--- Updating {} ---".format(domain))
    update_host(config[domain]['zone_id'], config[domain]['record'])

print("Save old IP")
save_old_ip(public_ip)
