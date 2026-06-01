"""
YAML front-matter parsing for topic files.
"""

import re
from pathlib import Path
from typing import Any

import yaml


def extract_front_matter(content: str) -> tuple[dict[str, Any], str]:
    """
    Extract YAML front matter from markdown content.

    Returns:
        tuple of (front_matter_dict, body_content)
    """
    front_matter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*(\n|$)", re.DOTALL)
    match = front_matter_pattern.match(content)

    if match:
        front_matter_text = match.group(1)
        body = content[match.end() :]
        try:
            front_matter = yaml.safe_load(front_matter_text)
            return (front_matter if front_matter else {}, body)
        except yaml.YAMLError:
            raise

    return ({}, content)


def parse_topic_file(path: Path) -> tuple[dict[str, Any], str]:
    """
    Read a topic .md file and extract front matter and body.

    Returns:
        tuple of (front_matter_dict, body_content)

    Raises:
        FileNotFoundError: if the topic file does not exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Topic file not found: {path}")

    content = path.read_text(encoding="utf-8")
    try:
        return extract_front_matter(content)
    except yaml.YAMLError:
        raise yaml.YAMLError(f"Failed to parse YAML front matter in {path}")