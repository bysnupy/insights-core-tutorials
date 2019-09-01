"""
oc rsh/exec/logs CLI cannot use on added new RHEL7 worker nodes
==================================================================================
RHEL7 worker node is required Minimal mode to install, the Minial mode is enabled
firewalld Service by default. It affects connectivity using oc rsh/exec/logs CLI.
As of OpenShift 4.1, kube-proxy is managed by the Cluster Network Operator. 
Unlike OpenShift 3.x, it maintains network rules using only iptables service 
instead of firewalld service. 

Trigger condition:

  1, The Worker Node OS is RHEL7

  2, The OpenShift version is 4.1

  3, OpenShift Worker Node is running

  4, firewalld.service is running and enabled

 - Trello: TODO
 - KBase: https://access.redhat.com/solutions/4347481
"""

from insights.core.filters import add_filter
from insights.core.plugins import rule, make_fail, condition
from insights.parsers.ps import PsAux
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm
from insights.parsers.systemd.unitfiles import ListUnits
from insights.combiners.redhat_release import RedHatRelease
from insights.specs import Specs

ERROR_KEY = "OCP_FIREWALLD_ENABLED"
NODE_4_1_PLUS_CMD = "/usr/bin/hyperkube kubelet"
add_filter(Specs.ps_aux, NODE_4_1_PLUS_CMD)

@condition(RedHatRelease)
def check_rhel_version(rel):
    return rel.major == 7

@condition(InstalledRpms)
def is_openshift_version_4x(installed_rpms):
    openshift_rpm = installed_rpms.get_max('openshift-hyperkube')
    if openshift_rpm and openshift_rpm.version.startswith(('4.1')):
        return openshift_rpm.version
    
@condition(PsAux)
def is_shift_4_1_node_running(ps):
    return any(row[ps.command_name].startswith(NODE_4_1_PLUS_CMD) for row in ps.data)

@condition(ListUnits)
def is_firewalld_service_running(lu):
    return lu.is_running("firewalld.service")

@rule(is_shift_4_1_node_running, is_firewalld_service_running, is_openshift_version_4x, check_rhel_version)
def report(node_running, firewalld_service, ocp_4x, rh_release):
    if all([node_running, firewalld_service, ocp_4x, rh_release]):
        return make_fail(ERROR_KEY, firewalld_service=firewalld_service, version=ocp_4x)
