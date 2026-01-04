from ast import literal_eval
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import xmltodict

from pybpmn_server.dmn.model import Decision, DecisionTable, Input, InputEntry, Output, OutputEntry, Rule


class DMNParser:
    """Parses a DMN file."""

    DT_FORMAT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, path: Path):
        content = path.read_text(encoding="utf-8")
        self.tree = xmltodict.parse(content)
        self.decision = None

    def parse(self) -> Decision:
        """Parse the DMN file."""
        decision_element = self.tree["definitions"].get("decision", None)
        if decision_element is None:
            raise ValueError("No decisions found")

        if isinstance(decision_element, list):
            raise ValueError("Multiple decisions found")

        decision = Decision(decision_element["@id"], decision_element.get("@name", ""))

        # Parse decision tables
        DMNParser.parse_decision_tables(decision, decision_element)

        return decision

    @staticmethod
    def parse_decision_tables(decision: Decision, decision_element: dict[str, Any]):
        for decision_table_element in decision_element:
            assert decision_table_element.tag.endswith("decisionTable"), (
                'Element %r is not of type "decisionTable"' % (decision_table_element.tag)
            )

            decision_table = DecisionTable(
                decision_table_element.attrib["id"], decision_table_element.attrib.get("name", "")
            )
            decision.decision_tables.append(decision_table)

            # parse inputs
            DMNParser.__parseInputsOutputs(decision, decision_table, decision_table_element)

    @staticmethod
    def __parseInputsOutputs(decision, decisionTable, decisionTableElement):
        for element in decisionTableElement:
            if element.tag.endswith("input"):
                input = DMNParser.__parseInput(element)
                decisionTable.inputs.append(input)
            elif element.tag.endswith("output"):
                output = DMNParser.__parseOutput(element)
                decisionTable.outputs.append(output)
            elif element.tag.endswith("rule"):
                rule = DMNParser.__parseRule(decision, decisionTable, element)
                decisionTable.rules.append(rule)
            else:
                raise Exception("Unknown type in decision table: %r" % (element.tag))

    @staticmethod
    def __parseInput(inputElement):
        typeRef = None
        for inputExpression in inputElement:
            assert inputExpression.tag.endswith("inputExpression"), 'Element %r is not of type "inputExpression"' % (
                inputExpression.tag
            )

            typeRef = inputExpression.attrib.get("typeRef", "")

        input = Input(
            inputElement.attrib["id"],
            inputElement.attrib.get("label", ""),
            inputElement.attrib.get("name", ""),
            typeRef,
        )
        return input

    @staticmethod
    def __parseOutput(outputElement):
        output = Output(
            outputElement.attrib["id"],
            outputElement.attrib.get("label", ""),
            outputElement.attrib.get("name", ""),
            outputElement.attrib.get("typeRef", ""),
        )
        return output

    @staticmethod
    def __parseRule(decision, decisionTable, ruleElement):
        rule = Rule(ruleElement.attrib["id"])

        inputIdx = 0
        outputIdx = 0
        for child in ruleElement:
            # Load description
            if child.tag.endswith("description"):
                rule.description = child.text

            # Load input entries
            elif child.tag.endswith("inputEntry"):
                inputEntry = DMNParser.parse_input_output_element(decision, decisionTable, child, InputEntry, inputIdx)
                rule.input_entries.append(inputEntry)
                inputIdx += 1

            # Load output entries
            elif child.tag.endswith("outputEntry"):
                outputEntry = DMNParser.parse_input_output_element(
                    decision, decisionTable, child, OutputEntry, outputIdx
                )
                rule.output_entries.append(outputEntry)
                outputIdx += 1

        return rule

    @staticmethod
    def parse_input_output_element(decision, decision_table: DecisionTable, element, cls: type, idx: int):
        input_or_output = (
            decision_table.inputs if cls == InputEntry else decision_table.outputs if cls == OutputEntry else None
        )[idx]
        entry = cls(element.attrib["id"], input_or_output)

        for child in element:
            if child.tag.endswith("description"):
                entry.description = child.text
            elif child.tag.endswith("text"):
                entry.text = child.text

                if cls == InputEntry:
                    entry.operators = list(DMNParser.parse_ref(input_or_output.typeRef, entry.text))
                elif cls == OutputEntry:
                    operators = list(DMNParser.parse_ref(input_or_output.typeRef, entry.text))
                    assert len(operators) <= 1, (
                        "Normally it is impossible to have multiple values as output column! %s: %r"
                        % (input_or_output.typeRef, entry.text)
                    )
                    entry.parsed_value = operators[0][1]
                else:
                    raise NotImplementedError(cls.__name__)

        return entry

    @staticmethod
    def parse_ref(type_ref: str, val: str) -> list[tuple[str, Any]]:
        """
        Parses a given value based on its type reference and returns a list of parsed tuples.

        Args:
            type_ref: The type reference that indicates the expected type of the input value. Supported types
                include "string", "boolean", "integer", "long", "double", and "date".
            val: The value to be parsed.

        Returns:
            A list of tuples containing the parsed value(s). Each tuple consists of a string identifier and the
                corresponding parsed value.

        Raises:
            NotImplementedError: If the method does not support the provided type_ref.
        """
        if val is None:
            return []

        if type_ref == "string":
            return DMNParser.parse_string(val)

        elif type_ref == "boolean":
            return DMNParser.parse_boolean(val)

        elif type_ref == "integer":
            return DMNParser.parse_integer(val)

        elif type_ref in ("long", "double"):
            return DMNParser.parse_long_or_double(val)

        elif type_ref == "date":
            return DMNParser.parse_date(val)

        else:
            raise NotImplementedError(type_ref)

    @staticmethod
    def parse_string(val: str) -> list[tuple[str, str]]:
        """
        Parses a string value in DMN format and returns a list of tuples representing the parsed comparison.
        """
        not_ = False
        if "not" in val:
            not_ = True
            val = val.replace("not(", "").replace(")", "")

        return [("!=" if not_ else "==", literal_eval(val))]

    @staticmethod
    def parse_boolean(val: str) -> list[tuple[str, bool]]:
        """
        Parses a boolean value in DMN format.
        """
        return [("==", bool(val.lower() == "true"))]

    @staticmethod
    def parse_integer(val: str) -> list[tuple[str, int]]:
        """
        Parses an integer value in DMN format and returns a list of tuples representing the parsed range or comparison.
        """
        if ".." in val:
            int_str_frm, int_str_to = val[1:-1].split("..")
            return [
                (">=" if val[0] == "[" else ">", int(int_str_frm)),
                ("<=" if val[-1] == "]" else "<", int(int_str_to)),
            ]
        elif val.startswith(("<", ">", "=")):
            vals = val.split(" ")
            return [(vals[0], int(vals[1]))]
        else:
            return [("==", int(val))]

    @staticmethod
    def parse_long_or_double(val: str) -> list[tuple[str, Decimal]]:
        """
        Parses a long or double value in DMN format to a list of tuples representing the parsed range or comparison.
        """
        if ".." in val:
            int_str_frm, int_str_to = val[1:-1].split("..")
            return [
                (">=" if val[0] == "[" else ">", Decimal(int_str_frm)),
                ("<=" if val[-1] == "]" else "<", Decimal(int_str_to)),
            ]
        elif val.startswith(("<", ">", "=")):
            vals = val.split(" ")
            return [(vals[0], Decimal(vals[1]))]
        else:
            return [("==", Decimal(val))]

    @staticmethod
    def parse_date(val: str) -> list[tuple[str, datetime]]:
        """
        Parses a date string in DMN format to a list of tuples representing the parsed date range or comparison.
        """
        if ".." in val:
            # Example: [date and time("2017-11-03T00:00:00")..date and time("2017-11-04T23:59:59")]
            dt_str_frm, dt_str_to = val[1:-1].split("..")
            dt_frm = DMNParser.parse_date_str(dt_str_frm)
            dt_to = DMNParser.parse_date_str(dt_str_to)
            return [
                (">=" if val[0] == "[" else ">", dt_frm),
                ("<=" if val[-1] == "]" else "<", dt_to),
            ]
        elif val.startswith((">", "<")):
            # Example: > date and time("2017-11-03T00:00:00")
            # Example: < date and time("2017-11-03T00:00:00")
            operator, dt_str = val.split(" ", 1)
            dt = DMNParser.parse_date_str(dt_str)
            return [(operator, dt)]
        else:
            return [("==", DMNParser.parse_date_str(val))]

    @staticmethod
    def parse_date_str(val: str) -> datetime:
        """
        Parses a date string in DMN format to a datetime object.

        Args:
            val: The date string in DMN format.

        Returns:
            The parsed datetime object.
        """
        # Example: date and time("2017-11-03T00:00:00")
        dt_str_val = val.replace('date and time("', "").replace('")', "")
        return datetime.strptime(dt_str_val, DMNParser.DT_FORMAT)
