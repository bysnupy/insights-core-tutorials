from insights.core.plugins import make_fail
from insights.tests import InputData, archive_provider, RHEL7, RHEL6
from insights.specs import Specs
from mycomponents.rules.plugins.shift import ocp_firewalld_enabled

CONTENT_PS_AUX_HIT = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      3404  0.3  2.4 517628 50192 ?        Ssl  21:51   0:14 /usr/bin/crio --enable-metrics=true --metrics-port=9537
root      3870  3.3  3.8 1217908 79256 ?       Ssl  21:51   2:28 /usr/bin/hyperkube kubelet --config=/etc/kubernetes/kubelet.conf --bootstrap-kubeconfig=/etc/kubernetes/kubeconfig --kubeconfig=/var/lib/kubelet/kubeconfig --container-runtime=remote --container-runtime-endpoint=/var/run/crio/crio.sock --allow-privileged --node-labels=node-role.kubernetes.io/worker,node.openshift.io/os_version=7.6,node.openshift.io/os_id=rhel --minimum-container-ttl-duration=6m0s --volume-plugin-dir=/etc/kubernetes/kubelet-plugins/volume/exec --client-ca-file=/etc/kubernetes/ca.crt --cloud-provider= --anonymous-auth=false --v=3
""".strip()

CONTENT_PS_AUX_NOT_HIT = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      3404  0.3  2.4 517628 50192 ?        Ssl  21:51   0:14 /usr/bin/crio --enable-metrics=true --metrics-port=9537
""".strip()

LIST_UNITS_FIREWALLD_RUNNING = """
crio.service                       loaded active running Open Container Initiative Daemon
dbus.service                       loaded active running D-Bus System Message Bus
firewalld.service                  loaded active running firewalld - dynamic firewall daemon
kubelet.service                    loaded active running Kubernetes Kubelet
""".strip()

LIST_UNITS_FIREWALLD_NOT_RUNNING = """
crio.service                       loaded active running Open Container Initiative Daemon
dbus.service                       loaded active running D-Bus System Message Bus
kubelet.service                    loaded active running Kubernetes Kubelet
""".strip()

CONTENT_INSTALLED_RPMS_HIT = """
cri-o-1.13.9-1.rhaos4.1.gitd70609a.el7.x86_64
subscription-manager-1.21.10-2.el7.x86_64
subscription-manager-rhsm-1.21.10-2.el7.x86_64
openshift-clients-4.1.9-201907280809.git.0.0cb2391.el7.x86_64
criu-3.12-2.el7.x86_64
cri-tools-1.13.0-1.rhaos4.1.gitc06001f.el7.x86_64
subscription-manager-rhsm-certificates-1.21.10-2.el7.x86_64
initscripts-9.49.46-1.el7.x86_64
openshift-hyperkube-4.1.9-201907280809.git.0.0cb2391.el7.x86_64
""".strip()

CONTENT_INSTALLED_RPMS_NOT_HIT = """
cri-o-1.13.9-1.rhaos4.1.gitd70609a.el7.x86_64
subscription-manager-1.21.10-2.el7.x86_64
subscription-manager-rhsm-1.21.10-2.el7.x86_64
openshift-clients-4.1.9-201907280809.git.0.0cb2391.el7.x86_64
criu-3.12-2.el7.x86_64
cri-tools-1.13.0-1.rhaos4.1.gitc06001f.el7.x86_64
subscription-manager-rhsm-certificates-1.21.10-2.el7.x86_64
initscripts-9.49.46-1.el7.x86_64
""".strip()

@archive_provider(ocp_firewalld_enabled.report)
def integration_test_no_hit():
    data = InputData("test1")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    expected = make_fail(ocp_firewalld_enabled.ERROR_KEY, firewalld_service=True, version="4.1.9")
    yield data, expected

    data = InputData("test2")
    data.add(Specs.redhat_release, RHEL6)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    yield data, None

    data = InputData("test3")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_NOT_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    yield data, None

    data = InputData("test4")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_NOT_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    yield data, None

    data = InputData("test5")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_NOT_HIT)
    yield data, None

    data = InputData("test6")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_NOT_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_NOT_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_NOT_HIT)
    yield data, None
