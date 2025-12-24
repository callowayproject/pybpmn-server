from typing import Any

import pytest

from pybpmn_server.datastore.query_translator import (
    QueryTranslator,
    _evaluate_condition,  # noqa: PLC2701
    _evaluate_value,  # noqa: PLC2701
    _parse_complex_condition,  # noqa: PLC2701
    eval_eq,
    eval_exists,
    eval_false,
    eval_gt,
    eval_gte,
    eval_in,
    eval_lt,
    eval_lte,
)


class TestEvalGte:
    def test_returns_true_if_value_is_greater_than_term(self):
        # We want to ensure that values greater than the term return True.
        assert eval_gte(10, 5) is True

    def test_returns_true_if_value_is_equal_to_term(self):
        # We want to ensure that values equal to the term return True.
        assert eval_gte(5, 5) is True

    def test_returns_false_if_value_is_less_than_term(self):
        # We want to ensure that values less than the term return False.
        assert eval_gte(3, 5) is False

    def test_returns_false_if_value_is_none(self):
        # We want to ensure that if the value is None, it returns False even if the term is also None or something else.
        assert eval_gte(None, 5) is False


class TestEvalGt:
    def test_returns_true_if_value_is_greater_than_term(self):
        # We want to ensure that values greater than the term return True.
        assert eval_gt(10, 5) is True

    def test_returns_false_if_value_is_equal_to_term(self):
        # We want to ensure that values equal to the term return False.
        assert eval_gt(5, 5) is False

    def test_returns_false_if_value_is_less_than_term(self):
        # We want to ensure that values less than the term return False.
        assert eval_gt(3, 5) is False

    def test_returns_false_if_value_is_none(self):
        # We want to ensure that if the value is None, it returns False.
        assert eval_gt(None, 5) is False


class TestEvalEq:
    def test_returns_true_if_value_is_equal_to_term(self):
        # We want to ensure that equal values return True.
        assert eval_eq(5, 5) is True

    def test_returns_false_if_value_is_not_equal_to_term(self):
        # We want to ensure that non-equal values return False.
        assert eval_eq(5, 10) is False

    def test_returns_true_if_both_are_none(self):
        # We want to ensure that if both value and term are None, they are considered equal.
        assert eval_eq(None, None) is True


class TestEvalLte:
    def test_returns_true_if_value_is_less_than_term(self):
        # We want to ensure that values less than the term return True.
        assert eval_lte(3, 5) is True

    def test_returns_true_if_value_is_equal_to_term(self):
        # We want to ensure that values equal to the term return True.
        assert eval_lte(5, 5) is True

    def test_returns_false_if_value_is_greater_than_term(self):
        # We want to ensure that values greater than the term return False.
        assert eval_lte(10, 5) is False

    def test_returns_false_if_value_is_none(self):
        # We want to ensure that if the value is None, it returns False.
        assert eval_lte(None, 5) is False


class TestEvalLt:
    def test_returns_true_if_value_is_less_than_term(self):
        # We want to ensure that values less than the term return True.
        assert eval_lt(3, 5) is True

    def test_returns_false_if_value_is_equal_to_term(self):
        # We want to ensure that values equal to the term return False.
        assert eval_lt(5, 5) is False

    def test_returns_false_if_value_is_greater_than_term(self):
        # We want to ensure that values greater than the term return False.
        assert eval_lt(10, 5) is False

    def test_returns_false_if_value_is_none(self):
        # We want to ensure that if the value is None, it returns False.
        assert eval_lt(None, 5) is False


class TestEvalExists:
    def test_returns_true_if_val_exists_and_term_is_true(self):
        # We want to ensure that if both value and term are truthy, it returns True.
        assert eval_exists("something", True) is True

    def test_returns_false_if_val_is_none_and_term_is_true(self):
        # We want to ensure that if the value is None, it returns False even if we are checking for existence.
        assert eval_exists(None, True) is False

    def test_returns_false_if_val_exists_but_term_is_false(self):
        # We want to ensure that if the term is False (meaning we might be checking for non-existence), it returns False.
        assert eval_exists("something", False) is False


class TestEvalIn:
    def test_returns_true_if_val_is_in_term_list(self):
        # We want to ensure that if the value is an element of the term list, it returns True.
        assert eval_in(1, [1, 2, 3]) is True

    def test_returns_true_if_term_is_in_val_list(self):
        # We want to ensure that if the term is an element of the value list, it returns True.
        assert eval_in([1, 2, 3], 1) is True

    def test_returns_false_if_val_is_not_in_term_list(self):
        # We want to ensure that if the value is not in the term list, it returns False.
        assert eval_in(4, [1, 2, 3]) is False

    def test_returns_false_if_neither_is_list(self):
        # We want to ensure that if neither argument is a list, it returns False according to the implementation.
        assert eval_in(1, 2) is False


class TestEvalFalse:
    def test_always_returns_false(self):
        # We want to ensure that this function always returns False regardless of input.
        assert eval_false(Any, Any) is False


class TestParseComplexCondition:
    def test_returns_true_if_all_conditions_satisfied(self):
        # We want to ensure that multiple conditions are all checked and return True if they all pass.
        condition = {"$gt": 5, "$lt": 15}
        assert _parse_complex_condition(condition, 10) is True

    def test_returns_false_if_one_condition_fails(self):
        # We want to ensure that if any one of the conditions fails, the whole check returns False.
        condition = {"$gt": 5, "$lt": 15}
        assert _parse_complex_condition(condition, 20) is False

    def test_returns_false_for_unknown_operator(self):
        # We want to ensure that an unknown operator results in a False evaluation via eval_false.
        condition = {"$unknown": 5}
        assert _parse_complex_condition(condition, 5) is False


class TestEvaluateValue:
    def test_evaluates_simple_key_in_dict(self):
        # We want to ensure that it correctly retrieves a value from a dictionary by key.
        item = {"name": "test"}
        assert _evaluate_value(item, "name", "test") is True

    def test_evaluates_nested_key_in_dict(self):
        # We want to ensure that dot-notation can be used to access nested dictionary values.
        item = {"nested": {"key": "value"}}
        assert _evaluate_value(item, "nested.key", "value") is True

    def test_evaluates_attribute_on_object(self):
        # We want to ensure that it can also retrieve values from object attributes.
        class Obj:
            def __init__(self):
                self.name = "test"

        item = Obj()
        assert _evaluate_value(item, "name", "test") is True

    def test_evaluates_nested_attribute_on_object(self):
        # We want to ensure that dot-notation works for nested object attributes.
        class Nested:
            def __init__(self):
                self.key = "value"

        class Obj:
            def __init__(self):
                self.nested = Nested()

        item = Obj()
        assert _evaluate_value(item, "nested.key", "value") is True

    def test_returns_false_if_key_not_found(self):
        # We want to ensure that if a key is missing, it evaluates to None and thus might fail equality.
        item = {"name": "test"}
        assert _evaluate_value(item, "missing", "test") is False

    def test_returns_true_if_both_none(self):
        # We want to ensure that if both the retrieved value and the condition are None, it returns True.
        item = {"name": None}
        assert _evaluate_value(item, "name", None) is True

    def test_handles_complex_condition_dict(self):
        # We want to ensure that if the condition is a dictionary, it's treated as a complex condition.
        item = {"age": 20}
        assert _evaluate_value(item, "age", {"$gt": 18}) is True

    def test_handles_val_list_cond_list_intersection(self):
        # We want to ensure that if both value and condition are lists, it checks for intersection.
        item = {"tags": ["a", "b"]}
        assert _evaluate_value(item, "tags", ["b", "c"]) is True

    def test_handles_val_list_cond_scalar_inclusion(self):
        # We want to ensure that if the value is a list and condition is a scalar, it checks for inclusion.
        item = {"tags": ["a", "b"]}
        assert _evaluate_value(item, "tags", "a") is True


class TestEvaluateCondition:
    def test_returns_true_if_all_key_conditions_match(self):
        # We want to ensure that all conditions in the condition dictionary must match for the item.
        item = {"name": "test", "age": 20}
        condition = {"name": "test", "age": {"$gt": 18}}
        assert _evaluate_condition(item, condition) is True

    def test_returns_false_if_any_key_condition_fails(self):
        # We want to ensure that if any one of the key-based conditions fails, the whole thing is False.
        item = {"name": "test", "age": 15}
        condition = {"name": "test", "age": {"$gt": 18}}
        assert _evaluate_condition(item, condition) is False


class TestQueryTranslatorTranslateCriteria:
    def test_translates_simple_query(self):
        # We want to ensure that a simple query without special keys remains unchanged.
        qt = QueryTranslator("items")
        query = {"name": "test"}
        expected = {"name": "test"}
        assert qt.translate_criteria(query) == expected

    def test_translates_query_with_child_name_prefix(self):
        # We want to ensure that keys prefixed with child_name are moved into an $elemMatch.
        qt = QueryTranslator("items")
        query = {"items.status": "wait"}
        expected = {"items": {"$elemMatch": {"status": "wait"}}}
        assert qt.translate_criteria(query) == expected

    def test_translates_query_with_or_operator(self):
        # We want to ensure that $or operator is recursively translated.
        qt = QueryTranslator("items")
        query = {"$or": [{"items.status": "wait"}, {"name": "test"}]}
        expected = {"$or": [{"items": {"$elemMatch": {"status": "wait"}}}, {"name": "test"}]}
        assert qt.translate_criteria(query) == expected

    def test_translates_multiple_child_keys_into_single_elemmatch(self):
        # We want to ensure that multiple keys with the child_name prefix are combined into one $elemMatch.
        qt = QueryTranslator("items")
        query = {"items.status": "wait", "items.type": "task"}
        expected = {"items": {"$elemMatch": {"status": "wait", "type": "task"}}}
        assert qt.translate_criteria(query) == expected


class TestQueryTranslatorFilterOr:
    def test_returns_true_if_any_condition_is_met(self, mocker):
        """We want to ensure that _filter_or returns True if at least one of its conditions matches the item."""
        qt = QueryTranslator("items")
        item = {"name": "test"}
        conditions = [{"name": "wrong"}, {"name": "test"}]
        # Mock filter_item to control its return value
        mock_filter = mocker.patch.object(qt, "filter_item")
        mock_filter.side_effect = [False, True]

        assert qt._filter_or(item, conditions) is True
        assert mock_filter.call_count == 2

    def test_returns_false_if_no_conditions_are_met(self, mocker):
        """We want to ensure that _filter_or returns False if none of its conditions match."""
        qt = QueryTranslator("items")
        item = {"name": "test"}
        conditions = [{"name": "wrong1"}, {"name": "wrong2"}]
        mock_filter = mocker.patch.object(qt, "filter_item")
        mock_filter.return_value = False

        assert qt._filter_or(item, conditions) is False


class TestQueryTranslatorFilterItem:
    """
    Test suite for the filter_item method of QueryTranslator.
    """

    def test_filters_by_child_name_using_elemmatch(self):
        """We want to ensure that filter_item correctly handles the child_name key using _evaluate_condition."""
        qt = QueryTranslator("items")
        # In this implementation, 'item' itself is passed to _evaluate_condition when child_name matches.
        # This seems to assume 'item' is the element that should match the $elemMatch criteria.
        item = {"status": "wait"}
        query = {"items": {"$elemMatch": {"status": "wait"}}}
        assert qt.filter_item(item, query) is True

    def test_filters_by_or_operator(self):
        """We want to ensure that filter_item correctly delegates $or conditions to _filter_or."""
        qt = QueryTranslator("items")
        item = {"name": "test"}
        query = {"$or": [{"name": "test"}, {"name": "other"}]}
        assert qt.filter_item(item, query) is True

    def test_filters_by_regular_key(self):
        """We want to ensure that regular keys are evaluated using _evaluate_value."""
        qt = QueryTranslator("items")
        item = {"name": "test"}
        query = {"name": "test"}
        assert qt.filter_item(item, query) is True

    def test_returns_false_if_any_top_level_condition_fails(self):
        """We want to ensure that all top-level conditions in the query must be satisfied."""
        qt = QueryTranslator("items")
        item = {"name": "test", "status": "active"}
        query = {"name": "test", "status": "inactive"}
        assert qt.filter_item(item, query) is False
