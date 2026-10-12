from pydantic import BaseModel
from typing import Optional, Dict, Literal

class RenderConfig(BaseModel):
    tipo: str         # TEXTO ou GRAFICO
    formato: str      # latex, txt, gif, 3d
    paleta: Optional[str] = None
    operacao_id: Optional[int] = None

class AnaliseRequest(BaseModel):
    render: RenderConfig
    analises: Dict[str, bool]
    idioma: Literal["pt", "en", "zh"] = "pt"