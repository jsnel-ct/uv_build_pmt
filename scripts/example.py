from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from uv_build_pmt.utils.printing import print_model_tree


class Item(BaseModel):
    item_id: int
    value: str


class Module(BaseModel):
    module_id: int
    description: str
    items: list[Item]


class Metadata(BaseModel):
    created: str
    tags: list[str]


class ComplexModel(BaseModel):
    id: int
    name: str
    modules: list[Module]
    metadata: Metadata


def main():
    example_file = Path(__file__).resolve().parent / "example_data.json"
    with example_file.open(encoding="utf-8") as f:
        data = json.load(f)
    model = ComplexModel(**data)
    print_model_tree(model)


if __name__ == "__main__":
    main()
