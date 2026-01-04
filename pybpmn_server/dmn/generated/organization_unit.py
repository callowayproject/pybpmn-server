from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_organization_unit import TOrganizationUnit

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class OrganizationUnit(TOrganizationUnit):
    class Meta:
        name = "organizationUnit"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
