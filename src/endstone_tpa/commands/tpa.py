from endstone import Player
from ..utils import get_target_player, handle_tpa_request

command = {
    "tpa": {
        "description": "Request to teleport to another player.",
        "usages": ["/tpa <player: player>"],
        "permissions": ["tpa.command.tpa"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True

    player = sender

    if len(args) != 1:
        plugin._(sender, "tpa.command.usage")
        return False

    target_name = args[0]
    target = get_target_player(player, target_name)

    if target is None:
        plugin._(sender, "tpa.player_not_found", target_name)
        return True

    handle_tpa_request(plugin, player, target, "tpa")
    return True
