import configparser
import json
import urllib.error
import urllib.parse
import urllib.request


def make_request(method="GET", url="", request_body=None):
    headers = {
        'Authorization': "Bearer {}".format(CF_API_TOKEN),
        'Content-Type': 'application/json'
    }

    data = urllib.parse.urlencode(request_body)
    data = data.encode('ascii')

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
    pass


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

    body = '{"type":"A","name":"$2","content":"$ip"}'

    make_request("PUT", endpoint, body)


config_file = 'config.ini'

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


for domain in config_sections:
    update_host(domain['zone_id'], domain['record'])