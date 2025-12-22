"""Data handling utilities."""

from typing import Any, Optional


def merge_data(
    instance_data: list | dict,
    input_data: Any,
    item: Any,
    data_path: Optional[str] = None,
) -> None:
    """
    Merges input data into a target within instance data, potentially handling array and dictionary structures.

    This is useful for dynamically populating or updating data hierarchies based on the provided parameters.

    Args:
        instance_data: The main data structure into which data will be merged.
            This can be a dictionary or a list that forms the hierarchical structure.
        input_data: The data to be merged into the instance data, which can be a list,
            dictionary, or other compatible data type.
        item: An object containing contextual information that may include tokens
            for error reporting or other auxiliary data like variable mappings.
        data_path: Optional path within the instance data indicating where
            the input data should be merged. Paths may include special syntax (e.g., "[]")
            for lists.
    """
    as_array = False

    if isinstance(input_data, list) or bool(data_path and data_path.endswith("[]")):
        as_array = True

    target = get_and_create_data(instance_data, data_path, as_array)

    if target is None:
        if item and hasattr(item, "token") and item.token:
            item.token.error("*** Error *** target is not defined")
        return

    if not input_data:
        return

    if as_array:
        if isinstance(target, list):
            target.append(input_data)
    else:
        if isinstance(input_data, dict):
            # We need to iterate over a copy of keys because we might delete keys from input_data
            for key in list(input_data.keys()):
                val = input_data[key]
                if key.startswith("vars."):
                    del input_data[key]
                    if item and hasattr(item, "vars"):
                        item.vars[key[5:]] = val
                else:
                    target[key] = val


def get_data(instance_data: Any, data_path: Optional[str]) -> Any:
    """Legacy wrapper for DataHandler.get_data."""
    target = instance_data

    if not data_path:
        return target

    for path_segment in data_path.split("."):
        # strip off []
        segment_name = path_segment.replace("[]", "")
        if segment_name:
            if isinstance(target, dict) and segment_name in target:
                target = target[segment_name]
            else:
                return None
    return target


def get_and_create_data(instance_data: Any, data_path: Optional[str], as_array: bool = False) -> Any:
    """
    Fetches nested data within a dictionary based on a specified path.

    Creates missing nested dictionaries if they do not exist.
    """
    target = instance_data

    if not data_path:
        return target

    parts = data_path.split(".")

    for i, part in enumerate(parts):
        if not part:
            continue
        part_name = part.replace("[]", "")
        if part_name not in target:
            if i == len(parts) - 1 and as_array:
                target[part_name] = []
            else:
                target[part_name] = {}
        target = target[part_name]

    return target
