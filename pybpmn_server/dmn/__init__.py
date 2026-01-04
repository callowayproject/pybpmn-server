from bpmn_dmn.dmn.engine.dmn_engine import DMNEngine
from bpmn_dmn.dmn.engine.dmn_parser import DMNParser


class DMNDecisionRunner:
    def __init__(self, path, debug=None):
        self.path = path

        self.dmnParser = DMNParser(self.path)
        self.dmnParser.parse()

        decision = self.dmnParser.decision
        assert len(decision.decision_tables) == 1, "Exactly one decision table should exist! (%s)" % (
            len(decision.decision_tables)
        )

        self.dmnEngine = DMNEngine(decision.decision_tables[0], debug=debug)

    def decide(self, *inputArgs, **inputKwargs):
        return self.dmnEngine.decide(*inputArgs, **inputKwargs)
