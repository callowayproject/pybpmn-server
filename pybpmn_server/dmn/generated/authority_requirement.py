from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_authority_requirement import TAuthorityRequirement

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class AuthorityRequirement(TAuthorityRequirement):
    class Meta:
        name = "authorityRequirement"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
