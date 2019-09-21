from insights.core.plugins import make_info
from insights.tests import InputData, archive_provider, RHEL7, RHEL6
from insights.specs import Specs
from mycomponents.rules.plugins.shift import ocp_elasticsearch_crashbackoff

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

CONTENT_SYSCTL_COMMAND_HIT = """
vm.legacy_va_layout = 0
vm.lowmem_reserve_ratio = 256	256	32
vm.max_map_count = 65530
vm.memory_failure_early_kill = 0
vm.memory_failure_recovery = 1
""".strip()

CONTENT_SYSCTL_COMMAND_NOT_HIT = """
vm.legacy_va_layout = 0
vm.lowmem_reserve_ratio = 256	256	32
vm.max_map_count = 262144
vm.memory_failure_early_kill = 0
vm.memory_failure_recovery = 1
""".strip()

CONTENT_MESSAGES_HIT = """
Sep 16 16:43:47 all atomic-openshift-node: I0916 16:43:47.104648    7429 kuberuntime_manager.go:757] checking backoff for container "elasticsearch" in pod "logging-es-data-master-zaakv5bw-2-zbbzm_openshift-logging(73930796-d855-11e9-bb7f-080027ee6289)"
Sep 16 16:43:47 all atomic-openshift-node: I0916 16:43:47.104978    7429 kuberuntime_manager.go:767] Back-off 40s restarting failed container=elasticsearch pod=logging-es-data-master-zaakv5bw-2-zbbzm_openshift-logging(73930796-d855-11e9-bb7f-080027ee6289)
Sep 16 16:43:47 all atomic-openshift-node: E0916 16:43:47.105027    7429 pod_workers.go:186] Error syncing pod 73930796-d855-11e9-bb7f-080027ee6289 ("logging-es-data-master-zaakv5bw-2-zbbzm_openshift-logging(73930796-d855-11e9-bb7f-080027ee6289)"), skipping: failed to "StartContainer" for "elasticsearch" with CrashLoopBackOff: "Back-off 40s restarting failed container=elasticsearch pod=logging-es-data-master-zaakv5bw-2-zbbzm_openshift-logging(73930796-d855-11e9-bb7f-080027ee6289)"
""".strip()

CONTENT_MESSAGES_NOT_HIT = """
Sep 16 16:43:56 all atomic-openshift-node: I0916 16:43:56.099616    7429 kuberuntime_manager.go:757] checking backoff for container "prometheus" in pod "prometheus-k8s-0_openshift-monitoring(84792900-1be5-11e9-99b0-080027ee6289)"
Sep 16 16:43:56 all atomic-openshift-node: I0916 16:43:56.099762    7429 kuberuntime_manager.go:767] Back-off 5m0s restarting failed container=prometheus pod=prometheus-k8s-0_openshift-monitoring(84792900-1be5-11e9-99b0-080027ee6289)
Sep 16 16:43:56 all atomic-openshift-node: E0916 16:43:56.099804    7429 pod_workers.go:186] Error syncing pod 84792900-1be5-11e9-99b0-080027ee6289 ("prometheus-k8s-0_openshift-monitoring(84792900-1be5-11e9-99b0-080027ee6289)"), skipping: failed to "StartContainer" for "prometheus" with CrashLoopBackOff: "Back-off 5m0s restarting failed container=prometheus pod=prometheus-k8s-0_openshift-monitoring(84792900-1be5-11e9-99b0-080027ee6289)"
""".strip()


@archive_provider(ocp_elasticsearch_crashbackoff.report)
def integration_tests():
    data = InputData("Hit test 1")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    data.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    data.add(Specs.messages, CONTENT_MESSAGES_HIT)
    expected = make_info(ocp_elasticsearch_crashbackoff.ERROR_KEY, 
                         kcs=ocp_elasticsearch_crashbackoff.KCS, 
                         checked_sysctl="vm.max_map_count=65530")
    yield data, expected

    data = InputData("No Hit test 1")
    data.add(Specs.redhat_release, RHEL6)
    data.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    data.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    data.add(Specs.messages, CONTENT_MESSAGES_HIT)
    yield data, None

    data = InputData("No Hit test 2")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_NOT_HIT)
    data.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    data.add(Specs.messages, CONTENT_MESSAGES_HIT)
    yield data, None

    data = InputData("No Hit test 3")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    data.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_NOT_HIT)
    data.add(Specs.messages, CONTENT_MESSAGES_HIT)
    yield data, None

    data = InputData("No Hit test 4")
    data.add(Specs.redhat_release, RHEL7)
    data.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    data.add(Specs.sysctl, CONTENT_SYSCTL_COMMAND_HIT)
    data.add(Specs.messages, CONTENT_MESSAGES_NOT_HIT)
    yield data, None
