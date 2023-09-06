# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""Copy files from external locations as defined in `sync.yml`."""
from __future__ import annotations

import os
from pathlib import Path
from sys import argv
from typing import Any

import yaml
from github import Auth, Github
from jinja2 import Environment, FileSystemLoader
from jsonschema import validate

SCHEMA = {
    "type": "object",
    "patternProperties": {
        r"\w+/\w+": {
            "type": "array",
            "items": {
                "type": ["string", "object"],
                "minLength": 1,
                "properties": {
                    "src": {"type": "string"},
                    "dst": {"type": "string"},
                    "with": {
                        "type": "object",
                        "patternProperties": {
                            r"\w+": {"type": "string"},
                        },
                    },
                },
                "required": ["src"],
            },
        }
    },
}

CONFIG = yaml.load(
    Path(argv[-1]).expanduser().resolve().read_text(),
    Loader=yaml.SafeLoader,
)
validate(CONFIG, schema=SCHEMA)

ENV = Environment(
    loader=FileSystemLoader("./.github/templates"),
    # {{ }} is used in MermaidJS
    # ${{ }} is used in GitHub Actions
    # { } is used in Python
    # %( )s is used in Python
    block_start_string="[%",
    block_end_string="%]",
    variable_start_string="[[",
    variable_end_string="]]",
    comment_start_string="[#",
    comment_end_string="#]",
)

GH = Github(auth=Auth.Token(os.environ.get("GITHUB_TOKEN")))

for repository, files in CONFIG.items():
    repo = GH.get_repo(repository)

    for file in files:
        src: str
        dst: Path
        context: dict[str, Any]

        if isinstance(file, str):
            src = file
            dst = Path(file)
            context = {}
        elif isinstance(file, dict):
            src = file["src"]
            dst = Path(file.get("dst", src))
            context = file.get("with", {})

        content = repo.get_contents(src).decoded_content.decode()
        template = ENV.from_string(content)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(template.render(repo=repo, **context))

        print(f"Templated {repository}/{src} as {dst}")
