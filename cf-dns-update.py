# -*- coding: utf-8 -*-

"""
Dynamic DNS record update utility for CloudFlare DNS service.
(c) Dung Nguyen (nhymxu)
"""

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from configparser import ConfigParser
from os import path


CF_API_TOKEN = ''
IS_DRYRUN = False


def make_request(method="GET", url="", request_body=None):
    """
    Send API request ( json type )

    :param method:
    :param url:
    :param request_body:
    :return:
    """
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

    '''
    Other domain can using to get IP:
    ifconfig.me
    icanhazip.com
    ipecho.net/plain
    ifconfig.co
    '''
    endpoint = "https://checkip.amazonaws.com/"

    return make_request(url=endpoint).strip().decode('utf-8')


def get_old_ip():
    """
    Get old public IP if exist

    :return:
    """
    old_ip = None

    if path.exists("old_ip.txt"):
        with open('old_ip.txt', 'r') as fp:
            old_ip = fp.read().strip()

    return old_ip


def save_old_ip(ip):
    """
    Write current public IP to file

    :param ip:
    :return:
    """
    with open('old_ip.txt', 'w+') as fp:
        fp.write(ip)


def get_record_id(zone_id, record_name):
    """
    Get CloudFlare record id from domain/sub-domain name

    :param zone_id:
    :param record_name:
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


def update_host(zone_id, record_name, public_ip):
    """
    Update host to CloudFlare

    :param zone_id:
    :param record_name:
    :param public_ip:
    :return:
    """
    record_id = get_record_id(zone_id, record_name)

    if not record_id:
        print("Record not found")
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


def get_config(config_path='config.ini'):
    """
    Read and parsing config from ini file.
    Set global var CF_API_TOKEN

    :return:
    """
    global CF_API_TOKEN

    if not path.exists(config_path):
        raise RuntimeError("config file not found")

    config = ConfigParser()
    config.read(config_path)

    if "common" not in config:
        raise Exception("Common config not found.")

    if "CF_API_TOKEN" not in config['common'] or not config['common']['CF_API_TOKEN']:
        raise Exception("Missing CloudFlare API Token on config file")

    CF_API_TOKEN = config['common']['CF_API_TOKEN']

    config_sections = config.sections()
    config_sections.remove("common")

    if not config_sections:
        raise Exception("Empty site to update DNS")

    return config, config_sections


def process_section(section_data, public_ip):
    """
    Process all record in section

    :param section_data:
    :param public_ip:
    :return:
    """
    base_domain = section_data["base_domain"].strip()
    record_list = section_data["records"].strip().split("|")

    for record in record_list:
        record = record.strip()
        dns_record = base_domain
        if record != '@':
            dns_record = "{}.{}".format(record, base_domain)

        if IS_DRYRUN:
            print("[DRY RUN] Update record `{}` in zone id `{}`".format(dns_record, section_data['zone_id']))
            continue

        update_host(section_data['zone_id'], dns_record, public_ip)


def main(args):
    """
    Argument from input

    :param args:
    :return:
    """
    config, config_sections = get_config(config_path=args.config)

    public_ip = get_local_ip()
    print("")
    print("--- Public IP: {}".format(public_ip))
    if not IS_DRYRUN and public_ip == get_old_ip():
        print("Skip update")
        exit()

    for section in config_sections:
        print("")
        print("--- Updating {} ---".format(section))

        if "base_domain" not in config[section] or not config[section]["base_domain"]:
            print("Not found `base_domain` config on section `{}`".format(section))
            continue

        if "records" not in config[section] or not config[section]["records"]:
            print("Not found `records` config on section `{}`".format(section))
            continue

        process_section(section_data=config[section], public_ip=public_ip)

    if not IS_DRYRUN:
        print("Save old IP")
        save_old_ip(public_ip)


if __name__ == "__main__":
    nx_parser = argparse.ArgumentParser(
        prog='cf-dns-update',
        usage='%(prog)s [options] --config config_path',
        description='Dynamic DNS record update utility for CloudFlare DNS service.'
    )
    nx_parser.add_argument('--config', action='store', type=str, default='config.ini')
    nx_parser.add_argument('--dryrun', '--check', action='store_true')

    input_args = nx_parser.parse_args()

    IS_DRYRUN = input_args.dryrun

    main(args=input_args)
