# Citizen Assist AI

Assistente de terminal que orienta **pessoas idosas** sobre saúde, INSS e benefícios, transporte, direitos e segurança, sempre com **fonte, data de verificação e aviso de que não é canal oficial**. Não pede nem registra dados pessoais.

## Integrantes
| Nome | RM |
|------|----|
| [RAFAEL SÁ] | [569223] |
| [JOÃO MELO] | [571116] |
| [GABRIEL SOUZA] | [571583] |

## Público e problema
Idosos perdem tempo para descobrir onde e como pedir o Cartão SUS, a aposentadoria, o passe livre ou como denunciar um golpe. A informação está espalhada, em linguagem técnica e misturada com sites falsos. O assistente reúne orientações verificadas em linguagem simples.

## ODS relacionados
- ODS 3 – Saúde e Bem-Estar
- ODS 10 – Redução das Desigualdades
- ODS 16 – Paz, Justiça e Instituições Eficazes (acesso à informação)

## Como executar
```
python main.py
```
Só usa a biblioteca padrão (Python 3.8+). Menu: 1 perguntar, 2 navegar por categorias, 3 indicadores, 4 exportar CSV, 0 sair (pede nota de 1 a 5).

## Estrutura
```
main.py  orientacao.py  base_conhecimento.py  assistente.py
data/base_conhecimento.json  data/historico.json  data/atendimentos.csv
```
Composição: `Assistente` → `BaseConhecimento` → lista de `Orientacao`.

## Regra de pontuação
- Palavra-chave da orientação que aparece na pergunta: **+3**
- Palavra da pergunta com 4+ letras que aparece no título: **+1** (cada palavra conta uma vez)
- **6 ou mais** = confiança ALTA · **3 a 5** = MÉDIA · **menos de 3** = "não encontrei"
- Texto normalizado (minúsculas, sem acento, sem pontuação). A palavra-chave só vale se aparecer como palavra inteira.
- `buscar()` devolve lista de tuplas `(pontos, orientacao)`; o assistente mostra a melhor e até 2 alternativas com 3+ pontos.

Exemplo: "Como faço o cartão do SUS?" → `cartao do sus` (+3), `sus` (+3), `cartao` no título (+1) = 7 → ALTA.

## Privacidade e segurança
Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não** é registrada. Entradas inválidas nunca encerram o programa. JSON ausente ou corrompido não trava o programa.

## Integrações com outras disciplinas
nenhuma

## Fontes consultadas
gov.br/saude, gov.br/inss, gov.br/mds, gov.br/mdh, gov.br/antt, consumidor.gov.br, gov.br e Lei 10.741/2003 (Estatuto da Pessoa Idosa, planalto.gov.br).

## Teste com usuários
> Preencher depois de testar com 3+ pessoas de fora da equipe (10+ atendimentos). Não registrar nomes.

| Indicador | Resultado |
|-----------|-----------|
Atendimentos registrados:    12
Resposta encontrada (%):     91.7
Taxa de acerto: ajudou (%):  91.7
Tempo médio para encontrar:  17.0 s
Tentativas por atendimento:  1.2
Facilidade de uso (1 a 5):   4.3
Dúvidas sem solução:
  - Como pedir isenção de IPVA?

## Limitações
- Só responde o que está na base (16 orientações); não interpreta frases muito diferentes das palavras-chave.
- Regras como gratuidade de transporte de 60 a 64 anos variam por município.
- As informações precisam ser reconferidas periodicamente.
- Não substitui os canais oficiais.

## Vídeo técnico
[LINK DO YOUTUBE – não listado]
