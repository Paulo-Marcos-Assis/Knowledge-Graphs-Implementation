# Tutorial 2 — KG with LLM (SBBD 2024)

Fonte: https://github.com/andreregino/tutorial-2-kg-with-llm
Página: https://sbbd.org.br/2024/tutoriais-2/ (autores Unicamp + Wageningen)
Notebook original: `Tutorial_2_KG_Generation_with_LLMs.ipynb` (64 células, Colab)

## Conteúdo clonado aqui

- `Tutorial_2_KG_Generation_with_LLMs.ipynb` — notebook completo (baixado do raw GitHub em 15/10/2026)
- `README.md` — original do repo (só título)

## Roteiro do notebook (resumo para apresentação)

- §2 Setup: `!pip install -q groq pandas rdflib ontospy pyvis`, auth Groq via Colab Secrets (`GROQ_TOKEN`), lista modelos `api.groq.com/openai/v1/models`
- §3 Ex.1 Produtos: dataset sintético 3 produtos → `rdflib` (FOAF/DCTERMS) cria grafo inicial → prompt (instrução + 2 few-shots) → `llama3-70b-8192` gera triplas p/ 3 frases novas (ex: "Ração Whiskas...", "retrovisores Metagal...", "Camiseta Bob Esponja...") → visualização
- §4 Ex.2 E-commerce Q&A: dataset perguntas/respostas → sumarização com LLM (compatibilidade carro × produto) → `ontology_parts = Classes [Car, Store, Product, Compatibility]` + lista de Properties ("use só as propriedades da lista") → triplas das frases sumarizadas
- §5 Desafio: adaptar prompts ao próprio domínio, testar outros LLMs, avaliar se sumarizar ajuda

## Lacunas (espaço de contribuição do nosso trabalho)

Sem avaliação, sem SHACL, sem métricas, sem DBpedia/linkage, saídas com ruído ("Here are the RDF triples...", categoria inventada "Petrônicos", IRIs cortados).

## Uso neste projeto

Baseline da Fase 2: trocar Groq por Ollama, trocar frases sintéticas por notícias reais de fraude, trocar ontologia de produtos por `../ontologia_fraude_minima.ttl` + `../prompt_extracao_kg.py`.
