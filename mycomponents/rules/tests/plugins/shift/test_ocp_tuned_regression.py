from insights.core.plugins import make_fail
from insights.tests import InputData, archive_provider, RHEL7, RHEL6
from insights.specs import Specs
from mycomponents.rules.plugins.shift import ocp_tuned_regression

CONTENT_SYSTEMCTL_LIST_UNITS_HIT = """
sockets.target                      loaded active active    Sockets
swap.target                         loaded active active    Swap
systemd-shutdownd.socket            loaded active listening Delayed Shutdown Socket
atomic-openshift-node.service       loaded active running   OpenShift Node
""".strip()

CONTENT_SYSTEMCTL_LIST_UNITS_NOT_HIT = """
sockets.target                      loaded active active    Sockets
swap.target                         loaded active active    Swap
systemd-shutdownd.socket            loaded active listening Delayed Shutdown Socket
""".strip()

CONTENT_INSTALLED_RPMS_HIT = """
libcap-2.22-10.el7.x86_64
filesystem-3.2-25.el7.x86_64
atomic-openshift-node-3.11.98-1.git.0.0cbaff3.el7.x86_64
tuned-2.11.0-5.el7.noarch
shadow-utils-4.6-5.el7.x86_64
ncurses-base-5.9-14.20130511.el7_4.noarch
""".strip()

CONTENT_INSTALLED_RPMS_HIT2 = """
libcap-2.22-10.el7.x86_64
filesystem-3.2-25.el7.x86_64
atomic-openshift-node-3.11.98-1.git.0.0cbaff3.el7.x86_64
tuned-2.11.0-5.el7fdp.noarch
shadow-utils-4.6-5.el7.x86_64
ncurses-base-5.9-14.20130511.el7_4.noarch
""".strip()

CONTENT_INSTALLED_RPMS_NOT_HIT = """
libcap-2.22-10.el7.x86_64
filesystem-3.2-25.el7.x86_64
atomic-openshift-node-3.11.98-1.git.0.0cbaff3.el7.x86_64
tuned-2.11.0-5.el7_7.1.noarch
shadow-utils-4.6-5.el7.x86_64
ncurses-base-5.9-14.20130511.el7_4.noarch
""".strip()

CONTENT_SYSCTL_COMMAND_HIT = """
net.ipv4.neigh.default.gc_thresh1 = 128
net.ipv4.neigh.default.gc_thresh2 = 512
net.ipv4.neigh.default.gc_thresh3 = 1024
net.netfilter.nf_conntrack_max = 262144
""".strip()

CONTENT_SYSCTL_COMMAND_NOT_HIT = """
net.ipv4.neigh.default.gc_thresh1 = 8192
net.ipv4.neigh.default.gc_thresh2 = 32768
net.ipv4.neigh.default.gc_thresh3 = 65536
net.netfilter.nf_conntrack_max = 1048576
""".strip()


@archive_provider(ocp_tuned_regression.report)
def integration_test_hit():
    bad_env = InputData("bad_environment_hit_1")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    bad_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_tuned_regression.ERROR_KEY, tuned_version='tuned-2.11.0-5.el7')
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_2")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT2)
    bad_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_tuned_regression.ERROR_KEY, tuned_version='tuned-2.11.0-5.el7fdp')
    yield bad_env, expected


@archive_provider(ocp_tuned_regression.report)
def integration_test_no_hit():
    good_env = InputData("good_environment_no_hit_1")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_NOT_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    good_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_2")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_NOT_HIT)
    good_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_3")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    good_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_NOT_HIT)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_4")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_HIT)
    good_env.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    good_env.add(Specs.redhat_release, RHEL6)
    yield good_env, None
