#!/bin/bash

# Get a valid pull secret (json string) from
# You can get this secret from https://cloud.openshift.com/clusters/install#pull-secret
set +x
set -x

# Uncomment to build a copy of ironic or inspector locally
#export IRONIC_INSPECTOR_IMAGE=https://github.com/metalkube/metalkube-ironic-inspector
#export IRONIC_IMAGE=https://github.com/metalkube/metalkube-ironic
export PULL_SECRET='{"auths": {"cloud.openshift.com": {"auth": "XXX","email": "XXX"},"quay.io": {"auth": "XXX","email": "XXX"},"registry.svc.ci.openshift.org": {"auth": "XXX"}}}'
export PRO_IF="em1"
export INT_IF="em2"
export ROOT_DISK="/dev/sda"
export CLUSTER_NAME="summit"
export BASE_DOMAIN="kni.lab.redhat.com"
export MANAGE_BR_BRIDGE=n

export NODES_FILE="/root/dev-scripts/bm.json"
export NODES_PLATFORM=BM
export KAFKA_NAMESPACE="amq"
export UPSTREAM_NTP_SERVERS="clock.redhat.com"
export NTP_SERVERS="172.16.200.1"
