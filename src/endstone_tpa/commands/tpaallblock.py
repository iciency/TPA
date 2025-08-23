from endstone import Player

command = {
    "tpaallblock": {
        "description": "Toggle blocking all TPA requests.",
        "usages": ["/tpaallblock"],
        "permissions": ["tpa.command.tpaallblock"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True

    player_uuid = sender.unique_id
    if player_uuid in plugin.tpa_all_blocks:
        plugin.tpa_all_blocks.remove(player_uuid)
        plugin._(sender, "tpa.all_block_disabled")
    else:
        plugin.tpa_all_blocks.append(player_uuid)
        plugin._(sender, "tpa.all_block_enabled")

    # Save to config
    plugin.plugin_config["all_blocks"] = [str(uuid) for uuid in plugin.tpa_all_blocks]
    with open(plugin.data_folder / "config.json", "w") as f:
        import json
        json.dump(plugin.plugin_config, f, indent=4)

    return True
