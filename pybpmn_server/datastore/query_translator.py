"""Query translator for filtering items in a data store."""

from typing import Any, Dict, List


def eval_gte(val: Any, term: Any) -> bool:
    """Evaluates if val is greater than or equal to term."""
    return (val is not None) and (val >= term)


def eval_gt(val: Any, term: Any) -> bool:
    """Evaluates if val is greater than term."""
    return (val is not None) and (val > term)


def eval_eq(val: Any, term: Any) -> bool:
    """Evaluates if val is equal to term."""
    return val == term


def eval_lte(val: Any, term: Any) -> bool:
    """Evaluates if val is less than or equal to term."""
    return (val is not None) and (val <= term)


def eval_lt(val: Any, term: Any) -> bool:
    """Evaluates if val is less than term."""
    return (val is not None) and (val < term)


def eval_exists(val: Any, term: bool) -> bool:
    """Evaluates if val exists and is supposed to be there."""
    return bool(val and term)


def eval_in(val: Any, term: Any) -> bool:
    """Evaluates if val is in term."""
    return (isinstance(term, list) and val in term) or (isinstance(val, list) and term in val)


def eval_false(val: Any, term: Any) -> bool:
    """Always returns false."""
    return False


COMPLEX_CONDITIONS = {
    "$gte": eval_gte,
    "$gt": eval_gt,
    "$eq": eval_eq,
    "$lte": eval_lte,
    "$lt": eval_lt,
    "$exists": eval_exists,
    "$in": eval_in,
}


def _parse_complex_condition(condition: Dict[str, Any], val: Any) -> bool:
    """
    Parses and evaluates a complex condition against a given value.

    This function iterates through a dictionary representing complex conditions,
    applies predefined evaluation functions from COMPLEX_CONDITIONS, and ensures
    that all conditions are satisfied for the given value.

    Args:
        condition: A dictionary where keys represent condition names  and values represent their
            respective terms to be evaluated.
        val: The value to evaluate against the provided conditions.

    Returns:
        True if all conditions are satisfied, otherwise False.
    """
    for cond, term in condition.items():
        ret = COMPLEX_CONDITIONS.get(cond, eval_false)(val, term)

        if not ret:
            return False
    return True


def _evaluate_value(item: Any, key: str, cond: Any) -> bool:
    """
    Evaluates a value from the provided item based on the specified key and condition.

    This function retrieves a value from an item (dictionary or object) by extracting
    it using the given key. Keys can be nested and separated by dots, which allows accessing
    deeply nested values. Once the value is retrieved, it evaluates the value against the
    provided condition to determine whether it matches certain criteria.

    Args:
        item: The source object or dictionary from which the value will be retrieved. It can include nested structures.
        key: The key used to extract the value from the item. Dots should separate nested keys.
        cond: The condition to evaluate against the retrieved value. It can be a basic value, a list of values, or a
            dictionary defining complex conditions.

    Returns:
        True if the retrieved value satisfies the condition provided, False otherwise.
    """
    val = item
    if "." in key:
        for k in key.split("."):
            if isinstance(val, dict) and k in val:
                val = val[k]
            elif hasattr(val, k):
                val = getattr(val, k)
            else:
                val = None
                break
    else:
        val = item.get(key) if isinstance(item, dict) else getattr(item, key, None)

    if isinstance(cond, dict):
        return _parse_complex_condition(cond, val)

    if isinstance(val, list):
        if isinstance(cond, list):
            return any(r in cond for r in val)
        else:
            return cond in val

    if cond is None and val is None:
        return True
    else:
        return val == cond


def _evaluate_condition(item: Any, condition: Dict[str, Any]) -> bool:
    """Evaluates a condition against an item."""
    return all(_evaluate_value(item, key, cond) for key, cond in condition.items())


class QueryTranslator:
    """
    Translates MongoDB query criteria into a format suitable for filtering items in a data store.

    Input Query:

    ```json
    {
        "items.status": "wait",
        "name": "Buy Used Car with Lanes",
        "$or": [
            {"items.candidateGroups": "Owner"},
            {"items.candidateUsers": "User1"}
        ]
    }
    ```

    MongoQuery:

    ```json
    {
        "name": "Buy Used Car with Lanes",
        "$or": [
            {"items":{"$elemMatch":{"candidateGroups":"Owner"}}},
            {"items":{"$elemMatch":{"candidateUsers":"User1"}}}
        ],
        "items":{"$elemMatch":{"status":"wait"}
    }
    ```

    And filter items by performing the Query on each Instance Item

    Supported Operators:
    - $or
    - $lte
    - $lt
    - $gte
    - $gt
    - $eq

    Missing the following:
    - $ne
    - $regex
    - $in
    - $and

    https://www.mongodb.com/docs/manual/reference/mql/query-predicates/
    """

    def __init__(self, child_name: str):
        self.child_name = child_name

    def translate_criteria(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a query dictionary by analyzing and modifying its structure based on specific criteria.

        This method parses the incoming query dictionary to identify and handle special keys such as "$or"
        and keys associated with the child name. Keys starting with the child name are converted so that
        they can be matched using MongoDB's `$elemMatch` operator. The transformation allows for more
        flexible and detailed querying on nested structures.

        Args:
            query: The original query dictionary to be transformed.

        Returns:
            A new query dictionary with transformed keys and structure.
        """
        match = {}
        has_match = False
        new_query: Dict[str, Any] = {}

        for key, val in query.items():
            if key == "$or":
                predicates = [self.translate_criteria(predicate) for predicate in val]
                new_query["$or"] = predicates
            elif key.startswith(f"{self.child_name}."):
                new_key = key.replace(f"{self.child_name}.", "")
                match[new_key] = val
                has_match = True
            else:
                new_query[key] = val

        if has_match:
            new_query[self.child_name] = {"$elemMatch": match}

        return new_query

    def _filter_or(self, item: Any, condition: List[Dict[str, Any]]) -> bool:
        return any(self.filter_item(item, c) for c in condition)

    def filter_item(self, item: Any, query: Dict[str, Any]) -> bool:
        """Filters an item based on a query dictionary."""
        pass_ = True
        for key, condition in query.items():
            if key == self.child_name:
                pass_ = _evaluate_condition(item, condition.get("$elemMatch", {}))
            elif key == "$or":
                pass_ = self._filter_or(item, condition)
            else:
                # Top level fields not related to child_name are handled differently or ignored here?
                # In TS, it seems to just continue. If it's not $or or child_name, it's not clear what it does.
                # Actually, in TS `evaluateValue` handles regular keys too.
                pass_ = _evaluate_value(item, key, condition)

            if not pass_:
                break
        return pass_
