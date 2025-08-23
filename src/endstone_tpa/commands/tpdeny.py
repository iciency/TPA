from endstone import Player
from ..utils import get_target_player

command = {
    "tpdeny": {
        "description": "Deny a teleport request.",
        "usages": ["/tpdeny [player: player]"],
        "permissions": ["tpa.command.tpdeny"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True
    
    player = sender
    requests = plugin.tpa_requests.get(player.unique_id, {})

    if not requests:
        plugin._(player, "tpa.no_pending_request", "")  # Fallback for single arg
        return True

    requester_uuid = None
    requester_name = None
    if args:
        requester_name = args[0]
        requester = get_target_player(player, requester_name)
        if requester is None or requester.unique_id not in requests:
            plugin._(player, "tpa.no_pending_request", requester_name)
            return True
        requester_uuid = requester.unique_id
    elif len(requests) == 1:
        requester_uuid = list(requests.keys())[0]
    else:
        plugin._(player, "tpa.multiple_requests")
        return True

    requests.pop(requester_uuid)
    requester = plugin.server.get_player(requester_uuid)

    # Determine the requester's name for the message
    if requester_name is None and requester is not None:
        requester_name = requester.name
    elif requester_name is None:
        requester_name = "Someone" # Fallback

    plugin._(player, "tpa.request_denied", requester_name)
    if requester:
        plugin._(requester, "tpa.sender_denied", player.name)
    return True
