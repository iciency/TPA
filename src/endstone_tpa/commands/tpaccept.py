import time
from endstone import Player
from ..utils import get_target_player

command = {
    "tpaccept": {
        "description": "Accept a teleport request.",
        "usages": ["/tpaccept [player: player]"],
        "permissions": ["tpa.command.tpaccept"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True
    
    player = sender
    requests = plugin.tpa_requests.get(player.unique_id, {})

    if not requests:
        plugin._(player, "tpa.no_pending_request")
        return True

    requester_uuid = None
    if args:
        requester_name = args[0]
        requester = get_target_player(player, requester_name)
        if requester is None or requester.unique_id not in requests:
            plugin._(player, "tpa.no_request_from_player", requester_name)
            return True
        requester_uuid = requester.unique_id
    elif len(requests) == 1:
        requester_uuid = list(requests.keys())[0]
    else:
        plugin._(player, "tpa.multiple_requests")
        return True

    timestamp, tpa_type = requests.pop(requester_uuid)
    requester = plugin.server.get_player(requester_uuid)

    timeout = plugin.plugin_config.get("request-timeout", 60)
    if time.time() - timestamp > timeout:
        plugin._(player, "tpa.request_expired")
        if requester:
            plugin._(requester, "tpa.requester_expired", player.name)
        return True

    if not requester:
        plugin._(player, "tpa.requester_not_online")
        return True

    if tpa_type == "tpa":
        requester.teleport(player.location)
        plugin._(requester, "tpa.accepted_tpa", player.name)
        plugin._(player, "tpa.accepted_by_target", requester.name)
    elif tpa_type == "tpthere":
        player.teleport(requester.location)
        plugin._(player, "tpthere.accepted_tpa", requester.name)
        plugin._(requester, "tpthere.accepted_by_requester", player.name)
    return True
