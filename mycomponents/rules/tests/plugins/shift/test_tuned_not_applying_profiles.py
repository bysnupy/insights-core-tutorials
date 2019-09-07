from insights.core.plugins import make_fail
from insights.specs import Specs
from insights.tests import archive_provider, InputData
from mycomponents.rules.plugins.shift import tuned_not_applying_profiles

INSTALLED_TUNED_HIT = """
libpwquality-1.2.3-5.el7.x86_64
openssh-server-7.4p1-21.el7.x86_64
tuned-2.11.0-5.el7.noarch
gettext-0.19.8.1-2.el7.x86_64
chrony-3.4-1.el7.x86_64
""".strip()

INSTALLED_TUNED_FDP_HIT = """
openvswitch-2.9.0-114.el7fdp.x86_64
tuned-2.11.0-5.el7fdp.noarch
chrony-3.4-1.el7fdp.x86_64
""".strip()

INSTALLED_TUNED_NOT_HIT = """
libpwquality-1.2.3-5.el7.x86_64
openssh-server-7.4p1-21.el7.x86_64
tuned-2.11.0-5.el7_7.1.noarch
gettext-0.19.8.1-2.el7.x86_64
chrony-3.4-1.el7.x86_64
""".strip()

INSTALLED_TUNED_FDP_NOT_HIT = """
openvswitch-2.9.0-114.el7fdp.x86_64
tuned-2.11.0-5.el7_7.1.noarch
chrony-3.4-1.el7fdp.x86_64
""".strip()


@archive_provider(tuned_not_applying_profiles.report)
def integration_test_no_hit():
    data = InputData("test1")
    data.add(Specs.installed_rpms, INSTALLED_TUNED_HIT)
    expected = make_fail(tuned_not_applying_profiles.ERROR_KEY, installed_package='tuned-2.11.0-5.el7', kcs=tuned_not_applying_profiles.KCS)
    yield data, expected

    data = InputData("test2")
    data.add(Specs.installed_rpms, INSTALLED_TUNED_FDP_HIT)
    expected = make_fail(tuned_not_applying_profiles.ERROR_KEY, installed_package='tuned-2.11.0-5.el7fdp', kcs=tuned_not_applying_profiles.KCS)
    yield data, expected

    data = InputData("test3")
    data.add(Specs.installed_rpms, INSTALLED_TUNED_NOT_HIT)
    yield data, None

    data = InputData("test4")
    data.add(Specs.installed_rpms, INSTALLED_TUNED_FDP_NOT_HIT)
    yield data, None
