#!/usr/bin/env python3

import json
import math
import os
import time
import traceback
import subprocess
import sys

def log(msg):
    print(msg, flush=True)

def bytes_to_json(byte_str):
    return json.loads(byte_str.decode('utf8').replace("'", '"'))

def to_line(d):
    output = ''
    for key, value in d.items():
        output += key + '=' + str(value) + ','
    return output[:-1]

def mbps(bw):
    return bw / 125000

def get_measurement():
    return 'speedtest'

def as_str(val):
    val = str(val)
    val = val.replace(' ', '')
    val = val.replace(',', '')
    return '"' + val + '"'

def get_tags(r):
    tags = {'isp': as_str(r['isp']),
            'result_id': as_str(r['result']['id']),
            'server_country': as_str(r['server']['country']),
            'server_host': as_str(r['server']['host']),
            'server_ip': as_str(r['server']['ip']),
            'server_location': as_str(r['server']['location']),
            'server_name': as_str(r['server']['name'])}
    return to_line(tags)

def get_fields(r):
    fields = {'ping_latency_ms': r['ping']['latency'],
              'ping_jitter_ms': r['ping']['jitter'],
              'download_mbps': mbps(r['download']['bandwidth']),
              'upload_mbps': mbps(r['upload']['bandwidth'])}
    return to_line(fields)

def get_line(results):
    line = get_measurement() + ','
    line += get_tags(results) + ' '
    line += get_fields(results)
    return line

def get_host():
    return os.environ['INFLUXDB_HTTP']

def write_to_influx(line):
    url = get_host() + '/write?db=speedtest'
    cmd = ['curl', '-i', '-XPOST', url, '--data-binary', line]
    log('Running command:')
    log(cmd)
    return subprocess.check_output(cmd)

def create_influx_db():
    url = get_host() + '/query'
    cmd = ['curl', '-G', url, '--data-urlencode', 'q=CREATE DATABASE speedtest']
    log('Running command:')
    log(cmd)
    return subprocess.check_output(cmd)

def run_speedtest():
    cmd = ['speedtest', '-p', 'no', '-f', 'json-pretty', '--accept-license', '--accept-gdpr']
    output = subprocess.check_output(cmd)
    log('Processing result...')
    result = bytes_to_json(output)
    return get_line(result)

def main():
    log('Initializing DB...')
    db_result = create_influx_db()
    log(db_result)
    while True:
        log('Running speedtest...')
        try:
            line = run_speedtest()
            write_result = write_to_influx(line)
            log(write_result)
        except Exception as e:
            log('ERROR:')
            log(e)
        time.sleep(5)

main()
