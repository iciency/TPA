from endstone import Player
from ..utils import get_target_player

command = {
    "tpablock": {
        "description": "Block TPA requests from a specific player.",
        "usages": ["/tpablock <player: player>"],
        "permissions": ["tpa.command.tpablock"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True

    if len(args) != 1:
        plugin._(sender, "tpa.block.usage")
        return False

    block_target_name = args[0]
    block_target = get_target_player(sender, block_target_name)

    if block_target is None:
        plugin._(sender, "tpa.player_not_found", block_target_name)
        return True

    if sender == block_target:
        plugin._(sender, "tpa.cannot_block_self")
        return True

    player_blocks = plugin.tpa_blocks.get(sender.unique_id, [])
    if block_target.unique_id in player_blocks:
        player_blocks.remove(block_target.unique_id)
        plugin._(sender, "tpa.player_unblocked", block_target.name)
    else:
        player_blocks.append(block_target.unique_id)
        plugin._(sender, "tpa.player_blocked", block_target.name)

    plugin.tpa_blocks[sender.unique_id] = player_blocks

    # Save to config
    plugin.plugin_config["blocks"] = {str(k): [str(v) for v in val] for k, val in plugin.tpa_blocks.items()}
    with open(plugin.data_folder / "config.json", "w") as f:
        import json
        json.dump(plugin.plugin_config, f, indent=4)
    return True
