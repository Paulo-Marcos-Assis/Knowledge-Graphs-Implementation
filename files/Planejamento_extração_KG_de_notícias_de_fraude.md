# Planejamento: extração de KG de notícias de fraude

Oct 14, 2026 · @Paulo Marcos

## Contexto: a etapa 2 deve já produzir um grafo

A etapa 2 deve extrair os atributos já como triplas RDF, ancoradas numa ontologia pré-estabelecida, porque é isso que torna possível a etapa 3, a vinculação a bases públicas.

1. **Classificação** das notícias de fraude: concluída, com algoritmo treinado em milhares de notícias.
2. **Extração de informação:** pessoas, empresas e tipo de fraude, agora em forma de schema de grafo de conhecimento.
3. **Vinculação** a bases públicas, relacionando cada notícia ao que ela descreve. Fica para depois, mas define o que a etapa 2 precisa guardar.

Para a etapa 3, o grafo precisa carregar pistas de linkagem (nome normalizado e menção original, CNPJ quando aparecer, município, órgão, ano, valor, número do edital) e a proveniência (URL e trecho da notícia).

## O que o Tutorial 2 do SBBD 2024 faz

O tutorial é um único notebook do Colab, sem ferramenta própria: mostra como pedir a um LLM que gere triplas RDF a partir de texto, e não traz avaliação nem ligação a bases externas. O README do [repositório](https://github.com/andreregino/tutorial-2-kg-with-llm) tem só o título; a descrição está na [página do SBBD 2024](https://sbbd.org.br/2024/tutoriais-2/) (autores da Unicamp, com participação da Wageningen).

- **Stack:** Groq com Llama 3 70B, `rdflib`, `ontospy`, `pyvis` e `pandas`.
- **Exemplo 1:** gera o mesmo grafo de produtos de duas formas, determinística (`rdflib`, reaproveitando FOAF e DCTERMS) e com LLM a partir de frases soltas, usando instrução e dois few-shots.
- **Exemplo 2:** perguntas e respostas de e-commerce viram triplas guiadas por ontologia. Um passo de sumarização tira o ruído, e o prompt recebe a lista de classes e propriedades com a ordem "use só as propriedades da lista".
- **Desafio final:** adaptar os prompts ao próprio domínio, testar outros LLMs e avaliar se sumarizar antes ajuda.
- **Lacunas visíveis nas saídas:** categoria inventada ("Petrônicos"), IRIs com detalhes cortados e texto extra ("Here are the RDF triples...") a limpar. Não há DBpedia, validação (SHACL) nem métricas.

## Por que o tutorial foi sugerido

Provavelmente porque é uma receita mínima e executável do que o professor descreveu, e porque suas lacunas são o espaço da sua contribuição. Isto é inferência minha, a confirmar com ele.

- Mostra o padrão pedido: trecho da ontologia no prompt, few-shot e saída em RDF.
- O Desafio já propõe comparar LLMs, que é a comparação de modelos abertos que ele quer.
- A sumarização prévia combina com notícias longas e ruidosas.
- É do SBBD 2024, em Florianópolis, e serve de base para trabalhos relacionados.
- Não tem avaliação, validação nem ligação a bases: é onde entram suas métricas e a etapa 3.
- O DBpedia não vem do tutorial; foi acréscimo do professor, e aqui serve para ligar lugares, órgãos e programas a recursos públicos.

## Planejamento de ação

O trabalho se divide em seis fases, e cada uma termina em algo verificável.

| Fase | O que fazer | Entregável | Critério |
| --- | --- | --- | --- |
| 1. Ontologia e gabarito | Ontologia mínima (6 a 8 classes, 10 a 12 propriedades) e anotação manual de 100 a 200 notícias já classificadas | Ontologia em Turtle e conjunto-ouro | Duas pessoas conseguem anotar com concordância aceitável |
| 2. Baseline do tutorial | Trocar o Groq pelo Ollama e rodar em notícias reais, não em frases sintéticas | Notebook reproduzido | Gera Turtle que o `rdflib` lê |
| 3. Ablações | Com e sem sumarização; 0, 2 e 5 exemplos; Turtle direto contra JSON validado convertido por código; saída livre contra restrita à ontologia | Tabela de configurações | Cada variação muda só um fator |
| 4. Métricas | Turtle válido, conformidade com a ontologia (SHACL), precisão, revocação e F1 de entidades e de triplas, alucinação, consistência de IRI | Script de avaliação | Roda sobre o conjunto-ouro |
| 5. Modelos abertos | Mesmo protocolo para os modelos que o professor citou e os do servidor | Tabela comparativa | Mesmas notícias, mesmos prompts |
| 6. Preparar a etapa 3 | IRIs estáveis, atributos de linkagem, `owl:sameAs` para DBpedia só em lugares e órgãos | Mapa de campos para as bases | Cada atributo tem uma base-alvo |

## Estrutura da apresentação da próxima semana

A apresentação segue as quatro partes pedidas pelo professor, com a metodologia como foco.

1. **Contexto e motivação:** o pipeline em três etapas e por que um grafo na etapa 2 facilita a etapa 3.
2. **Trabalhos relacionados:** geração de KG a partir de texto com LLMs, extração guiada por ontologia, ligação de entidades; o Tutorial 2 como baseline. A bibliografia ainda precisa ser levantada.
3. **Estado da arte:** o que a literatura mede (validade, conformidade, F1 de triplas) e onde os modelos abertos falham.
4. **Metodologia:** as fases do planejamento acima, com o desenho experimental e as métricas.

Se der tempo, vale mostrar uma execução preliminar em cerca de 20 notícias com dois modelos.

## Riscos e perguntas para o professor

O maior risco é o LLM afirmar mais do que a notícia afirma, por exemplo marcar alguém como condenado quando só foi investigado; por isso a ontologia tem status processual. Pessoas privadas no grafo exigem cuidado de LGPD e de presunção de inocência se o grafo for publicado.

- [ ] A ontologia pré-estabelecida já existe ou é para eu propor a mínima?
- [ ] Quais modelos abertos exatamente (os nomes e tamanhos citados na reunião)?
- [ ] Pode usar o Groq/Llama 3 como referência do tutorial ou só os modelos locais?
- [ ] O DBpedia entra já na etapa 2 ou fica para a etapa 3?
- [ ] Quantas notícias devo anotar para o conjunto-ouro?
