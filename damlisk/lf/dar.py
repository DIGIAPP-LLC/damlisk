import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from dazl._gen.com.digitalasset.daml.lf.archive import daml_lf1_pb2, daml_lf2_pb2, daml_lf_pb2
from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.parse import parse_archive_payload
from google.protobuf.message import DecodeError

from damlisk.exceptions import DarError
from damlisk.lf.lf2 import Extras, Parser1, Parser23

MANIFEST = "META-INF/MANIFEST.MF"
FORMATS = (
    ("daml_lf_2", daml_lf2_pb2.Package, Parser23, 2),
    ("daml_lf_1", daml_lf1_pb2.Package, Parser1, 1),
)


@dataclass(frozen=True)
class Manifest:
    main_dalf: str
    sdk: str | None

    @classmethod
    def parse(cls, raw: str) -> "Manifest":
        pairs = (line.partition(":") for line in re.sub(r"\r?\n ", "", raw).splitlines())
        fields = {key.strip(): value.strip() for key, sep, value in pairs if sep}
        return cls(fields.get("Main-Dalf", ""), fields.get("Sdk-Version"))

    @property
    def root(self) -> str:
        return self.main_dalf.split("/", 1)[0]

    @property
    def main_id(self) -> str:
        return Path(self.main_dalf).stem.rsplit("-", 1)[-1]


@dataclass(frozen=True)
class LfPackage:
    pkg_id: str
    name: str
    version: str
    lf_ver: str
    package: lf.Package
    extras: Extras

    @property
    def modules(self) -> tuple[lf.Module, ...]:
        return tuple(self.package.modules)

    @classmethod
    def parse(cls, data: bytes, fname: str) -> "LfPackage":
        archive = daml_lf_pb2.Archive()
        archive.ParseFromString(data)
        ref = lf.PackageRef(archive.hash)
        payload = parse_archive_payload(ref, archive.payload)
        for field, message, parser_cls, major in FORMATS:
            if payload.HasField(field):
                pkg_pb = message()
                pkg_pb.ParseFromString(getattr(payload, field))
                parser = parser_cls(ref)
                package = parser.parse_Package(pkg_pb)
                meta = package.metadata
                name = meta.name if meta else Path(fname).stem.rsplit("-", 1)[0]
                lf_ver = f"{major}.{payload.minor}"
                version = meta.version if meta else ""
                return cls(archive.hash, name, version, lf_ver, package, parser.extras)
        raise DarError(f"{fname} contains neither Daml-LF 1 nor Daml-LF 2")


@dataclass(frozen=True)
class Dar:
    path: Path
    sdk: str | None
    main: LfPackage
    packages: tuple[LfPackage, ...]
    sources: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> "Dar":
        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
                if MANIFEST not in names:
                    raise DarError(f"{path} has no {MANIFEST}")
                manifest = Manifest.parse(zf.read(MANIFEST).decode())
                if not manifest.main_dalf:
                    raise DarError(f"{path} has no Main-Dalf entry in its manifest")
                packages = tuple(
                    LfPackage.parse(zf.read(n), n) for n in names if n.endswith(".dalf")
                )
                prefix = f"{manifest.root}/"
                sources = {
                    n[len(prefix) : -len(".daml")].replace("/", "."): zf.read(n).decode()
                    for n in names
                    if n.startswith(prefix) and n.endswith(".daml")
                }
        except (zipfile.BadZipFile, DecodeError) as e:
            raise DarError(f"{path} is not a valid DAR: {e}") from e
        main = next((p for p in packages if p.pkg_id == manifest.main_id), None)
        if main is None:
            raise DarError(f"{path} does not contain its main package {manifest.main_id}")
        return cls(path, manifest.sdk, main, packages, sources)
