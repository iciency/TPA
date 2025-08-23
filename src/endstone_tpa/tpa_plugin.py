import json
import os
import time
from typing import Dict, Tuple
from uuid import UUID

from endstone import Player
from endstone.command import Command, CommandSender
from endstone.plugin import Plugin

from .commands import preloaded_commands, preloaded_handlers


class TpaPlugin(Plugin):
    prefix = "TpaPlugin"
    api_version = "0.10"
    load = "POSTWORLD"
    # target_uuid -> {requester_uuid: (timestamp, type)}
    tpa_requests: Dict[UUID, Dict[UUID, Tuple[float, str]]] = {}
    # player_uuid -> [blocked_player_uuid]
    tpa_blocks: Dict[UUID, list[UUID]] = {}
    translations: Dict[str, Dict[str, str]] = {}

    def _(self, sender: CommandSender, message: str, *args, return_string: bool = False) -> str | None:
        if isinstance(sender, Player):
            locale = sender.locale
        else:
            locale = self.server.language.locale

        translation = self.translations.get(message, {}).get(
            locale, self.translations.get(message, {}).get("en_US")
        )
        text_to_translate = translation if translation else message

        if args:
            formatted_message = text_to_translate.format(*args)
        else:
            formatted_message = text_to_translate

        if return_string:
            return formatted_message
        else:
            sender.send_message(formatted_message)
            return None

    commands = preloaded_commands

    permissions = {
        "tpa.command.*": {"description": "Allows users to use all TPA commands.", "default": True},
        "tpa.command.tpa": {"description": "Allows users to use the /tpa command.", "default": True},
        "tpa.command.tpaccept": {"description": "Allows users to use the /tpaccept command.", "default": True},
        "tpa.command.tpdeny": {"description": "Allows users to use the /tpdeny command.", "default": True},
        "tpa.command.tpacancel": {"description": "Allows users to use the /tpacancel command.", "default": True},
        "tpa.command.tpthere": {"description": "Allows users to use the /tpthere command.", "default": True},
        "tpa.command.tpablock": {"description": "Allows users to use the /tpablock command.", "default": True},
    }

    def on_load(self) -> None:
        self.logger.info("TpaPlugin loaded.")
        self.load_config()
        lang_dir = os.path.join(os.path.dirname(__file__), "lang")
        if not os.path.exists(lang_dir):
            self.logger.warning(f"Language directory not found at {lang_dir}")
            return

        for file_name in os.listdir(lang_dir):
            if file_name.endswith(".json"):
                locale = file_name[:-5]
                with open(os.path.join(lang_dir, file_name), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key not in self.translations:
                            self.translations[key] = {}
                        self.translations[key][locale] = value

    def load_config(self):
        config_path = os.path.join(self.data_folder, "config.json")
        default_config = {
            "request-timeout": 60,
            "blocks": {},
        }
        
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            self.plugin_config = default_config
            with open(config_path, 'w') as f:
                json.dump(self.plugin_config, f, indent=4)
        else:
            with open(config_path, 'r') as f:
                self.plugin_config = json.load(f)
        
        self.tpa_blocks = {UUID(k): [UUID(v) for v in val] for k, val in self.plugin_config.get("blocks", {}).items()}

    def on_enable(self) -> None:
        self.logger.info("TPA plugin enabled.")
        self.handlers = preloaded_handlers
        self.register_events(self)
        self.server.scheduler.run_task(self, self.cleanup_expired_requests, delay=20, period=20)

    def cleanup_expired_requests(self):
        current_time = time.time()
        timeout = self.plugin_config.get("request-timeout", 60)
        # Iterate over a copy of the items to allow modification during iteration
        for target_uuid, requests in list(self.tpa_requests.items()):
            for requester_uuid, (timestamp, _) in list(requests.items()):
                if current_time - timestamp > timeout:
                    # Remove the specific expired request
                    requests.pop(requester_uuid)
                    
                    # Notify players if they are online
                    target = self.server.get_player(target_uuid)
                    requester = self.server.get_player(requester_uuid)
                    if target and requester:
                        self._(requester, "tpa.requester_expired", target.name)

            # If a target has no more pending requests, remove the entry
            if not requests:
                self.tpa_requests.pop(target_uuid)

    def on_disable(self) -> None:
        self.logger.info("TPA plugin disabled.")

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in self.handlers:
            handler = self.handlers[command.name]
            return handler(self, sender, args)
        return False
