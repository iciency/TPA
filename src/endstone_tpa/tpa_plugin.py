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
    }

    def on_load(self) -> None:
        self.logger.info("TpaPlugin loaded.")
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

    def on_enable(self) -> None:
        self.logger.info("TPA plugin enabled.")
        self.handlers = preloaded_handlers
        self.register_events(self)

    def on_disable(self) -> None:
        self.logger.info("TPA plugin disabled.")

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in self.handlers:
            handler = self.handlers[command.name]
            return handler(self, sender, args)
        return False
