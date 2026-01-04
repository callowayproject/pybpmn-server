from dataclasses import dataclass

from pybpmn_server.dmn.generated.t_import import TImport

__NAMESPACE__ = "https://www.omg.org/spec/DMN/20240513/MODEL/"


@dataclass
class Import(TImport):
    class Meta:
        name = "import"
        namespace = "https://www.omg.org/spec/DMN/20240513/MODEL/"
