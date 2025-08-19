import time
from endstone import Player
from endstone.form import MessageForm
from ..utils import get_target_player

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

    if player == target:
        plugin._(player, "tpa.cannot_request_self")
        return True

    if target.unique_id not in plugin.tpa_requests:
        plugin.tpa_requests[target.unique_id] = {}
    plugin.tpa_requests[target.unique_id][player.unique_id] = (time.time(), "tpa")
    plugin._(player, "tpa.request_sent", target.name)

    def on_form_submit(target_player: Player, data: int):
        if data == 0:  # Accept
            plugin.server.dispatch_command(target_player, f'tpaccept "{player.name}"')
        else:  # Deny
            plugin.server.dispatch_command(target_player, f'tpdeny "{player.name}"')

    form = MessageForm(
        title=plugin._(target, "tpa.form.title", return_string=True),
        content=plugin._(target, "tpa.form.content.tpa", player.name, return_string=True),
        button1=plugin._(target, "tpa.form.accept", return_string=True),
        button2=plugin._(target, "tpa.form.deny", return_string=True),
    )
    
    plugin._(target, "tpa.request_received", player.name)
    plugin._(target, "tpa.request_helper")
    
    form.on_submit = on_form_submit
    target.send_form(form)
    return True
