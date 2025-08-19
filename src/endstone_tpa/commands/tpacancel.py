from endstone import Player

command = {
    "tpacancel": {
        "description": "Cancel a teleport request.",
        "usages": ["/tpacancel"],
        "permissions": ["tpa.command.tpacancel"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True
    
    player = sender

    request_found = False
    target_to_notify = None
    for target_uuid, requests in plugin.tpa_requests.items():
        if player.unique_id in requests:
            requests.pop(player.unique_id)
            request_found = True
            target_to_notify = plugin.server.get_player(target_uuid)
            if not requests:
                # Clean up the entry if no more requests for this target
                plugin.tpa_requests.pop(target_uuid)
            break  # Assuming a player can only send one request at a time

    if not request_found:
        plugin._(player, "tpa.no_pending_request")
        return True

    target = target_to_notify

    plugin._(player, "tpa.request_cancelled")
    if target:
        plugin._(target, "tpa.cancelled_by_requester", player.name)
    return True
