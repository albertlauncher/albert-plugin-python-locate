# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Manuel Schneider

import shlex
import subprocess
from pathlib import Path

from albert import *

md_iid = "3.0"
md_version = "3.1"
md_name = "Locate"
md_description = "Find files using locate"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/albert-plugin-python-locate"
md_bin_dependencies = ["locate"]
md_authors = ["@ManuelSchneid3r"]
md_maintainers = ["@ManuelSchneid3r"]


class Plugin(PluginInstance, TriggerQueryHandler):

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

        self.iconUrls = [
            "xdg:preferences-system-search",
            "xdg:system-search",
            "xdg:search",
            "xdg:text-x-generic",
            f"file:{Path(__file__).parent}/locate.svg"
        ]

    def defaultTrigger(self):
        return "'"

    def handleTriggerQuery(self, query):
        try:
            args = shlex.split(query.string)
        except ValueError:
            return

        if args and all(len(token) > 2 for token in args):

            # Fetch results from locate and filter them using Matcher

            matcher = Matcher(query.string)
            rank_items = []
            with subprocess.Popen(['locate', *args], stdout=subprocess.PIPE, text=True) as proc:
                for line in proc.stdout:
                    if not query.isValid:
                        return

                    path = line.strip()
                    filename = Path(path).name
                    if m := matcher.match(filename, path):
                        rank_items.append(
                            RankItem(
                                StandardItem(
                                    id=path,
                                    text=filename,
                                    subtext=path,
                                    iconUrls=[f"qfip:{path}"],
                                    actions=[
                                        Action("open", "Open", lambda p=path: openUrl("file://%s" % p))
                                    ]
                                ),
                                m
                            )
                        )

            # Filter using the matcher

            rank_items = sorted(rank_items, key=lambda x: x.score, reverse=True)

            if not query.isValid:
                return

            query.add([ri.item for ri in rank_items])

        else:
            query.add(
                StandardItem(
                    id="locate.info",
                    text="Token is too short",
                    subtext="Each token must have at least three characters",
                    iconUrls=self.iconUrls
                )
            )
