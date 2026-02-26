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

from pymatgen.core.structure import Molecule as PymatgenMolecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer

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
            return (
                SymmetryAnalyzer
                .de(self.group, self.molecule)
                .usar(RepresentationType.PERMUTATION)
                .configurar(analises, uid)
                .executar()
                .renderizar(RenderTipo.TEX)
            )

        # Com operação selecionada: renderiza operação
        return (
            SymmetryAnalyzer
            .de(self.group, self.molecule)
            .usar(RepresentationType.PERMUTATION)
            .render(RenderTipo.from_str(config.render.formato), uid)
            .renderizar_operacao(selected_op, paleta=config.render.paleta)
        )


def identificar_grupo_pontual(xyz_path: str) -> str:
    with open(xyz_path) as f:
        lines = f.readlines()[2:]
        especies = []
        coords = []
        for line in lines:
            tokens = line.strip().split()
            especies.append(tokens[0])
            coords.append([float(x) for x in tokens[1:4]])
    mol = PymatgenMolecule(especies, coords)
    return PointGroupAnalyzer(mol).sch_symbol  # ex: "D3h"

# filename (sem .xyz) -> grupo pontual
_MOLECULA_TO_GRUPO = {
    "benzeno": "D6h",
    "etano_eclipsado": "D3h",
    "etano_estrelado": "D3d",
    "hexafluoreto_enxofre": "Oh",
    "metano": "Td",
}

def identificar_grupo_pontual_versao_alternativa(xyz_path: str) -> str:
    """
    Substitui pymatgen:
    - determina grupo pontual a partir do nome do arquivo .xyz
    Ex: static/moleculas/benzeno.xyz -> D6h
    """
    base = os.path.splitext(os.path.basename(xyz_path))[0].lower().strip()

    try:
        return _MOLECULA_TO_GRUPO[base]
    except KeyError:
        raise ValueError(
            f"Molécula '{base}' não está mapeada para grupo pontual (sem pymatgen). "
            f"Arquivos suportados: {sorted(_MOLECULA_TO_GRUPO.keys())}"
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

    # salva xyz em /tmp
    mol_path = os.path.join(workdir, molecula_filename or "molecula.xyz")
    with open(mol_path, "wb") as f:
        f.write(molecula_bytes)

    # identifica grupo e acha json
    grupo_identificado = identificar_grupo_pontual_versao_alternativa(mol_path)
    grupo_path = encontrar_json_grupo(grupo_identificado)

    # roda app
    app = MoleculeSymmetryApp.from_files(mol_path, grupo_path)
    output = app.run(selected_op=data.render.operacao_id, config=data, uid=temp_id)

    # por enquanto: TEX sempre (igual sua versão atual)
    nome_base = (molecula_filename or "molecula.xyz").rsplit(".", 1)[0]
    nome_tex = (
        "Analise_Simetria_Molecula_Personalizada.tex"
        if nome_base.lower() in ["outro", "outro.xyz", "personalizado"]
        else f"Analise_Simetria_Molecula_{nome_base}.tex"
    )

    # se output já é TEX string
    if isinstance(output, str):
        return _resp_file_text(output, nome_tex, "application/x-tex")

    # se em algum momento output virar bytes (pdf)
    if isinstance(output, (bytes, bytearray)):
        return _resp_file_bytes(bytes(output), nome_tex.replace(".tex", ".pdf"), "application/pdf")

    # fallback
    return _resp_file_text(str(output), nome_tex, "application/x-tex")