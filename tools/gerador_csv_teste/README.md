# Gerador de CSV de Teste ESQUADA

Este diretório contém um gerador de CSV para testes do projeto ESQUADA.

O script produz arquivos no formato:

- `completo`: compatível com o CSV de teste usado no projeto e com o fluxo do script em R
- `modelo`: compatível com o modelo simples `ID + esq_q1_sem0 ... esq_q25_sem0`

As respostas são geradas de forma aleatória, mas respeitando a lógica dos itens:

- `esq_q2_sem0` depende de `esq_q1_sem0`
- `esq_q4_sem0` depende de `esq_q3_sem0`
- os itens são correlacionados por um perfil latente de qualidade da dieta, evitando combinações totalmente incoerentes
- opcionalmente, o script pode introduzir respostas parciais

Importante:

- os valores gerados para `esq_q*` seguem a codificação interna de escore usada no app Python e no script em R
- isto significa que os números representam categorias do modelo, e nao a ordem visual do questionário

## Uso

Gerar um CSV completo com 50 linhas:

```bash
python3 gerador_csv_teste/gerar_csv_teste.py --linhas 50
```

Gerar um CSV completo com nome personalizado:

```bash
python3 gerador_csv_teste/gerar_csv_teste.py --linhas 120 --saida gerador_csv_teste/saida/teste_120_linhas.csv
```

Gerar no formato simples:

```bash
python3 gerador_csv_teste/gerar_csv_teste.py --linhas 80 --formato modelo
```

Gerar respostas parcialmente preenchidas:

```bash
python3 gerador_csv_teste/gerar_csv_teste.py --linhas 100 --taxa-parciais 0.15
```

## Parâmetros

- `--linhas`: quantidade de linhas do CSV
- `--saida`: caminho do arquivo de saída
- `--seed`: semente aleatória para reproduzir o mesmo CSV
- `--formato`: `completo` ou `modelo`
- `--taxa-parciais`: percentual de linhas com alguns itens vazios, de `0` a `1`

## Comparar resultados

Tambem existe um comparador de resultados em:

- [comparar_scores_finais.py](/Users/caio/Desktop/esquada_full_web_fixed/gerador_csv_teste/comparar_scores_finais.py)

Ele compara dois CSVs de saída e foca apenas nos scores finais:

- `F1`
- `F1novo`
- `escore.cat`
- `escore.cat.novo`

Exemplo:

```bash
python3 gerador_csv_teste/comparar_scores_finais.py arquivo_a.csv arquivo_b.csv --rotulo-a py --rotulo-b r
```

O script gera:

- um CSV com a comparação linha a linha
- um TXT com o resumo das diferenças
- um parecer automático sobre o tamanho da diferença

No resumo, ele informa:

- quantas linhas foram comparadas
- qual chave foi usada no pareamento
- se existem chaves duplicadas
- maior diferença absoluta, média, mediana, P90, P95 e RMSE para `F1` e `F1novo`
- concordância das categorias finais
- os casos com maior divergência
