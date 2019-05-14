This repository provides information on the summit demo3 from 2019 that can be watched [here](https://youtu.be/jB9MnMTmMZw?t=4327)

It contains steps to deploy metalkube and a number of demo workloads.

One node is used as helper node to run the deployment.

## Workload Description

- authentication using a dedicated admin user.
- dotnet project with a mssqlserver pod.
- kafka. relies on ceph beeing deployed previously.
- nfs to be used for the windows vm. By default, it requires access to internal network to gather the windows vm although an alternative image can be indicated
- a windows vm connected through the brext bridges of the nodes.
- knative deployment.
- tweeting service using knative.
- uhc modifications so that the cluster shows as baremetal and with a given location at cloud.redhat.com.

## Base requirements

You will need to gather:
- ipmi information for your nodes and put in a [bm.json](bm.json) file. Use the helper script [ipmi.py](helpers/ipmi.py) to validate correct syntax and that credentials are valid.
- a valid pull secret. To reproduce summit demo versions, it will need to be valid for at least for registry.svc.ci.openshift.org, and optionally containing additional credentials for cloud.openshift.com (needed for uhc).
- generate a full [config_root.sh](config_root.sh).
- decide a CLUSTER_NAME name.
- decide a BASE_DOMAIN name.

You also need your baremetal nodes to have two interfaces, one dedicated for provisioning and the other one for public access.

## DNS requirements

for summit demo, we used a dedicated vm running on the helper node with dnsmasq server but in general, one needs the following DNS entries to be resolvable:

- api.$CLUSTER_NAME.$BASE_DOMAIN
- ns1.$CLUSTER_NAME.$BASE_DOMAIN

Additionally, if the nodes are not named master-0, master-1,..., the script `fix_ep.sh` will need to be called in the middle of the deployment process

## Metalkube Master Deployment

the following commands can be used to reproduce the same exact environment as the one used for demo.

Alternatively, follow upstream documentation to deploy kni using a more updated version.

The remainder of this section assumes you want to reproduce summit exact versions

```
yum -y install git screen bridge-utils net-tools
echo export KUBECONFIG=$HOME/dev-scripts/ocp/auth/kubeconfig >> ~/.bashrc
echo export GOPATH=$HOME/go >> ~/.bashrc
echo export PATH=\$GOPATH/bin:\$PATH >> ~/.bashrc
echo export OS_TOKEN=fake-token >> ~/.bashrc
echo export OS_URL=http://localhost:6385 >> ~/.bashrc
git clone https://github.com/openshift-metalkube/dev-scripts
git checkout 
echo """PATH=/usr/local/bin:/bin
*/5 * * * * $HOME/dev-scripts/fix_certs.sh""" > /tmp/mycron
crontab /tmp/mycron
cd dev-scripts
git checkout a0ea02d9a4e42d0e1e90ec0de7994b558465b4ea
# brext bridge
curl -L https://github.com/openshift-metalkube/dev-scripts/pull/282.patch | git am
# haproxy fix
curl -L https://github.com/openshift-metalkube/dev-scripts/pull/465.patch | git am
# knative fix
curl -L https://github.com/openshift-metalkube/dev-scripts/pull/505.patch | git am
```

You need to create a [config_root.sh](config_root.sh) file representing your infrastructure.

Use the following commands for an initial sample one:

```
cp config_example.sh config_root.sh
export PULL_SECRET='{"auths": {"cloud.openshift.com": {"auth": "XXX","email": "XXX"},"quay.io": {"auth": "XXX","email": "XXX"},"registry.svc.ci.openshift.org": {"auth": "XXX"}}}'
sed -i "s/PULL_SECRET=.*/PULL_SECRET='$PULL_SECRET'/" config_root.sh
```

At this point, you are ready to launch deployment.

```
make requirements configure repo_sync ironic
eval "$(go env)"
cd $GOPATH/src/github.com/openshift-metalkube/kni-installer
git checkout 1495d7ad68022bd365d98bf6ac846d9f132458bd 
# extend timeout to 60minutes
curl -L https://github.com/openshift-metalkube/kni-installer/pull/52.patch | git am
cd -
make build ocp_run deploy_bmo register_hosts
bash 09_deploy_kubevirt.sh
bash 10_deploy_rook.sh
```

## Metalkube Workers Deployment

Once masters are deployed, additional workers can be added simply by instantiating new baremetalhost custom resources:

```
oc create -f summit-worker00-cr.yaml -n openshift-machine-api
```

You can monitor progress by using the following commands:

```
openstack baremetal node list
oc get baremetalhost -n openshift-machine-api
```

## Additional workloads deployment

For additional workloads deployment, you can either use the scripts provided in this directory or the ones from the extras directory in the dev-script tagged repo:

```
sed -i 's@bmozaffa/ktweeter:1.0@karmab/ktweeter:v0.3@' 06_tweet.sh
make
````

## Variables

All the variables used for the specific workloads have default values, except for the last four ones, related to tweet service.

Those needs a twitter app to be created

- ADMIN_USER
- ADMIN_PASSWORD
- MSSQL_PASSWORD
- KAFKA_NAMESPACE
- KAFKA_CLUSTERNAME
- KAFKA_PVC_SIZE
- KAFKA_PRODUCER_TIMER
- KAFKA_PRODUCER_TOPIC
- WINDOWS_IMAGE
- VM_SIZE
- VM_MEMORY
- UHC_TOKEN
- CONSUMER_KEY
- CONSUMER_SECRET
- ACCESS_TOKEN
- ACCESS_TOKEN_SECRET
