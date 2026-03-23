import os
import uuid
import base64

from main_app.main_dto import AnaliseRequest

# --- imports do seu core ---
from core.core_molecula import Molecule
from core.core_grupo import Group
from core.symmetry_detector import SymmetryDetector
from engine.engine_symmetry_analyser import SymmetryAnalyzer
from representation.representation_type import RepresentationType
from analysis.analise_tipo import AnaliseTipo
from render.render_tipo import RenderTipo
from render.render_pdf import PdfReportGenerator
from datetime import datetime

# from pymatgen.core.structure import Molecule as PymatgenMolecule
# from pymatgen.symmetry.analyzer import PointGroupAnalyzer

import glob

def identificar_grupo_pontual_por_geometria(mol_path: str) -> dict:
    molecule = Molecule.from_file(mol_path)
    detector = SymmetryDetector(molecule, tolerancia=0.02)
    return detector.infer_group()

def _resp_file_text(text: str, filename: str, content_type: str):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        "body": text,
    }


def _resp_file_bytes(blob: bytes, filename: str, content_type: str):
    return {
        "statusCode": 200,
        "isBase64Encoded": True,
        "headers": {
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        "body": base64.b64encode(blob).decode("ascii"),
    }


class MoleculeSymmetryApp:
    def __init__(self, molecule, group):
        self.molecule = molecule
        self.group = group

    @classmethod
    def from_files(cls, mol_file, group_file):
        group = Group.from_file(group_file)
        molecule = Molecule.from_file(mol_file)
        return cls(molecule=molecule, group=group)

    def run(self, selected_op, config: AnaliseRequest, uid: str):
        # Sem operação selecionada: roda análises e render TEX
        if selected_op is None:
            analises = [
                AnaliseTipo[nome.upper()]
                for nome, ativo in config.analises.items()
                if ativo
            ]

            # >>> DEBUG (depois a gente troca por logger)
            print("=== DEBUG RUN ===")
            print("render.tipo   =", getattr(config.render, "tipo", None))
            print("render.formato=", getattr(config.render, "formato", None))
            print("render.paleta =", getattr(config.render, "paleta", None))
            print("analises      =", config.analises)
            print("=================")

            # usa o formato do payload (pdf/tex)
            formato = RenderTipo.from_str(config.render.formato)  # "pdf" / "tex"
            
            return (
                SymmetryAnalyzer
                .de(self.group, self.molecule)
                .usar(RepresentationType.PERMUTATION)
                .configurar(analises, uid)
                .executar()
                .renderizar(formato)
            )

        # Com operação selecionada: renderiza operação
        return (
            SymmetryAnalyzer
            .de(self.group, self.molecule)
            .usar(RepresentationType.PERMUTATION)
            .render(RenderTipo.from_str(config.render.formato), uid)
            .renderizar_operacao(selected_op, paleta=config.render.paleta)
        )


# def identificar_grupo_pontual(xyz_path: str) -> str:
#     with open(xyz_path) as f:
#         lines = f.readlines()[2:]
#         especies = []
#         coords = []
#         for line in lines:
#             tokens = line.strip().split()
#             especies.append(tokens[0])
#             coords.append([float(x) for x in tokens[1:4]])
#     mol = PymatgenMolecule(especies, coords)
#     return PointGroupAnalyzer(mol).sch_symbol  # ex: "D3h"

# filename (sem .xyz) -> grupo pontual
import os
import unicodedata

# normaliza "Hexafluoreto de Enxofre" -> "hexafluoreto_de_enxofre"
def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("ç", "c")  # opcional (normalização já cobre quase tudo)
    s = "".join(ch if ch.isalnum() else "_" for ch in s)
    s = "_".join([p for p in s.split("_") if p])  # remove __
    return s

# "slug" do nome (2a linha do xyz) -> grupo pontual
_NOME_TO_GRUPO = {
    _slug("H2O"): "C2v",
    _slug("NH3"): "C3v",
    _slug("BF3"): "D3h",
    _slug("Benzeno"): "D6h",
    _slug("CO2"): "Dinfh",
    _slug("Etano eclipsado"): "D3h",
    _slug("ethane_eclipsed"): "D3h",
    _slug("Etano estrelado"): "D3d",
    _slug("Hexafluoreto de Enxofre"): "Oh",
    _slug("SF6"): "Oh",
    _slug("Metano"): "Td",

    _slug("C60F36"): "S6",
    _slug("Co4(Cp)4"): "S4",
    _slug("Complexo de Fe(III)"): "S6",
    _slug("Infinitene - C48H24"): "D2",
    _slug("1,3,5,7-tetramethyl-cyclooctatetraeno"): "S4",
}

def identificar_grupo_pontual_versao_alternativa(xyz_path: str) -> str:
    # 1) tenta ler o "comentário" (linha 2 do .xyz)
    nome_linha2 = ""
    try:
        with open(xyz_path, "r", encoding="utf-8", errors="replace") as f:
            _ = f.readline()            # linha 1: número de átomos
            nome_linha2 = f.readline()  # linha 2: comentário/nome
    except Exception as e:
        print("[WARN] Falha lendo XYZ:", xyz_path, "err:", repr(e))

    key = _slug(nome_linha2)

    # fallback: se a linha2 vier vazia, tenta pelo filename (benzeno.xyz etc)
    if not key:
        base = os.path.splitext(os.path.basename(xyz_path))[0].lower().strip()
        key = _slug(base)

    print("=== DEBUG GRUPO ===")
    print("xyz_path:", xyz_path)
    print("linha2_raw:", (nome_linha2 or "").strip())
    print("key:", key)
    print("===================")

    try:
        return _NOME_TO_GRUPO[key]
    except KeyError:
        raise ValueError(
            f"Molécula '{key}' não está mapeada para grupo pontual (sem pymatgen). "
            f"Suportadas: {sorted(_NOME_TO_GRUPO.keys())}"
        )

def encontrar_json_grupo(grupo: str) -> str:
    grupo_proc = grupo.strip().lower()
    arquivos = glob.glob("static/grupos/**/*.json", recursive=True)

    for path in arquivos:
        nome_arquivo = os.path.splitext(os.path.basename(path))[0].lower()
        if nome_arquivo == grupo_proc or nome_arquivo.startswith(grupo_proc):
            return path

    raise FileNotFoundError(f"Arquivo JSON para o grupo '{grupo}' não encontrado.")


def processar_analise_bytes(molecula_bytes: bytes, molecula_filename: str, data: AnaliseRequest):
    temp_id = f"SIM{uuid.uuid4().hex[:6].upper()}"
    workdir = f"/tmp/analise_{temp_id}"
    os.makedirs(workdir, exist_ok=True)

    mol_path = os.path.join(workdir, molecula_filename or "molecula.xyz")
    with open(mol_path, "wb") as f:
        f.write(molecula_bytes)

    usar_detector = False
    grupo_dinamico = None

    if usar_detector:
        try:
            grupo_dinamico = identificar_grupo_pontual_por_geometria(mol_path)
            print("[DEBUG DETECTOR] grupo inferido:", grupo_dinamico["nome"])
        except Exception as e:
            print("[WARN] detector geométrico falhou, usando fallback:", repr(e))

    if grupo_dinamico is not None:
        molecule = Molecule.from_file(mol_path)
        group = Group(
            sistema="Molecular",
            nome=grupo_dinamico["nome"],
            ordem=grupo_dinamico.get("ordem", len(grupo_dinamico.get("operacoes", []))),
            operacoes=grupo_dinamico.get("operacoes", []),
            tolerancia=grupo_dinamico.get("tolerancia", 0.02),
        )
        app = MoleculeSymmetryApp(molecule=molecule, group=group)
    else:
        grupo_identificado = identificar_grupo_pontual_versao_alternativa(mol_path)
        grupo_path = encontrar_json_grupo(grupo_identificado)
        app = MoleculeSymmetryApp.from_files(mol_path, grupo_path)

    # 🔑 decide formato
    # (garante que 'pdf' e 'tex' sejam entendidos)
    formato = (data.render.formato or "").strip().lower()

    # roda análises e gera TEX SEMPRE
    # (ajuste aqui se sua app.run hoje retorna direto string/pdf dependendo do formato)
    tex = (
        SymmetryAnalyzer
        .de(app.group, app.molecule)
        .usar(RepresentationType.PERMUTATION)
        .configurar(
            [AnaliseTipo[n.upper()] for n, ativo in data.analises.items() if ativo],
            temp_id
        )
        .executar()
        .renderizar(RenderTipo.TEX)
    )

    resp = {
        "ok": True,
        "uuid": temp_id,
        "molecula": getattr(app.molecule, "nome", None),
        "grupo": getattr(app.group, "nome", None),
        "tex": tex,                 # sempre vai pro “Resultado”
    }

    return resp
