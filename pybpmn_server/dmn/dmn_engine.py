"""
DMN Engine for evaluating decision tables based on input data.

Based on: https://github.com/labsolutionlu/bpmn_dmn

This module provides a DMNEngine class for evaluating decision tables against input data.
It supports various input types and operators, and logs debug information if enabled.
"""

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class DMNEngine:
    def __init__(self, decision_table, debug=None):
        self.decision_table = decision_table
        self.debug = debug

    def decide(self, *args, **kwargs):
        for rule in self.decision_table.rules:
            self.logger.debug("Checking rule {} ({})...".format(rule.id, rule.description))

            res = self.__checkRule(rule, *args, **kwargs)
            self.logger.debug(" Match? %s" % (res))
            if res:
                self.logger.debug(" Return {} ({})".format(rule.id, rule.description))
                return rule

    def __checkRule(self, rule, *inputData, **inputKwargs):
        for idx, inputEntry in enumerate(rule.input_entries):
            input = self.decision_table.inputs[idx]

            self.logger.debug(
                " Checking input entry {} ({}: {})...".format(inputEntry.id, input.label, inputEntry.operators)
            )

            for operator, parsedValue in inputEntry.operators:
                if parsedValue is not None:
                    inputVal = DMNEngine.__getInputVal(inputEntry, idx, *inputData, **inputKwargs)
                    if isinstance(parsedValue, Decimal) and not isinstance(inputVal, Decimal):
                        self.logger.warning("Attention, you are comparing a Decimal with %r" % (type(inputVal)))

                    expression = "{!r} {} {!r}".format(inputVal, operator, parsedValue)

                    self.logger.debug(" Evaludation expression: %s" % (expression))
                    if not eval(expression):
                        return False  # Value does not match
                    else:
                        continue  # Check the other operators/columns
                else:
                    # Empty means ignore decision value
                    self.logger.debug(" Value not defined")
                    continue  # Check the other operators/columns

        self.logger.debug(" All inputs checked")
        return True

    @staticmethod
    def __getInputVal(inputEntry, idx, *inputData, **inputKwargs):
        """
        The input of the decision method can be args or kwargs.
        This function tries to extract the input data from args if passed,
         otherwise from kwargs using the label of the decision input column as mapping

        :param inputEntry:
        :param idx:
        :param inputData:
        :param inputKwargs:
        :return:
        """
        return (
            inputData[idx] if inputData else inputKwargs[inputEntry.input.label]
        )  # TODO (pybpmn-server-s8w): Check if label is correct in dmn_engine.py
