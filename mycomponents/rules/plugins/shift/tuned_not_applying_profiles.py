"""
Not applying tuned profiles due to regression
=============================================++++=====================
The tuned profiles does not be applied sysctl after upgrading RHEL7.7.
It would affect intermittent DNS/Network timeouts and you can see
"kernel: net_ratelimit: 100 callbacks suppressed" error messages either.

Trigger Logic:
  1. installed tuned (RHEL7) is tuned-2.11.0-5.el7 or tuned-2.11.0-5.el7fdp <= tuned-2.11.0-5.el7_7.1

* KCS:      https://access.redhat.com/solutions/4395931
* Bugzilla: https://bugzilla.redhat.com/show_bug.cgi?id=1739418
"""

from insights import condition, rule, make_fail
from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm

ERROR_KEY = "BAD_TUNED_NOT_APPLYING_SYSCTL"
KCS = "https://access.redhat.com/solutions/4395931"


@condition(InstalledRpms)
def affected_tuned_package(rpms):
    installed_tuned = rpms.newest('tuned')
    affected_tuned = InstalledRpm.from_package('tuned-2.11.0-5.el7.noarch')
    affected_tuned_fdp = InstalledRpm.from_package('tuned-2.11.0-5.el7fdp.noarch')
    fixed_tuned = InstalledRpm.from_package('tuned-2.11.0-5.el7_7.1.noarch')
    if (installed_tuned >= affected_tuned or installed_tuned >= affected_tuned_fdp):
        if (installed_tuned < fixed_tuned):
            return installed_tuned.package
    return []


@rule(affected_tuned_package)
def report(package):
    if package:
        return make_fail(ERROR_KEY, installed_package=package, kcs=KCS)
