"""Printing utilities for pydantic models with support for nested structures."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from typing import Union
from typing import get_args
from typing import get_origin

from pydantic import BaseModel
from rich.console import Console
from rich.tree import Tree

# Optional rich import
try:
    from rich import print as rich_print

    HAS_RICH = True
except ImportError:
    rich_print = print  # type: ignore[assignment]
    HAS_RICH = False

__all__ = ["HAS_RICH", "debug_print", "print_model_tree"]


def debug_print(obj: Any) -> None:
    """Print debug information using rich formatting if available.

    Parameters
    ----------
    obj : Any
        Any object to be printed.
    """
    rich_print(obj)


def _get_type_name(field_type: Any) -> str:
    """Helper function to get the type name with support for complex types."""
    if hasattr(field_type, "__name__"):
        return field_type.__name__

    # Handle string representations of types
    if isinstance(field_type, str):
        if "Annotated[" in field_type:
            base_type = field_type.split("[", 1)[1].rsplit(",", 1)[0]
            return _get_type_name(base_type)
        if "Optional[" in field_type:
            return f"Optional[{field_type.replace('Optional[', '').rstrip(']')}]"
        if "Union[" in field_type:
            types = field_type.split("[", 1)[1].rsplit("]", 1)[0].split(",")
            cleaned_types = [t.strip() for t in types if "NoneType" not in t]
            return f"Union[{', '.join(cleaned_types)}]"
        return field_type

    # Handle typing objects
    origin = get_origin(field_type)
    if origin is not None:
        if origin is Union:
            args = [_get_type_name(arg) for arg in get_args(field_type) if arg is not type(None)]
            return f"Optional[{args[0]}]" if len(args) == 1 else f"Union[{', '.join(args)}]"
        if origin is list:
            args = [_get_type_name(arg) for arg in get_args(field_type)]
            return f"list[{', '.join(args)}]"
        if hasattr(field_type, "_name") and field_type._name:
            args = [_get_type_name(arg) for arg in get_args(field_type)]
            return f"{field_type._name}[{', '.join(args)}]"

    return str(field_type)


def _add_fields_to_tree(  # noqa: C901
    tree: Tree,
    model: BaseModel | Sequence,
    depth: int = 0,
    skip_types: set[str] | None = None,
) -> None:
    """Recursively add fields to the tree, handling nested structures.

    Parameters
    ----------
    tree : Tree
        The rich Tree object to add nodes to
    model : BaseModel | Sequence
        The model or sequence to process
    depth : int, optional
        Current recursion depth to prevent infinite recursion
    skip_types : set[str] | None, optional
        Set of type names to treat as simple types (not expanded)
    """
    if depth > 10:  # Prevent infinite recursion
        tree.add("[red]Max recursion depth reached[/red]")
        return

    # Handle sequences (lists, tuples, etc.)
    if isinstance(model, Sequence) and not isinstance(model, str | bytes):
        if not model:  # Handle empty sequences
            return

        element_type = type(model[0])
        for i, item in enumerate(model):
            if i >= 1 and element_type is type(item):
                tree.add("...")
                break

            if isinstance(item, BaseModel):
                subtree = tree.add(
                    f"[green][{i}][/green]: [purple]{item.__class__.__name__}[/purple]"
                )
                if not (skip_types and item.__class__.__name__ in skip_types):
                    _add_fields_to_tree(subtree, item, depth=depth + 1, skip_types=skip_types)
            else:
                tree.add(f"[{i}]: {type(item).__name__}")
        return

    # Handle BaseModel instances
    if not isinstance(model, BaseModel):
        return

    annotations = model.__annotations__
    for field_name, field_type in annotations.items():
        field_value = getattr(model, field_name, None)

        # Get clean type name
        type_name = _get_type_name(field_type)

        # Handle nested BaseModel instances
        if isinstance(field_value, BaseModel):
            subtree = tree.add(f"[gold3]{field_name}[/gold3]: [purple]{type_name}[/purple]")
            if not (skip_types and field_value.__class__.__name__ in skip_types):
                _add_fields_to_tree(subtree, field_value, depth=depth + 1, skip_types=skip_types)

        # Handle sequences of BaseModels
        elif isinstance(field_value, Sequence) and not isinstance(field_value, str | bytes):
            subtree = tree.add(f"[gold3]{field_name}[/gold3]: [purple]{type_name}[/purple]")
            _add_fields_to_tree(subtree, field_value, depth=depth + 1, skip_types=skip_types)

        # Handle regular fields
        else:
            tree.add(f"[gold3]{field_name}[/gold3]: [green]{type_name}[/green]")


def print_model_tree(model: BaseModel, *, skip_types: tuple[str, ...] = ("BaseImage",)) -> None:
    """Print a tree representation of a Pydantic model including nested structures.

    Parameters
    ----------
    model : BaseModel
        The Pydantic model to visualize
    skip_types : tuple[str, ...], by default ("BaseImage",)
        Tuple of type names to treat as simple types. These types will be shown in the tree
        but their internal structure won't be expanded. For example: ("BaseImage",)
        will show fields of these types but won't show their internal attributes.
        To show all fields, set `skip_types=()`.
    """

    tree = Tree(f"[bold]{model.__class__.__name__}[/bold]")
    _add_fields_to_tree(tree, model, skip_types=set(skip_types))
    console = Console()
    console.print(tree, highlight=True)
