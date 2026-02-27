import os
import uuid
import base64

from main_app.main_dto import AnaliseRequest

# --- imports do seu core ---
from core.core_molecula import Molecule
from core.core_grupo import Group
from engine.engine_symmetry_analyser import SymmetryAnalyzer
from representation.representation_type import RepresentationType
from analysis.analise_tipo import AnaliseTipo
from render.render_tipo import RenderTipo

# from pymatgen.core.structure import Molecule as PymatgenMolecule
# from pymatgen.symmetry.analyzer import PointGroupAnalyzer

import glob


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
    "benzeno": "D6h",
    "etano_eclipsado": "D3h",
    "etano_estrelado": "D3d",
    "hexafluoreto_de_enxofre": "Oh",
    "metano": "Td",
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
        "tex": tex,                 # ✅ sempre vai pro “Resultado”
    }

    # só compila pdf se marcado
    if formato == "pdf":
        pdf_bytes = PdfReportGenerator(
            metadata={
                "molecula": app.molecule.nome,
                "grupo": app.group.nome,
                "ordem": len(app.group.operacoes),
                "uuid": temp_id,
                "data": datetime.today().strftime("%Y-%m-%d %H:%M"),
                "sistema": app.group.sistema,
            },
            resultado=(SymmetryAnalyzer.de(app.group, app.molecule)
                        .usar(RepresentationType.PERMUTATION)
                        .configurar([AnaliseTipo[n.upper()] for n, ativo in data.analises.items() if ativo], temp_id)
                        .executar()
                        ._resultado)  # se você não quiser recalcular, guarde o resultado em variável
        ).gerar_pdf()

        resp["pdf_base64"] = base64.b64encode(pdf_bytes).decode("ascii")

    return _resp_json(resp)

