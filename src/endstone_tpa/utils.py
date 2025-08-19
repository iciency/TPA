import random
from endstone import Player

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
