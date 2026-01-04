"""General utility functions."""

from importlib import import_module


def import_string(dotted_path: str) -> type:
    """
    Import a dotted module path and return the attribute/class designated by the last name in the path.

    Raises:
        ImportError: if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)
    return getattr(module, class_name)
