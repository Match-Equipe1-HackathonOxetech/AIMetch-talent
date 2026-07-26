"""
GeminiAdapter — a única classe do projeto que sabe que existe uma "API do
Gemini". Implementa LLMPort; o domínio (EntrevistaService) não importa nada
deste módulo, só a interface em app/ports/llm_port.py.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from google import genai

from app.domain.entities import PerguntaTemplate, Vaga
from app.domain.value_objects import Memoria, ResultadoIA, ResumoIA
from app.ports.llm_port import LLMPort

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "prompt-entrevista-softskills.md")


class GeminiAdapter(LLMPort):
    def __init__(self, api_key: str, modelo: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.modelo = modelo
        with open(_PROMPT_PATH, encoding="utf-8") as f:
            self._prompt_template = f.read()

    def gerar_pergunta(
        self,
        vaga: Vaga,
        memoria: Memoria,
        pergunta_template: Optional[PerguntaTemplate],
        resposta: Optional[str],
    ) -> ResultadoIA:
        prompt = self._montar_prompt(vaga, memoria, pergunta_template, resposta)
        data = self._chamar_gemini(prompt)

        return ResultadoIA(
            proxima_pergunta=data.get("proxima_pergunta"),
            memoria_atualizada=Memoria.from_dict(data["memoria_atualizada"]),
            concluida=bool(data.get("entrevista_concluida", False)),
        )

    def gerar_resumo_resultado(self, vaga: Vaga, memoria: Memoria) -> ResumoIA:
        prompt = (
            "Você acabou de concluir uma entrevista de softskills para a vaga "
            f"'{vaga.titulo}'. Estado final da memória (softskills avaliadas, "
            f"pontuações e contexto pessoal coletado): {json.dumps(memoria.to_dict(), ensure_ascii=False)}\n\n"
            "Gere um resumo objetivo do desempenho do candidato e uma recomendação "
            "de contratação para o recrutador. Responda apenas com um JSON no formato: "
            '{"resumo": "...", "recomendacao": "..."}'
        )
        data = self._chamar_gemini(prompt)
        return ResumoIA(resumo=data["resumo"], recomendacao=data["recomendacao"])

    def _chamar_gemini(self, prompt: str) -> dict:
        response = self.client.models.generate_content(
            model=self.modelo,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)

    def _montar_prompt(
        self,
        vaga: Vaga,
        memoria: Memoria,
        pergunta_template: Optional[PerguntaTemplate],
        resposta: Optional[str],
    ) -> str:
        memoria_dict = memoria.to_dict()
        return (
            self._prompt_template
            .replace("{titulo_vaga}", vaga.titulo)
            .replace("{softskills_alvo}", ", ".join(vaga.softskills_alvo))
            .replace("{softskill_atual}", memoria.softskill_atual() or "(nenhuma — todas avaliadas)")
            .replace("{softskills_estado_json}", json.dumps(memoria_dict["softskills"], ensure_ascii=False))
            .replace("{contexto_pessoal_json}", json.dumps(memoria_dict["contexto_pessoal"], ensure_ascii=False))
            .replace("{ganchos_usados_json}", json.dumps(memoria_dict["ganchos_usados"], ensure_ascii=False))
            .replace("{pergunta_template_texto}", pergunta_template.texto if pergunta_template else "(livre)")
            .replace("{resposta_candidato}", resposta or "")
        )
