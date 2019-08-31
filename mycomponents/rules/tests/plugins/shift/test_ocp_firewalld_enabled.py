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
tomic-openshift-excluder-3.11.59-1.git.0.7cb6277.el7.noarch
atomic-openshift-hyperkube-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-node-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-clients-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-docker-excluder-3.11.59-1.git.0.7cb6277.el7.noarch
""".strip()

CONTENT_INSTALLED_RPMS_NOT_HIT = """
atomic-openshift-excluder-3.11.59-1.git.0.7cb6277.el7.noarch
atomic-openshift-node-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-clients-3.11.59-1.git.0.7cb6277.el7.x86_64
atomic-openshift-docker-excluder-3.11.59-1.git.0.7cb6277.el7.noarch
""".strip()

@archive_provider(ocp_firewalld_enabled.report)
def integration_test_no_hit():
    data = InputData("test1")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.ps_aux, CONTENT_PS_AUX_HIT)
    data.add(Specs.systemctl_list_units, LIST_UNITS_FIREWALLD_RUNNING)
    data.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    expected = make_fail(ocp_firewalld_enabled.ERROR_KEY, firewalld_service=True, version="3.11.59")
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
