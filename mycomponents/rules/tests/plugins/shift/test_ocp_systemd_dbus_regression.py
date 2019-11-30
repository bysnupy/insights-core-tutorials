from insights.core.plugins import make_fail
from insights.tests import InputData, archive_provider, RHEL7, RHEL6
from insights.specs import Specs
from mycomponents.rules.plugins.shift import ocp_systemd_dbus_regression

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

CONTENT_INSTALLED_RPMS_HIT1 = """
redhat-support-lib-python-0.9.7-6.el7.noarch
cryptsetup-libs-2.0.3-3.el7.x86_64
systemd-219-62.el7.x86_64
hdparm-9.43-5.el7.x86_64
device-mapper-event-libs-1.02.146-4.el7.x86_64
""".strip()

# RHEL7.5.0 (not fixed)
CONTENT_INSTALLED_RPMS_750_HIT = """
subscription-manager-1.17.15-1.el7.x86_64                   Tue Jul  9 14:37:30 2019
sudo-1.8.6p7-20.el7.x86_64                                  Tue Jul  9 14:37:44 2019
systemd-219-57.el7.x86_64                                   Tue Jul  9 15:10:42 2019
systemd-libs-219-57.el7.x86_64                              Tue Jul  9 15:10:40 2019
systemd-sysv-219-57.el7.x86_64                              Tue Jul  9 15:10:42 2019
sysvinit-tools-2.88-14.dsf.el7.x86_64                       Tue Jul  9 14:36:10 2019
""".strip()

# RHEL7.6.0 (not fixed)
CONTENT_INSTALLED_RPMS_760_HIT = """
sudo-1.8.6p7-20.el7.x86_64                                  Tue Jul  9 14:37:44 2019
systemd-219-62.el7.x86_64                                   Tue Jul  9 15:13:36 2019
systemd-libs-219-62.el7.x86_64                              Tue Jul  9 15:13:34 2019
systemd-sysv-219-62.el7.x86_64                              Tue Jul  9 15:13:37 2019
sysvinit-tools-2.88-14.dsf.el7.x86_64                       Tue Jul  9 14:36:10 2019
""".strip()

# RHEL7.7 (fixed)
CONTENT_INSTALLED_RPMS_NOT_HIT = """
cryptsetup-libs-2.0.3-3.el7.x86_64                          Tue Jul  9 14:36:10 2019
systemd-219-67.el7.x86_64                                   Tue Jul  9 14:36:10 2019
systemd-libs-219-67.el7.x86_64                              Tue Jul  9 15:13:34 2019
systemd-sysv-219-67.el7.x86_64                              Tue Jul  9 15:13:37 2019
hdparm-9.43-5.el7.x86_64                                    Tue Jul  9 14:36:10 2019
device-mapper-event-libs-1.02.146-4.el7.x86_64              Tue Jul  9 14:36:10 2019
""".strip()

CONTENT_MESSAGE_HIT1 = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:11:09 master1 crond[100020]: pam_systemd(crond:session): Failed to create session: Connection timed out
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

CONTENT_MESSAGE_HIT2 = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:11:09 master1 systemd-logind[10714]: Failed to start user slice user-0.slice, ignoring: Connection timed out ((null))
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

CONTENT_MESSAGE_HIT3 = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:11:09 master1 systemd-logind[10714]: Failed to start session scope session-13692.scope: Connection timed out
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

CONTENT_MESSAGE_HIT4 = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:11:09 master1 systemd[1]: Failed to propagate agent release message: Operation not supported
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

CONTENT_MESSAGE_HIT5 = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:11:09 master1 crond[100020]: pam_systemd(crond:session): Failed to create session: Connection timed out
Nov 29 23:11:09 master1 systemd-logind[10714]: Failed to start user slice user-0.slice, ignoring: Connection timed out ((null))
Nov 29 23:11:09 master1 systemd[1]: Failed to propagate agent release message: Operation not supported
Nov 29 23:11:09 master1 systemd-logind[10714]: Failed to start session scope session-13692.scope: Connection timed out
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

CONTENT_MESSAGE_NOT_HIT = """
Nov 29 23:11:09 master1 dnsmasq[1248]: setting upstream servers from DBus
Nov 29 23:14:56 master1 atomic-openshift-node: I1129 23:14:56.379463    9814 kuberuntime_manager.go:513] Container {Name:prometheus-proxy Image:registry.redhat.io/openshift3/oauth-proxy:v3.11 Command:[] Args:[-provider=openshift -https-address=:9091 -http-address= -email-domain=* -upstream=http://localhost:9090 -htpasswd-file=/etc/proxy/htpasswd/auth -openshift-service-account=prometheus-k8s -openshift-sar={"resource": "namespaces", "verb": "get"} -openshift-delegate-urls={"/": {"resource": "namespaces", "verb": "get"}} -tls-cert=/etc/tls/private/tls.crt -tls-key=/etc/tls/private/tls.key -client-secret-file=/var/run/secrets/kubernetes.io/serviceaccount/token -cookie-secret-file=/etc/proxy/secrets/session_secret -openshift-ca=/etc/pki/tls/cert.pem -openshift-ca=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt -skip-auth-regex=^/metrics] WorkingDir: Ports:[{Name:web HostPort:0 ContainerPort:9091 Protocol:TCP HostIP:}] EnvFrom:[] Env:[] Resources:{Limits:map[] Requests:map[]} VolumeMounts:[{Name:secret-prometheus-k8s-tls ReadOnly:false MountPath:/etc/tls/private SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-proxy ReadOnly:false MountPath:/etc/proxy/secrets SubPath: MountPropagation:<nil>} {Name:secret-prometheus-k8s-htpasswd ReadOnly:false MountPath:/etc/proxy/htpasswd SubPath: MountPropagation:<nil>} {Name:prometheus-k8s-token-k57pp ReadOnly:true MountPath:/var/run/secrets/kubernetes.io/serviceaccount SubPath: MountPropagation:<nil>}] VolumeDevices:[] LivenessProbe:nil ReadinessProbe:nil Lifecycle:nil TerminationMessagePath:/dev/termination-log TerminationMessagePolicy:File ImagePullPolicy:IfNotPresent SecurityContext:&SecurityContext{Capabilities:&Capabilities{Add:[],Drop:[KILL MKNOD SETGID SETUID],},Privileged:nil,SELinuxOptions:nil,RunAsUser:*1000130000,RunAsNonRoot:nil,ReadOnlyRootFilesystem:nil,AllowPrivilegeEscalation:nil,RunAsGroup:nil,} Stdin:false StdinOnce:false TTY:false} is dead, but RestartPolicy says that we should restart it.
""".strip()

@archive_provider(ocp_systemd_dbus_regression.report)
def integration_test_hit():
    bad_env = InputData("bad_environment_hit_1")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT1)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-57.el7', 'systemd-219-67.el7'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_2")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT2)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-57.el7', 'systemd-219-67.el7'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_3")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT3)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-57.el7', 'systemd-219-67.el7'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_4")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT4)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-57.el7', 'systemd-219-67.el7'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_5")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT5)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-57.el7', 'systemd-219-67.el7'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_6")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT1)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-62.el7', 'systemd-219-62.el7_6.9'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_7")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT2)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-62.el7', 'systemd-219-62.el7_6.9'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_8")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT3)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-62.el7', 'systemd-219-62.el7_6.9'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_9")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT4)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-62.el7', 'systemd-219-62.el7_6.9'])
    yield bad_env, expected

    bad_env = InputData("bad_environment_hit_10")
    bad_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    bad_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    bad_env.add(Specs.messages, CONTENT_MESSAGE_HIT5)
    bad_env.add(Specs.redhat_release, RHEL7)
    expected = make_fail(ocp_systemd_dbus_regression.ERROR_KEY, systemd_version=['systemd-219-62.el7', 'systemd-219-62.el7_6.9'])
    yield bad_env, expected

@archive_provider(ocp_systemd_dbus_regression.report)
def integration_test_no_hit():
    good_env = InputData("good_environment_no_hit_1")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_NOT_HIT)
    good_env.add(Specs.messages, CONTENT_MESSAGE_HIT1)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_2")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_NOT_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_750_HIT)
    good_env.add(Specs.messages, CONTENT_MESSAGE_HIT2)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_3")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    good_env.add(Specs.messages, CONTENT_MESSAGE_NOT_HIT)
    good_env.add(Specs.redhat_release, RHEL7)
    yield good_env, None

    good_env = InputData("good_environment_no_hit_4")
    good_env.add(Specs.systemctl_list_units, CONTENT_SYSTEMCTL_LIST_UNITS_HIT)
    good_env.add(Specs.installed_rpms, CONTENT_INSTALLED_RPMS_760_HIT)
    good_env.add(Specs.messages, CONTENT_MESSAGE_HIT3)
    good_env.add(Specs.redhat_release, RHEL6)
    yield good_env, None
