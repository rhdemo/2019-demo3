#!/usr/bin/env python

import argparse
import os
from distutils.spawn import find_executable
import json
import sys

parser = argparse.ArgumentParser(description='Process ipmi json file.')
parser.add_argument('-a', '--action', help='Action to do on nodes', choices=('status', 'on', 'off'), default='status')
parser.add_argument('-f', '--inputfile', help='Path for ipmi file', default='rhhi_nodes_drac.json')
args = parser.parse_args()
inputfile = args.inputfile
action = args.action

if find_executable('ipmitool') is None:
    print("ipmitool not found")
    sys.exit(1)

if not os.path.exists(inputfile):
    print("input file %s not found" % inputfile)
    sys.exit(1)
with open(inputfile) as f:
    data = json.load(f)
    for node in data['nodes']:
        name = node['name']
        driver_info = node['driver_info']
        driver = node['driver']
        username = 'drac_username' if driver == 'idrac' else 'ipmi_username'
        password = 'drac_password' if driver == 'idrac' else 'ipmi_password'
        address = 'drac_address' if driver == 'idrac' else 'ipmi_address'
        username, password, address = driver_info[username], driver_info[password], driver_info[address]
        cmd = "ipmitool -H %s -U %s -P %s  -I lanplus power %s" % (address, username, password, action)
        result = os.popen(cmd).read()
        print("Checking %s: %s " % (name, result))
