"""Esqueleto do prompt de extração de KG (etapa 2), no estilo do Tutorial 2 do SBBD 2024.

Diferenças em relação ao tutorial:
- o cliente é o Ollama (OpenAI-compatível), não o Groq;
- a ontologia é passada como listas de classes/propriedades (como `ontology_parts`);
- a saída é validada com rdflib; resposta inválida vira erro, não é aceita.

Os exemplos few-shot abaixo vêm do caso de Botuverá analisado na conversa. Para a
avaliação real, use exemplos que NÃO estejam no conjunto-ouro.
"""
import json
import re
import urllib.request
from rdflib import Graph

DEFAULT_MODEL = "qwen3.8:27b"
DEFAULT_BASE_URL = "https://ollama.ceos.ufsc.br"

ONTOLOGY_PARTS = {
    "Classes": ["Pessoa", "Empresa", "OrgaoPublico", "Localidade", "Licitacao",
                "Fraude", "Noticia"],
    "Properties": ["rdf:type", "fr:menciona", "fr:relataFraude", "fr:tipoFraude",
                   "fr:envolvePessoa", "fr:envolveEmpresa", "fr:envolveOrgao",
                   "fr:relativaALicitacao", "fr:ocorreEm", "fr:statusPessoa",
                   "fr:socioDe", "fr:nomeNormalizado", "fr:mencaoOriginal", "fr:cnpj",
                   "fr:cargo", "fr:valorReais", "fr:anoLicitacao", "fr:numeroEdital",
                   "fr:trechoOrigem"],
    "TipoFraude": ["fr:FraudeLicitacao", "fr:DirecionamentoLicitacao",
                   "fr:Superfaturamento", "fr:CartelConluio", "fr:DocumentoFalso",
                   "fr:Corrupcao", "fr:OutroTipo"],
    "StatusProcessual": ["fr:Investigado", "fr:Denunciado", "fr:Condenado",
                         "fr:Absolvido", "fr:StatusNaoInformado"],
}

PREFIXES = """@prefix fr: <http://example.org/ceos/fraude#> .
@prefix ex: <http://example.org/ceos/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

DIRECTIONS = f"""You will receive a Brazilian news article about public procurement fraud.
Your task is to create RDF triples in Turtle that describe the entities and relations in the article.
Use ONLY the classes and properties below. Never use anything outside these lists.
Classes: {", ".join(ONTOLOGY_PARTS["Classes"])}
Properties: {", ".join(ONTOLOGY_PARTS["Properties"])}
Fraud types (use exactly one per Fraude): {", ".join(ONTOLOGY_PARTS["TipoFraude"])}
Procedural status (only what the article states; else fr:StatusNaoInformado): {", ".join(ONTOLOGY_PARTS["StatusProcessual"])}
Rules:
- Create one IRI per entity as ex:<Class>_<NormalizedName> (ASCII, underscores).
- Keep the exact text of each mention in fr:mencaoOriginal.
- Put the sentence that supports each fr:Fraude in fr:trechoOrigem.
- Do not infer facts that the article does not state. Do not invent CNPJ, values or dates.
- Output only Turtle, with no explanation and no markdown fences.
I will give one example. Complete the next one.
"""

FEW_SHOT = """Article: O ex-prefeito de Botuverá, José Luiz Colombi, e mais quatro pessoas foram condenados por fraude a licitação em 2015. A Triângulo Engenharia venceu com proposta de R$ 148 mil.
Turtle:
ex:Pessoa_Jose_Luiz_Colombi a fr:Pessoa ;
    fr:mencaoOriginal "José Luiz Colombi" ; fr:nomeNormalizado "JOSE LUIZ COLOMBI" ;
    fr:cargo "ex-prefeito de Botuverá" ; fr:statusPessoa fr:Condenado .
ex:Empresa_Triangulo_Engenharia a fr:Empresa ;
    fr:mencaoOriginal "Triângulo Engenharia" ; fr:nomeNormalizado "TRIANGULO ENGENHARIA" .
ex:Localidade_Botuvera a fr:Localidade ; fr:mencaoOriginal "Botuverá" .
ex:Licitacao_Botuvera_2015 a fr:Licitacao ; fr:anoLicitacao "2015"^^xsd:gYear ;
    fr:valorReais "148000"^^xsd:decimal .
ex:Fraude_Botuvera_2015 a fr:Fraude ;
    fr:tipoFraude fr:FraudeLicitacao ;
    fr:envolvePessoa ex:Pessoa_Jose_Luiz_Colombi ;
    fr:envolveEmpresa ex:Empresa_Triangulo_Engenharia ;
    fr:relativaALicitacao ex:Licitacao_Botuvera_2015 ;
    fr:ocorreEm ex:Localidade_Botuvera ;
    fr:trechoOrigem "foram condenados por fraude a licitação em 2015" .
"""


def build_prompt(article: str) -> str:
    return DIRECTIONS + "\n" + FEW_SHOT + f"\nArticle: {article}\nTurtle:\n"


def clean_turtle(raw: str) -> str:
    """Remove cercas markdown, blocos <think> e frases introdutórias."""
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
    raw = re.sub(r"```(?:turtle|ttl)?", "", raw)
    lines = [l for l in raw.splitlines() if not l.lower().startswith("here are")]
    return "\n".join(lines).strip()


def parse_turtle(raw: str) -> Graph:
    """Levanta exceção se o Turtle for inválido (conta como falha na métrica)."""
    g = Graph()
    g.parse(data=PREFIXES + clean_turtle(raw), format="turtle")
    return g


def extract(article: str, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL):
    """Chama um modelo via API /api/chat com stdlib (sem openai) e devolve (grafo, texto bruto)."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": build_prompt(article)}],
        "stream": False,
        "options": {"temperature": 0},
    }).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/chat",
        data=body, headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    raw = data.get("message", {}).get("content", "")
    return parse_turtle(raw), raw


def extract_openai(article: str, model: str, base_url: str = "http://localhost:11434/v1"):
    """Variante original via pacote openai (Ollama local OpenAI-compatível)."""
    from openai import OpenAI  # pip install openai
    client = OpenAI(base_url=base_url, api_key="ollama")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": build_prompt(article)}],
        temperature=0,
    )
    raw = resp.choices[0].message.content
    return parse_turtle(raw), raw


if __name__ == "__main__":
    import sys
    _model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    texto = sys.argv[2] if len(sys.argv) > 2 else "Prefeito é condenado por fraude em licitação."
    base = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_BASE_URL
    grafo, bruto = extract(texto, model=_model, base_url=base)
    print(grafo.serialize(format="turtle"))
