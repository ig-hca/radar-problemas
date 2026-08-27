# Radar de Problemas

O Radar de Problemas é um aplicativo local que ajuda quem está em fase de descoberta a sair
da intuição e chegar a uma ordenação defensável dos problemas que encontrou em campo. Cada
candidato a problema é registrado com título, descrição, público afetado e quatro notas de
1 a 5 — frequência, intensidade, acesso ao público e disposição a pagar. O aplicativo calcula
o score como a média simples dessas quatro notas, exibe todos os problemas do maior para o
menor score com as três primeiras posições marcadas (`1º`, `2º`, `3º`) e destacadas, guarda
tudo em um arquivo JSON local para o trabalho sobreviver ao fechamento do aplicativo, e
permite baixar a lista inteira em CSV para abrir em planilha. Roda offline, sem banco de
dados, sem cadastro e sem nenhuma chamada de rede.

---

## Pré-requisitos

- **Python 3.11 ou superior** instalado e disponível no `PATH`.
- **pip** (já vem com as instalações oficiais do Python).
- Um navegador (o Streamlit abre a interface no navegador padrão).
- Nada além disso: o aplicativo não usa banco de dados, servidor nem conexão de rede.

Para conferir a versão do Python:

```powershell
python --version
```

---

## Instalação e execução no Windows

Passo a passo no **PowerShell**, a partir da pasta onde você quer guardar o projeto.

**1. Obter o projeto e entrar na pasta**

```powershell
git clone <url-do-repositorio> radar-problemas
cd radar-problemas
```

Se você recebeu o projeto como pasta pronta (sem git), basta entrar nela:

```powershell
cd C:\caminho\para\radar-problemas
```

**2. Criar o ambiente virtual**

```powershell
python -m venv .venv
```

**3. Ativar o ambiente virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

O prompt passa a começar com `(.venv)`. Se o PowerShell recusar a ativação com uma mensagem
sobre execução de scripts desabilitada, libere a política **para o usuário atual** e tente de
novo:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Alternativa sem mexer na política: usar o Prompt de Comando (`cmd`) e ativar com
`.venv\Scripts\activate.bat`.

**4. Instalar as dependências**

```powershell
pip install -r requirements.txt
```

**5. Executar o aplicativo**

```powershell
streamlit run src/app.py
```

O Streamlit abre o navegador em `http://localhost:8501`. Se não abrir sozinho, cole esse
endereço no navegador.

**6. Encerrar**

`Ctrl + C` no PowerShell para parar o servidor, e `deactivate` para sair do ambiente virtual.

> Na primeira execução ainda não existe `data/problemas.json` — a tela mostra a indicação de
> lista vazia, e o arquivo é criado no primeiro registro bem-sucedido.

---

## Como rodar os testes

Com o ambiente virtual ativado, **a partir da raiz do repositório**:

```powershell
pytest
```

Para ver o nome de cada teste:

```powershell
pytest -v
```

Para rodar só um arquivo:

```powershell
pytest tests/test_dominio.py
```

O `pyproject.toml` já declara `pythonpath = ["src"]`, então os testes importam `dominio`,
`armazenamento` e `exportacao` sem instalação nem ajuste de `PYTHONPATH`. Os testes cobrem
apenas as regras — score, validação, ordenação, leitura e gravação do arquivo e geração do
CSV — e não dependem de Streamlit, de rede nem de arquivos fora do repositório: as provas de
armazenamento usam o `tmp_path` do pytest. A camada de tela é verificada à mão pelo roteiro
de [`specs/001-priorizacao-problemas/quickstart.md`](specs/001-priorizacao-problemas/quickstart.md).

---

## Estrutura de pastas

```
radar-problemas/
├── src/                    Código do aplicativo
│   ├── app.py              Interface Streamlit — único módulo que importa streamlit
│   ├── dominio.py          Regras de negócio: score, validação e ordenação
│   ├── armazenamento.py    Leitura e gravação do JSON local
│   └── exportacao.py       Geração do CSV em memória
├── tests/                  Suíte pytest, um arquivo por módulo de regra
│   ├── test_dominio.py
│   ├── test_armazenamento.py
│   └── test_exportacao.py
├── data/                   Dados do usuário (problemas.json não é versionado)
├── specs/                  Especificação, plano, contratos e lista de tarefas
├── pyproject.toml          Configuração do projeto e do pytest
├── requirements.txt        Dependências: streamlit e pytest
└── README.md
```

A separação entre `src/app.py` e os demais módulos de `src/` é a regra central do projeto:

- **`dominio.py`, `armazenamento.py` e `exportacao.py` não importam Streamlit.** São módulos
  puros, que recebem dados simples e devolvem o resultado ao chamador — é isso que permite
  exercitá-los por pytest sem subir a aplicação.
- **`app.py` não calcula nada.** Ele coleta a entrada, chama o domínio e exibe o que ele
  devolve. Nem a fórmula do score, nem a faixa de 1 a 5 das notas, nem o limiar do top 3
  moram na tela — toda regra que vaza para a interface deixa de ser coberta por teste.

O `data/problemas.json` guarda a lista na ordem de registro e **não** guarda o score: o score
é derivado das notas e recalculado a cada leitura, para não sair de sincronia se a fórmula
mudar. O formato do arquivo está documentado em
[`specs/001-priorizacao-problemas/data-model.md`](specs/001-priorizacao-problemas/data-model.md).

---

## Exportação em CSV: por que ponto e vírgula

O arquivo exportado usa **ponto e vírgula (`;`) como separador de colunas**, e não vírgula.

O motivo é o próprio score. Na tela e no arquivo, o score aparece no formato brasileiro, com
vírgula decimal — `3,50`, `5,00`, `1,75`. Se a vírgula também fosse o separador de colunas,
cada score viraria duas colunas na planilha (`3` e `50`), e a linha inteira sairia desalinhada.
Com `;` como separador, a vírgula decimal fica sem ambiguidade nenhuma. É também o
separador que o Excel em português espera por padrão, então o arquivo abre com as colunas já
separadas, sem passar pelo assistente de importação.

Duas decisões acompanham essa:

- **Codificação UTF-8 com BOM (`utf-8-sig`)**: é o que faz o Excel em português reconhecer os
  acentos automaticamente, em vez de exibir `Ã§` no lugar de `ç`.
- **Aspas onde for preciso (`QUOTE_MINIMAL`)**: se um título ou descrição contiver `;`, aspas
  ou quebra de linha, o campo sai entre aspas e o texto chega à planilha em uma única célula,
  exatamente como foi digitado. Nada é recusado nem substituído.

O arquivo é gerado inteiro em memória e entregue pelo botão de download — cai na pasta de
downloads do navegador, sem arquivo intermediário dentro do projeto.

---

## Ambiente de desenvolvimento

O projeto foi desenvolvido e testado com:

| Componente | Versão |
|---|---|
| Python | 3.14.4 |
| Streamlit | 1.62.0 |
| pytest | 9.1.1 |
| Sistema operacional | Windows 11 |

O `requirements.txt` não fixa versões: declara apenas `streamlit` e `pytest`, e o
`pyproject.toml` exige `requires-python = ">=3.11"`. As versões acima são as usadas no
desenvolvimento, registradas aqui para reprodução em caso de diferença de comportamento.

---
## Uso de IA

**Agente utilizado:** Claude Code (Opus 5), em todas as fases do ciclo SDD —
constitution, specify, clarify, plan, tasks e implement. O ChatGPT/Claude via chat
foi usado para revisar criticamente os artefatos entre uma fase e outra, sem gerar
nenhum deles.

**O que foi corrigido na revisão humana:**

- A constituição gerada descrevia o projeto como individual, contrariando o enunciado.
  Corrigida em todas as oito ocorrências antes do commit.
- A constituição inicial fixava Python 3.14.7 exato; foi redefinida para 3.11+,
  gerando a emenda de versão 2.0.0.
- O agente propôs mensagem de commit fora do padrão exigido pelo enunciado
  (`docs: amend constitution to v2.0.0 (...)`); mantivemos `docs: constitution`.
- O `plan.md` nasceu com o cabeçalho apontando para uma branch inexistente; corrigido
  para `develop`, alinhando spec e plano com o repositório real.
- O commit `docs: plan` não existia — os artefatos do plano tinham ido junto no commit
  de tasks. O histórico foi reescrito para separar as duas fases.
- Na spec, o FR de exportação especificava "valores separados por vírgula", que é
  decisão de formato e pertence ao plano; foi reescrito em termos de comportamento
  observável.
- Os exemplos numéricos da spec misturavam ponto e vírgula como separador decimal;
  padronizados em vírgula, o que revelou a colisão com o delimitador do arquivo
  exportado e levou à escolha do ponto-e-vírgula.
