# Relatório de atualização — Meu Inglês 1.4 (Etapa 5)

## Novidades
- O aplicativo registra tentativas e erros por cartão, preservando compatibilidade com cartões antigos.
- O relatório de progresso destaca até cinco palavras que merecem reforço, com base nos erros e nas revisões difíceis registradas.
- Foi adicionado um modo de revisão direcionada, que prioriza os cartões com maior histórico de dificuldade.
- A revisão diária agora prioriza cartões com mais lapsos e menor facilidade estimada, sem remover a revisão espaçada existente.

## Privacidade e dados
Todo o histórico permanece no armazenamento local do navegador, como já acontecia com o progresso do aplicativo. Os campos novos são opcionais e são inicializados automaticamente ao abrir dados antigos.

## Verificações
- Sintaxe JavaScript: aprovada com Node.js.
- Regressão: inicialização, preservação de backup vazio, proteção contra JSON corrompido, XP diário, sincronização entre abas, progresso semanal, listening e conquistas.
- Etapa 5: ranking de palavras difíceis, sessão de revisão direcionada, relatório e migração de cartões antigos.
- Limite: ainda não foi possível executar teste visual em navegador real nem publicar no Netlify.


## Etapa 6 — Conversação prática (versão 1.5)
- Adicionado modo de conversação guiada com cinco situações: cafeteria, apresentações, aeroporto, compras e pedidos de informação.
- Cada diálogo apresenta a fala da outra pessoa, tradução/contexto e uma resposta sugerida.
- Respostas podem ser digitadas ou ditas pelo microfone quando o navegador oferece reconhecimento de fala.
- Feedback compara a resposta com o modelo, mostra a transcrição e uma porcentagem aproximada; não afirma avaliar fonética.
- Histórico por diálogo, avanço entre falas, conclusão e opção de repetir ou escolher outra situação.
- Mantido o treino individual de pronúncia já existente.
- Validação: `node --check`, testes de regressão das etapas anteriores, testes de catálogo/conversação/progressão e integridade do ZIP.


## Etapa 7 — Conversação adaptativa e evolução (versão 1.6)
- O aplicativo registra sessões iniciadas, respostas tentadas, acertos aproximados, média de correspondência, melhor resultado e conversas concluídas por situação.
- A tela de conversação exibe o histórico de cada cenário e sugere a situação com menor média registrada para reforço.
- O relatório de progresso ganhou um painel dedicado à evolução nas conversas, sem confundir correspondência textual com fluência ou pronúncia.
- O histórico novo é salvo localmente e inicializado vazio em backups antigos, mantendo compatibilidade com os dados existentes.
- Validação: `node --check`, testes de regressão das etapas anteriores e testes de sessões, tentativas, conclusão, recomendação adaptativa, relatório e migração.
- Limite: ainda não foi possível executar teste visual em navegador real nem publicar no Netlify.

## Etapa 8 — identidade visual e microinterações (versão 1.7)
- Refinado o acabamento visual do tema Jardim de Vrindavan sem alterar o fluxo de estudo nem os dados do usuário.
- Melhorados estados de foco, hover e pressionamento em botões, navegação, cartões, opções, campos e itens de revisão.
- Acrescentadas transições curtas para progresso, feedback e desbloqueio de conquistas.
- Melhorado o tratamento visual de diálogos, notificações e modal.
- Ajustes específicos para toque/mobile e tema escuro.
- Respeitada a preferência `prefers-reduced-motion`, desativando animações e transições não essenciais.
- Alterações concentradas na folha `assets/vrindavan.css`; nenhuma migração de dados ou alteração de lógica de aprendizagem foi necessária.

## Etapa 9 — celebração, repertório visual e variedade dos exercícios (versão 1.8)

- Incluída a imagem enviada pela usuária na tela de **Rodada concluída**, com tratamento visual em moldura ornamental e texto alternativo acessível.
- Ampliado o repertório de ornamentos SVG com símbolos inspirados em tradições dhármicas e na arte egípcia (ankh, olho de Hórus, escaravelho e disco solar), além dos elementos florais e musicais existentes.
- Os ornamentos das questões agora variam aleatoriamente entre oito motivos.
- A fila da missão diária é embaralhada para evitar sequência previsível de revisões e palavras novas.
- Removido o ciclo que apresentava uma palavra nova e imediatamente repetia a mesma palavra em uma questão de significado.
- Os exercícios agora alternam aleatoriamente entre escolha inglês→português, escolha português→inglês, escrita em inglês, listening e tradução reversa. A sessão evita repetir o mesmo tipo de exercício em sequência.
- A correção reconhece a direção da questão e mostra inglês, português e exemplo no feedback.
- Respeitada a preferência do sistema por movimento reduzido nas novas animações.

Validação: `node --check` aprovado; conferência estática dos cinco formatos de exercício, símbolos e caminho da imagem concluída; integridade do ZIP validada. A tentativa de abrir Chromium headless neste ambiente excedeu o tempo disponível, portanto a inspeção visual real não foi concluída.

## Etapa 10 — iconografia variada e referências de acervo (versão 1.9)
- Reduzida a repetição visual de flores de lótus e penas de pavão na navegação, cabeçalhos e rodapé.
- Substituídos elementos repetidos por símbolos figurativos egípcios (ankh, Olho de Hórus, escaravelho, disco solar) e elementos associados à tradição hindu (flauta, diya), em usos alternados por seção.
- Adicionada uma faixa iconográfica com fotografias de peças históricas: grupo de divindades hindus (Ganesha, Shiva e Karttikeya), escultura de Anúbis e Shiva Nataraja. As imagens são carregadas dos acervos públicos dos museus/Wikimedia, com crédito no próprio aplicativo.
- Fontes e direitos consultados:
  - LACMA / Wikimedia Commons, “13th century Hindu Gods Ganesha, Shiva, and Karttikeya on Their Mounts” — domínio público: https://commons.wikimedia.org/wiki/File:13th_century_Hindu_Gods_Ganesha,_Shiva,_and_Karttikeya_on_Their_Mounts.jpg
  - The Metropolitan Museum of Art / Wikimedia Commons, “Statuette of Anubis” — CC0: https://commons.wikimedia.org/wiki/File:Statuette_of_Anubis_MET_38.5_EGDP022866.jpg
  - The Metropolitan Museum of Art, “Shiva as Lord of Dance (Nataraja)” — Open Access / domínio público: https://www.metmuseum.org/art/collection/search/39328
- Observação: as fotografias são carregadas por URL dos acervos; portanto, a exibição delas depende de conexão com a internet. Os arquivos locais e os símbolos vetoriais continuam disponíveis offline.

## Etapa 11 — trilha progressiva para iniciantes (versão 2.0)
- Criada uma trilha de cinco etapas baseada na quantidade de cartões já apresentados: Primeiros passos (0–9), Palavras do dia a dia (10–24), Frases ganhando forma (25–49), Escuta com confiança (50–99) e Independência (100+).
- No início, as missões usam somente reconhecimento com alternativas e no máximo três opções, evitando exigir escrita livre ou listening antes da hora.
- A partir da segunda etapa entram questões inglês↔português; na terceira é liberada escrita ativa; na quarta entram listening e tradução reversa; na quinta a prática combina todos os formatos.
- Escrita ativa e listening exibem a etapa em que serão desbloqueados e impedem iniciar antes do momento adequado.
- A tela inicial agora mostra etapa atual, descrição do objetivo, progresso e as próximas etapas.
- Respostas erradas de quem está nas primeiras etapas recebem uma dica curta e acolhedora.
- A progressão utiliza os cartões já apresentados no próprio aplicativo; não apaga XP, cartões, histórico nem configurações existentes.

Validação técnica: sintaxe dos scripts inline validada com Node.js; estrutura ZIP e arquivos do projeto preservados. A execução interativa em navegador real não está disponível neste ambiente.


### Ajuste visual 2.1 — símbolos e imagens
- Removidas as imagens avulsas de divindades das janelas e da lateral.
- Substituída a decoração ocular pelo Olho de Hórus vetorial nas áreas correspondentes.
- Marca Meu Inglês identificada com o Ankh.
- Mantidos ornamentos simbólicos vetoriais, sem mosaicos de imagens externas.


## Versão 2.2 — unidades temáticas guiadas
- Adicionada área Aulas com quatro unidades iniciais em sequência: cumprimentos, apresentação pessoal, rotina e lugares/pedidos.
- Cada unidade apresenta vocabulário, tradução, frase contextual e áudio; depois traz exercícios de reconhecimento e revisão final.
- Progresso das unidades fica salvo no estado local, unidades seguintes são liberadas após concluir a anterior e cada conclusão concede 20 XP.
- As palavras das aulas são adicionadas ao vocabulário do usuário quando a unidade é iniciada, sem duplicar termos existentes.

## Versão 2.3 — trilha ampliada e identidade visual por seção
- A navegação recebeu símbolos vetoriais exclusivos por área: disco solar para Início, pergaminho para Aulas, flauta para Estudar, papiro para Cartões, bússola para Progresso, ondas sonoras para Pronúncia e engrenagem para Configurações.
- A trilha passou a incluir unidades temáticas adicionais geradas a partir do vocabulário que já acompanha o aplicativo, preservando as quatro unidades guiadas originais e reaproveitando os cartões existentes sem duplicá-los no catálogo.
- Cada unidade ampliada segue quatro microetapas de vocabulário, com uma explicação gramatical curta, um exemplo e uma atividade de construção de frase antes da revisão final.
- Foram incluídas explicações simples sobre pronomes, verbo to be, presente, perguntas e negativas, artigos, plural, adjetivos, preposições, passado, futuro, comparativos, conectivos e outros fundamentos.
- O desbloqueio continua sequencial; progresso e conclusões permanecem no armazenamento local. A revisão final só pode avançar depois de revelar a resposta.
- O total de microetapas é calculado pelo próprio catálogo, para refletir a quantidade efetiva de unidades presentes no pacote.

Validação técnica: sintaxe JavaScript verificada com Node.js e integridade do ZIP verificada após empacotamento. Não foi possível concluir teste visual interativo em navegador real neste ambiente; a publicação no Netlify continua sendo uma ação externa.


## Versão 2.3.1 — remoção de símbolos solicitada
- Removidas todas as referências visuais ao Olho de Hórus e ao Ankh das telas, menus, marca, rodadas, cabeçalhos, rodapé e decoração lateral.
- Excluídos os dois símbolos do arquivo SVG compartilhado para impedir reutilização acidental.
- Substituídos por motivos já existentes no aplicativo (disco solar, lótus, diya, flauta, bússola e escaravelho), preservando a identidade visual geral.


## Atualização — aprofundamento da gramática (05/11/2026)

- As 30 notas gramaticais existentes agora contam com explicação ampliada em português.
- Cada tópico apresenta estrutura/formação, três exemplos bilíngues, dica de uso e erro comum.
- Os exemplos em inglês possuem botão para ouvir o áudio.
- Foi acrescentado um exercício específico de gramática por tópico, com correção e explicação da resposta.
- A sequência original de vocabulário, construção de frase, revisão, progresso e XP foi preservada.
- Nenhum arquivo de áudio ou dado de progresso foi removido ou renomeado.

Validação: sintaxe JavaScript conferida com Node.js 22 (`node --check`). Integridade do ZIP e referências do manifesto conferidas após a edição.
