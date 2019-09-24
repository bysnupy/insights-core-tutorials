from insights.core.plugins import make_info, rule, condition
from insights.combiners.redhat_release import RedHatRelease
from insights.parsers.sysctl import Sysctl
from insights.parsers.messages import Messages
from insights.specs import Specs
from insights.core.filters import add_filter
from mycomponents.rules.plugins.shift import is_shift_node_service_running

ERROR_KEY = "OCP_ELASTICSEARCH_CRASHBACKOFF"
KCS = "https://access.redhat.com/solutions/4349391"

INCIDENTS_1 = 'checking backoff for container "elasticsearch" in pod'
INCIDENTS_2 = ['Back-off', 'restarting failed container=elasticsearch']

add_filter(Specs.messages, INCIDENTS_1)
Messages.keep_scan("checking_backoff_elasticsearch", INCIDENTS_1)

add_filter(Specs.messages, INCIDENTS_2[1])
Messages.keep_scan("restarting_failed_elasticsearch", INCIDENTS_2)


@condition(Sysctl)
def check_sysctl(sysctlcommand):
    if "vm.max_map_count" in sysctlcommand and sysctlcommand["vm.max_map_count"] == "65530":
        return "vm.max_map_count=" + sysctlcommand["vm.max_map_count"]


@condition(Messages)
def check_error_log(msgs):
    if getattr(msgs, "checking_backoff_elasticsearch") and getattr(msgs, "restarting_failed_elasticsearch"):
        return getattr(msgs, "checking_backoff_elasticsearch")[-1].get("raw_message")


@rule(is_shift_node_service_running, check_sysctl, check_error_log, RedHatRelease)
def report(node, checked_sysctl, checked_msg, rh_release):
    if all([node, checked_sysctl, checked_msg, rh_release.major == 7]):
        return make_info(ERROR_KEY, kcs=KCS, checked_sysctl=checked_sysctl)
