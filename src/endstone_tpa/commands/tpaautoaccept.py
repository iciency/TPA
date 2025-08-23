from endstone import Player

command = {
    "tpaautoaccept": {
        "description": "Toggle automatically accepting all TPA requests.",
        "usages": ["/tpaautoaccept"],
        "permissions": ["tpa.command.tpaautoaccept"],
    }
}

def handler(plugin, sender, args):
    if not isinstance(sender, Player):
        plugin._(sender, "tpa.not_a_player")
        return True

    player_uuid = sender.unique_id
    if player_uuid in plugin.tpa_auto_accept:
        plugin.tpa_auto_accept.remove(player_uuid)
        plugin._(sender, "tpa.auto_accept_disabled")
    else:
        plugin.tpa_auto_accept.append(player_uuid)
        plugin._(sender, "tpa.auto_accept_enabled")

    # Save to config
    plugin.plugin_config["auto_accept"] = [str(uuid) for uuid in plugin.tpa_auto_accept]
    with open(plugin.data_folder / "config.json", "w") as f:
        import json
        json.dump(plugin.plugin_config, f, indent=4)

    return True
