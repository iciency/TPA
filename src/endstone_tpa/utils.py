import random
import time
from endstone import Player
from endstone.form import MessageForm

def get_target_player(sender: Player, name_or_selector: str) -> Player | None:
    """
    Gets a single player target from a name or a target selector (@r).
    Selectors @s and @p are disallowed as they can resolve to the sender.
    """
    server = sender.server

    if not name_or_selector.startswith("@"):
        return server.get_player(name_or_selector)

    selector = name_or_selector.lower()

    if selector == "@s" or selector == "@p":
        # Disallowed for TPA commands as they can resolve to the sender.
        return None

    # Exclude self from potential targets for @r
    online_players = [p for p in server.online_players if p.unique_id != sender.unique_id]

    if not online_players:
        return None

    if selector == "@r":
        return random.choice(online_players)

    # For other selectors like @a, @e, or invalid ones, return None
    # The command handler will issue the "player not found" message.
    return None

def handle_tpa_request(plugin, sender: Player, target: Player, request_type: str):
    """
    Handles the logic for sending a TPA request (/tpa or /tpthere).
    """
    if sender == target:
        plugin._(sender, "tpa.cannot_request_self")
        return

    if sender.unique_id in plugin.tpa_blocks.get(target.unique_id, []):
        plugin._(sender, "tpa.target_blocking_you", target.name)
        return

    if target.unique_id not in plugin.tpa_requests:
        plugin.tpa_requests[target.unique_id] = {}
    plugin.tpa_requests[target.unique_id][sender.unique_id] = (time.time(), request_type)
    plugin._(sender, "tpa.request_sent", target.name)

    def on_form_submit(target_player: Player, data: int):
        if data == 0:  # Accept
            plugin.server.dispatch_command(target_player, f'tpaccept "{sender.name}"')
        else:  # Deny
            plugin.server.dispatch_command(target_player, f'tpdeny "{sender.name}"')

    content_key = f"tpa.form.content.{request_type}"
    fallback_content_key = f"{request_type}.request_received"

    form = MessageForm(
        title=plugin._(target, "tpa.form.title", return_string=True),
        content=plugin._(target, content_key, sender.name, return_string=True),
        button1=plugin._(target, "tpa.form.accept", return_string=True),
        button2=plugin._(target, "tpa.form.deny", return_string=True),
    )
    
    plugin._(target, fallback_content_key, sender.name)
    timeout = plugin.plugin_config.get("request-timeout", 60)
    plugin._(target, "tpa.request_helper", sender.name, timeout)
    
    form.on_submit = on_form_submit
    target.send_form(form)
