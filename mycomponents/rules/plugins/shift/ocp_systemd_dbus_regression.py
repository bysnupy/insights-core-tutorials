from insights.core.plugins import make_fail, rule, condition
from insights.combiners.redhat_release import RedHatRelease
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm
from insights.specs import Specs
from insights.core.filters import add_filter
from insights.parsers.messages import Messages
from mycomponents.rules.plugins.shift import is_shift_node_service_running

ERROR_KEY = "OCP_SYSTEMD_DBUS_REGRESSION"

ERROR_LOG_CROND = 'pam_systemd(crond:session): Failed to create session: Connection timed out'
ERROR_LOG_SYSTEMD_LOGIND1 = 'slice, ignoring: Connection timed out'
ERROR_LOG_SYSTEMD_LOGIND2 = 'scope: Connection timed out'
ERROR_LOG_SYSTEMD = 'Failed to propagate agent release message: Operation not supported'

add_filter(Specs.messages, ERROR_LOG_CROND)
add_filter(Specs.messages, ERROR_LOG_SYSTEMD_LOGIND1)
add_filter(Specs.messages, ERROR_LOG_SYSTEMD_LOGIND2)
add_filter(Specs.messages, ERROR_LOG_SYSTEMD)

Messages.keep_scan('checking_crond_msg', ERROR_LOG_CROND)
Messages.keep_scan('checking_systemd-logind_msg1', ERROR_LOG_SYSTEMD_LOGIND1)
Messages.keep_scan('checking_systemd-logind_msg2', ERROR_LOG_SYSTEMD_LOGIND2)
Messages.keep_scan('checking_systemd_msg', ERROR_LOG_SYSTEMD)

@condition(InstalledRpms)
def is_affected_systemd_version(rpms):
    installed_systemd = rpms.newest('systemd')
    systemd760 = InstalledRpm.from_package('systemd-219-62.el7')
    systemd770 = InstalledRpm.from_package('systemd-219-67.el7')
    fixed_systemd76z = InstalledRpm.from_package('systemd-219-62.el7_6.9')
    fixed_systemd7 = InstalledRpm.from_package('systemd-219-67.el7')
    if (installed_systemd >= systemd760 and installed_systemd < systemd770):
        if (installed_systemd < fixed_systemd76z):
            return [installed_systemd.package, 'systemd-219-62.el7_6.9']
    elif (installed_systemd < fixed_systemd7):
        return [installed_systemd.package, 'systemd-219-67.el7']

@condition(Messages)
def check_error_log(msgs):
    if getattr(msgs, "checking_crond_msg") or getattr(msgs, "checking_systemd-logind_msg1") or getattr(
               msgs, "checking_systemd-logind_msg2") or getattr(msgs, "checking_systemd_msg"):
        return True
    return False

@rule(is_shift_node_service_running, is_affected_systemd_version, check_error_log, RedHatRelease)
def report(node, systemd_version, check_error_log, rh_release):
    if all([node, systemd_version, check_error_log, rh_release.major == 7]):
        return make_fail(ERROR_KEY, systemd_version=systemd_version)
