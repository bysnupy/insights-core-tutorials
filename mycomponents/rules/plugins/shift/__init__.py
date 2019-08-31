from insights.parsers.ps import PsAux
from insights.parsers.systemd.unitfiles import ListUnits
from insights.core.plugins import condition
from insights.core.filters import add_filter
from insights.specs import Specs

MASTER_CMD = "/usr/bin/openshift start master"
MASTER_API_3_10_PLUS_CMD = "openshift start master api"
MASTER_CONTROLLERS_3_10_PLUS_CMD = "openshift start master controllers"
NODE_CMD = "/usr/bin/openshift start node"
NODE_3_10_PLUS_CMD = "openshift start node"
add_filter(Specs.ps_aux, MASTER_CMD)
add_filter(Specs.ps_aux, NODE_CMD)
add_filter(Specs.ps_aux, MASTER_API_3_10_PLUS_CMD)
add_filter(Specs.ps_aux, MASTER_CONTROLLERS_3_10_PLUS_CMD)
add_filter(Specs.ps_aux, NODE_3_10_PLUS_CMD)

@condition(PsAux)
def is_shift_master_running(ps):
    master_3_9_or_less_running = any(row[ps.command_name].startswith(MASTER_CMD) for row in ps.data)
    master_api_3_10_or_more_running = any(row[ps.command_name].startswith(MASTER_API_3_10_PLUS_CMD) for row in ps.data)
    master_controllers_3_10_or_more_running = any(
        row[ps.command_name].startswith(MASTER_CONTROLLERS_3_10_PLUS_CMD) for row in ps.data)
    if master_3_9_or_less_running:
        return master_3_9_or_less_running
    elif master_api_3_10_or_more_running and master_controllers_3_10_or_more_running:
        return master_api_3_10_or_more_running
    else:
        return False


@condition(PsAux)
def is_shift_node_running(ps):
    node_3_9_or_less_running = any(row[ps.command_name].startswith(NODE_CMD) for row in ps.data)
    node_3_10_or_more_running = any(row[ps.command_name].startswith(NODE_3_10_PLUS_CMD) for row in ps.data)
    if node_3_9_or_less_running:
        return node_3_9_or_less_running
    elif node_3_10_or_more_running:
        return node_3_10_or_more_running
    else:
        return False


@condition(ListUnits)
def is_shift_node_service_running(lu):
    return lu.is_running("atomic-openshift-node.service")
