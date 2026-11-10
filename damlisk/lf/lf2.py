# Copyright 2026 DIGIAPP LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
from dataclasses import dataclass, field

from dazl._gen.com.digitalasset.daml.lf.archive import daml_lf2_pb2 as pb2
from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.parse_factory.pb_v1 import ProtobufParser117
from dazl.damlast.parse_factory.pb_v2 import ProtobufParser21
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from google.protobuf.message import Message


@dataclass(frozen=True)
class Implements:
    template: lf.TypeConName
    interface: lf.TypeConName
    methods: dict[str, lf.Expr]
    view: lf.Expr
    location: lf.Location | None


@dataclass(frozen=True)
class DefException:
    name: lf.TypeConName
    message: lf.Expr
    location: lf.Location | None


@dataclass
class Extras:
    implements: list[Implements] = field(default_factory=list)
    exceptions: list[DefException] = field(default_factory=list)


def apply_type(head: lf.Type, arg: lf.Type) -> lf.Type:
    if head.var is not None:
        return lf.Type(var=lf.Type.Var(head.var.var, (*head.var.args, arg)))
    if head.con is not None:
        return lf.Type(con=lf.Type.Con(head.con.tycon, (*head.con.args, arg)))
    if head.prim is not None:
        return lf.Type(prim=lf.Type.Prim(head.prim.prim, (*head.prim.args, arg)))
    if head.syn is not None:
        return lf.Type(syn=lf.Type.Syn(head.syn.tysyn, (*head.syn.args, arg)))
    raise ValueError(f"cannot apply a type argument to {head!r}")


def enum_name(enum: EnumTypeWrapper, value: int) -> str:
    try:
        return enum.Name(value)
    except ValueError:
        return f"UNKNOWN_{value}"


class Parser1(ProtobufParser117):
    def __init__(self, current_package: lf.PackageRef) -> None:
        super().__init__(current_package)
        self.extras = Extras()


class Parser23(ProtobufParser21):
    def __init__(self, current_package: lf.PackageRef) -> None:
        super().__init__(current_package)
        self.imports: list[str] = []
        self.kinds: list[Message] = []
        self.exprs: list[Message] = []
        self.extras = Extras()

    def parse_Package(self, pb):
        self.imports = list(pb.package_imports.imported_packages)
        self.kinds, self.exprs = list(pb.interned_kinds), list(pb.interned_exprs)
        return super().parse_Package(pb)

    def parse_ModuleId(self, pb):
        if pb.package_id.WhichOneof("Sum") != "package_import_id":
            return super().parse_ModuleId(pb)
        package = lf.PackageRef(self.imports[pb.package_id.package_import_id])
        name = lf.DottedName(self.interned_dotted_names[pb.module_name_interned_dname])
        return lf.ModuleRef(package, name)

    def parse_Kind(self, pb):
        if pb.WhichOneof("Sum") == "interned_kind":
            return self.parse_Kind(self.kinds[pb.interned_kind])
        return super().parse_Kind(pb)

    def parse_Expr(self, pb):
        if pb.WhichOneof("Sum") == "interned_expr":
            return self.parse_Expr(self.exprs[pb.interned_expr])
        return super().parse_Expr(pb)

    def parse_Type(self, pb):
        if pb.WhichOneof("Sum") == "tapp":
            return apply_type(self.parse_Type(pb.tapp.lhs), self.parse_Type(pb.tapp.rhs))
        return super().parse_Type(pb)

    def parse_BuiltinLit(self, pb):
        if pb.WhichOneof("Sum") == "failure_category":
            return lf.PrimLit(text=pb.FailureCategory.Name(pb.failure_category))
        return super().parse_BuiltinLit(pb)

    def parse_BuiltinFunction(self, pb):
        return enum_name(pb2.BuiltinFunction, pb)

    def parse_BuiltinType(self, pb):
        name = enum_name(pb2.BuiltinType, pb)
        return lf.PrimType[name] if name in lf.PrimType.__members__ else name

    def parse_Update(self, pb):
        return super().parse_Update(pb) if pb.WhichOneof("Sum") else None

    def parse_DefTemplate(self, pb):
        tmpl = super().parse_DefTemplate(pb)
        name = lf.TypeConName(self.current_module, tmpl.tycon.segments)
        self.extras.implements.extend(
            Implements(
                template=name,
                interface=self.parse_TypeConName(impl.interface),
                methods={
                    self.interned_strings[m.method_interned_name]: self.parse_Expr(m.value)
                    for m in impl.body.methods
                },
                view=self.parse_Expr(impl.body.view),
                location=self._location(impl),
            )
            for impl in pb.implements
        )
        return tmpl

    def parse_Module(self, pb):
        module = super().parse_Module(pb)
        self.current_module = lf.ModuleRef(self.current_package, module.name)
        try:
            self.extras.exceptions.extend(
                DefException(
                    name=lf.TypeConName(
                        self.current_module, self.interned_dotted_names[exc.name_interned_dname]
                    ),
                    message=self.parse_Expr(exc.message),
                    location=self._location(exc),
                )
                for exc in pb.exceptions
            )
        finally:
            self.current_module = None
        return module

    def _location(self, pb) -> lf.Location | None:
        return self.parse_Location(pb.location) if pb.HasField("location") else None

    def _copy(self) -> "Parser23":
        return copy.copy(self)
