"""
OpenShift Intermittent network issues after upgrading to RHEL 7.7
=================================================================
Due to a regression on tuned-2.11.0-5.el7, the OpenShift tuned
profile sysctl set does not be configured under "kernel.pid_max"
of "/etc/tuned/openshift/tuned.conf" after upgrading to RHEL 7.7.

Trigger Conditions:
1. The host is an OpenShift node
2. tuned version is tuned-2.11.0-5.el7
3. any of net.ipv4.neigh.default.gc_thresh{1,2,3} and
   net.netfilter.nf_conntrack_max sysctl shows default values.
If 1&2&3:
return Error_Key

* Bugzilla: https://bugzilla.redhat.com/show_bug.cgi?id=1739418
* KCS: https://access.redhat.com/solutions/4395931
"""

from insights.core.plugins import make_fail, rule, condition
from insights.combiners.redhat_release import RedHatRelease
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm
from insights.parsers.sysctl import Sysctl
from mycomponents.rules.plugins.shift import is_shift_node_service_running

ERROR_KEY = "OCP_TUNED_REGRESSION"
AFFECTED_VERSION = [InstalledRpm.from_package('tuned-2.11.0-5.el7').nvr,
                    InstalledRpm.from_package('tuned-2.11.0-5.el7fdp').nvr]


@condition(InstalledRpms)
def is_affected_tuned_version(installed_rpms):
    tuned_rpm = installed_rpms.get_max('tuned')
    openshift_node_rpm = installed_rpms.get_max('atomic-openshift-node')
    if tuned_rpm and openshift_node_rpm and tuned_rpm.nvr in AFFECTED_VERSION:
        return tuned_rpm.nvr


@condition(Sysctl)
def check_tuned_sysctl(sysctlcommand):
    if "net.ipv4.neigh.default.gc_thresh1" in sysctlcommand and sysctlcommand["net.ipv4.neigh.default.gc_thresh1"] == "128":
        return True
    if "net.ipv4.neigh.default.gc_thresh2" in sysctlcommand and sysctlcommand["net.ipv4.neigh.default.gc_thresh2"] == "512":
        return True
    if "net.ipv4.neigh.default.gc_thresh3" in sysctlcommand and sysctlcommand["net.ipv4.neigh.default.gc_thresh3"] == "1024":
        return True
    if "net.netfilter.nf_conntrack_max" in sysctlcommand and sysctlcommand["net.netfilter.nf_conntrack_max"] == "262144":
        return True


@rule(is_shift_node_service_running, is_affected_tuned_version, check_tuned_sysctl, RedHatRelease)
def report(node, tuned_version, checked_sysctl, rh_release):
    if all([node, tuned_version, checked_sysctl, rh_release.major == 7]):
        return make_fail(ERROR_KEY, tuned_version=tuned_version)
