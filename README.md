# 🏃‍♂️ Criador de Planos de Treino de Corrida

Um software completo em Python para criar planos de treino de corrida personalizados. Seja você treinar para 5K, 10K, Meia Maratona ou Maratona, esta ferramenta gera cronogramas estruturados adaptados ao seu nível de experiência e objetivos.

## ℹ️ O que é o Criador de Planos de Corrida

O Criador de Planos de Corrida é um **gerador automático de periodizações**. Ele coleta dados do atleta (tempo disponível, experiência, tempos de prova e histórico de lesões), calcula zonas de treino com métodos consagrados e produz um plano semanal completo com volume, distribuição de intensidades e treinos detalhados. Tudo é feito em Python, sem dependências externas, podendo ser usado via notebook, linha de comando ou integração com Intervals.icu.

### Principais Conceitos

- **Perfil do corredor**: definido por dias disponíveis, volume semanal máximo, preferências de dias de treino, histórico de lesões e objetivo de distância.
- **Geração do plano**: o `PlanGenerator` estrutura semanas com fases de base, construção, pico e taper, distribuindo treinos de intensidade e rodagens leves conforme o nível do atleta.
- **Zonas de treino**: calculadas via `training_zones.py` com métodos Jack Daniels (VDOT) ou Velocidade Crítica, produzindo paces alvo para as zonas Easy, Marathon, Threshold, Interval e Repetition.
- **Persistência**: os planos são serializados/deserializados por `running_plan.py`, permitindo salvar em JSON, reabrir e enviar para outras integrações.
- **Visualização**: `plot_utils.py` oferece gráficos de volume semanal e distribuição de zonas para validar a progressão e a carga.

## ✨ Funcionalidades

- **🎯 Múltiplas Distâncias**: Suporte para treinos de 5K, 10K, Meia Maratona e Maratona
- **📊 Três Níveis de Experiência**: Planos para Iniciante, Intermediário e Avançado
- **📅 Cronograma Flexível**: 3 a 6 dias de treino por semana
- **📈 Treino Progressivo**: Fases inteligentes de construção, pico e redução (taper)
- **🏋️ Variedade de Treinos**: Corridas fáceis, tempo run, intervalados, fartlek e longões
- **💾 Persistência de Planos**: Salve e carregue planos de treino como arquivos JSON
- **🖥️ Interface CLI Interativa**: Interface de linha de comando amigável
- **📆 Planejamento de Datas**: Defina datas de início e calcule datas de prova

### 🆕 Funcionalidades Avançadas (NOVO!)

- **🎨 Arredondamento Inteligente**:
  - Distâncias em múltiplos de 5km (5, 10, 15, 20, 25...)
  - Tempos em múltiplos de 30min (30min, 1h, 1h30, 2h...)

- **📊 Tabela Visual de Zonas**:
  - Visualização linda com emojis e bordas
  - Mostra pace, % FC e dicas de uso

- **📉 Rastreamento de Distribuição**:
  - Km por zona de intensidade
  - Análise de carga de treino

- **📈 Gráficos de Visualização**:
  - Volume semanal com gradiente de cores (azul→vermelho)
  - Distribuição de zonas em gráfico empilhado

- **🔄 Integração com Intervals.icu** (NOVO!):
  - Upload automático do plano para sua conta Intervals.icu
  - Sincronização de treinos estruturados com zonas
  - Acompanhamento fácil pelo app ou web
  - Configuração simples com API Key

- **🔬 Calculadora de Zonas de Treino**: Zonas de pace personalizadas baseadas em tempos recentes de prova
  - Método Jack Daniels VDOT (baseado em VO2max)
  - Método de Velocidade Crítica

- **📋 Estrutura Detalhada de Treino**: Cada sessão inclui:
  - Pace alvo específico para o treino
  - Tempo total estimado
  - Segmento de aquecimento com pace e duração
  - Intervalos de trabalho principais com repetições
  - Períodos de recuperação entre intervalos
  - Segmento de desaquecimento

- **🎯 5 Zonas de Treino**: Easy, Marathon, Threshold, Interval, Repetition
  - 🟢 Easy/Recovery (Verde)
  - 🔵 Marathon Pace (Azul)
  - 🟡 Threshold/Tempo (Amarelo)
  - 🟠 Interval/5K (Laranja)
  - 🔴 Repetition/Fast (Vermelho)

- **⚡ Paces Personalizados**: Baseados nos seus tempos de 5K, 10K, Meia Maratona ou Maratona
- **🔄 Compatível com Versões Anteriores**: Funciona com ou sem zonas de treino

## 🧭 Visão Geral de Arquitetura

- `user_profile.py`: coleta e valida as preferências do atleta (dias livres, horários, limitações e histórico de lesões).
- `plan_generator.py`: gera a periodização semanal, decide tipos de sessão (fácil, tempo, intervalado, longão) e distribui volume total.
- `running_plan.py`: representa o plano final com semanas, treinos, datas e oferece métodos para salvar/carregar em JSON.
- `training_zones.py`: calcula paces alvo a partir de tempos recentes de prova, suportando múltiplos métodos.
- `plot_utils.py`: cria gráficos para revisar volume e distribuição de zonas.
- `intervals_integration.py`: conecta o plano ao Intervals.icu (upload e teste de credenciais).
- Notebooks (`create_plan_interactive.ipynb`, `formulario_corredor*.ipynb`): fluxos guiados para usuários não técnicos.

### Fluxo de geração

1. **Coleta de dados** (CLI ou notebook) → `UserProfile`.
2. **Cálculo de zonas (opcional)** → `TrainingZones`.
3. **Criação do plano** → `PlanGenerator.generate_plan(...)` retorna um `RunningPlan`.
4. **Ajustes de datas e volumes** → métodos `set_start_date`, `adjust_volumes`, etc.
5. **Persistência** → `save_to_file`/`load_from_file`.
6. **Visualização e upload** → `plot_utils` e `IntervalsUploader`.

## 🛠️ Configuração e Dados

- **Entrada mínima**: objetivo de prova (5K/10K/21K/42K), nível (iniciante/intermediário/avançado), semanas e dias/semana.
- **Entrada recomendada**: tempos recentes de prova para gerar zonas; disponibilidade diária; restrições de volume semanal; data de início.
- **Saída**: JSON com semanas e treinos, incluindo pace/duração-alvo e estruturas (aquecimento, principal, desaquecimento).
- **Configuração de credenciais**: crie `intervals_config.json` (ou use `create_config_file`) para Intervals.icu; o arquivo já está no `.gitignore`.
- **Local dos planos**: arquivos `.json` gerados via CLI/Notebooks/`RunningPlan.save_to_file`.

## 📈 Recursos Avançados

- **Personalização de zonas**: escolha o método (`jack_daniels` ou `critical_velocity`), adicione múltiplos tempos de prova e visualize com `to_table()`.
- **Distribuição de cargas**: use `get_zone_distributions()` e `plot_zone_distribution_stacked()` para auditar intensidade semanal.
- **Análise de volume**: `get_weekly_volumes()` e `plot_weekly_volume()` ajudam a detectar picos bruscos.
- **Restrições de tempo**: o gerador respeita limites de duração por sessão, priorizando treinos-chave mesmo com pouco tempo disponível.
- **Compatibilidade**: planos sem zonas continuam funcionando; o arredondamento garante paces/distâncias amigáveis a relógios de treino.

## 🚀 Início Rápido

### 🌐 Google Colab (Mais Fácil - Sem Instalação!)

**Use o sistema direto no seu navegador sem instalar nada!**

1. **📱 Abra o notebook interativo no Google Colab:**
   - [🚀 Clique aqui para abrir no Colab](https://colab.research.google.com/github/tallesmedeiros/DecisionMaking/blob/main/create_plan_interactive.ipynb)

2. **⚙️ Execute a primeira célula para clonar os arquivos:**
   ```python
   !git clone https://github.com/tallesmedeiros/DecisionMaking.git
   %cd DecisionMaking
   ```

3. **📝 Preencha suas informações nas 12 seções interativas**

4. **🎉 Receba seu plano personalizado!**

📖 **[Ver guia completo em Português](GUIA_GOOGLE_COLAB.md)**

**🎁 O que você recebe:**
- ✅ Plano personalizado com base em seus dados (idade, peso, lesões, tempo disponível)
- ✅ Zonas de treino calculadas automaticamente dos seus tempos de prova
- ✅ Ajustes inteligentes para lesões e risco de lesão
- ✅ Treinos limitados ao tempo que você tem disponível
- ✅ Avisos e recomendações específicas para seu perfil
- ✅ Distâncias arredondadas (5km, 10km, 15km...)
- ✅ Tempos arredondados (30min, 1h, 1h30...)
- ✅ Tabela visual de zonas com emojis
- ✅ Gráficos de volume e distribuição de zonas

---

## 💻 Instalação Local

1. **📥 Clone este repositório:**
```bash
git clone https://github.com/tallesmedeiros/DecisionMaking.git
cd DecisionMaking
```

2. **🐍 Certifique-se de ter Python 3.7 ou superior instalado:**
```bash
python --version
```

**🎉 Sem dependências adicionais necessárias - usa apenas a biblioteca padrão do Python!**

## 🌡️ Registro de condições e hidratação

Para manter o plano alinhado às condições reais da prova e do treino:

- Use uma planilha ou app de treino para logar: temperatura (°C), umidade relativa (%), vento, ganho/percurso, RPE, peso pré/pós e ingestão de fluidos.
- Fotografe ou baixe os mapas de altimetria da prova e dos treinos-chave.
- Atualize semanalmente uma ficha de “Condições-alvo” vs. “Condições de treino”.

📄 Consulte o checklist e o modelo de ficha em [TRAINING_LOG_GUIDE.md](TRAINING_LOG_GUIDE.md).

## 📚 Modos de Uso

### 📓 Jupyter Notebook (Recomendado para Aprendizado)

Para uma experiência interativa e educacional com exemplos e visualizações:
```bash
jupyter notebook create_plan_interactive.ipynb
```

O notebook inclui:
- 📝 12 seções interativas com exemplos
- 🎓 Tutoriais passo a passo em português
- 📊 Visualização da progressão do treino
- 🎨 Guia de personalização
- 💡 Dicas e melhores práticas de treino

### 🖥️ Modo Interativo (CLI)

Execute a CLI em modo interativo para uma experiência guiada:
```bash
python cli.py
```

### ⚡ Criação Rápida de Plano

Gere um plano com padrões inteligentes:
```bash
python cli.py quick
```

### 👀 Visualizar Plano Existente

Visualize um plano de treino salvo:
```bash
python cli.py view meu_plano.json
```

---

## 🔄 Integração com Intervals.icu

**✨ NOVO!** Envie seu plano de treino diretamente para sua conta Intervals.icu e acompanhe seus treinos pelo app!

### 📋 O que é Intervals.icu?

[Intervals.icu](https://intervals.icu) é uma plataforma gratuita e poderosa para análise de treinos e planejamento. Com essa integração, você pode:

- 📱 Ver seus treinos planejados no app móvel ou web
- 📊 Acompanhar execução vs planejado
- 📈 Analisar métricas de performance
- ⌚ Sincronizar com Garmin, Polar, Wahoo, etc.

### ⚙️ Configuração (Apenas Primeira Vez)

**1. Obter suas credenciais:**

1. Acesse https://intervals.icu/
2. Faça login na sua conta
3. Vá em **Settings** (Configurações)
4. Clique em **Developer**
5. Copie sua **API Key** completa (formato: `athlete_12345:chave_longa`)
6. O **athlete_id** é o número que aparece após `athlete_`

**2. Configurar no sistema:**

**Opção A - Via Notebook (Google Colab):**

Nos notebooks, execute a célula de configuração e preencha:

```python
from intervals_integration import create_config_file

# Substitua pelos seus valores:
minha_api_key = "athlete_12345:sua_chave_completa_aqui"
meu_athlete_id = "12345"

create_config_file(minha_api_key, meu_athlete_id)
```

**Opção B - Manualmente:**

Crie um arquivo `intervals_config.json` na raiz do projeto:

```json
{
  "api_key": "athlete_12345:sua_chave_completa",
  "athlete_id": "12345"
}
```

⚠️ **IMPORTANTE**: Este arquivo contém credenciais sensíveis e já está no `.gitignore` - nunca compartilhe ou faça commit dele!

### 🚀 Como Usar

**No Jupyter Notebook:**

Após gerar seu plano, execute:

```python
from intervals_integration import IntervalsUploader

uploader = IntervalsUploader()
uploader.upload_plan(plan)
```

**Via Python (programaticamente):**

```python
from running_plan import RunningPlan
from intervals_integration import IntervalsUploader

# Carregar plano existente
plan = RunningPlan.load_from_file("meu_plano.json")

# Fazer upload
uploader = IntervalsUploader()
success = uploader.upload_plan(plan)

if success:
    print("✅ Plano enviado com sucesso!")
```

### ✅ Testar Conexão

Antes de fazer upload, teste se suas credenciais estão corretas:

```python
from intervals_integration import IntervalsUploader

uploader = IntervalsUploader()
uploader.test_connection()
```

### 🎯 O que é enviado?

O sistema envia cada treino do seu plano como um **evento planejado** no calendário Intervals.icu:

- 📅 Data e hora do treino
- 🏃 Tipo de treino (Easy Run, Tempo, Interval, etc)
- ⏱️ Duração estimada
- 📝 Descrição completa do treino
- 🎯 Estrutura detalhada com segmentos (aquecimento, principal, desaquecimento)
- 📊 Zonas de intensidade

### 📱 Acompanhamento

Após o upload:

1. Acesse https://intervals.icu/athletes/SEU_ID/calendar
2. Veja todos os seus treinos planejados no calendário
3. Use o app móvel Intervals.icu para ver treinos do dia
4. Complete os treinos e compare planejado vs executado

---

## 💡 Exemplos de Uso

### 🎯 Criação Básica de Plano

```bash
python cli.py
```

Depois siga as instruções:
- Escolha "Criar novo plano (detalhado)"
- Digite o nome do plano
- Selecione o objetivo de corrida (5K, 10K, Meia Maratona, Maratona)
- Escolha o nível de experiência (iniciante, intermediário, avançado)
- Defina o número de semanas
- Defina os dias de treino por semana
- Opcionalmente defina a data de início

### 🆕 Avançado: Plano com Zonas de Treino

Crie um plano personalizado com treinos baseados em pace:

```bash
python example_with_zones.py
```

Ou use a API Python:

```python
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from datetime import datetime

# 1. Configure as zonas de treino baseadas em tempos recentes de prova
zones = TrainingZones(method='jack_daniels')  # ou 'critical_velocity'

# Adicione seus tempos recentes de prova (formato: "MM:SS" ou "HH:MM:SS")
race_5k = RaceTime.from_time_string(5.0, "22:30")   # 5K em 22:30
race_10k = RaceTime.from_time_string(10.0, "47:15")  # 10K em 47:15

zones.add_race_time("5K Recente", race_5k)
zones.add_race_time("10K Recente", race_10k)
zones.calculate_zones()

# Visualize suas zonas de treino com tabela linda
print(zones.to_table())  # Mostra VDOT e faixas de pace para cada zona

# 2. Gere plano COM zonas de treino
plan = PlanGenerator.generate_plan(
    name="Meu Plano 10K com Zonas",
    goal="10K",
    level="intermediate",
    weeks=10,
    days_per_week=4,
    training_zones=zones  # Passe as zonas aqui!
)

plan.set_start_date(datetime(2025, 1, 6))

# 3. Visualize treino detalhado
week4 = plan.get_week(4)
for workout in week4.workouts:
    print(workout)  # Mostra pace, tempo e estrutura detalhada

# 4. Salve o plano
plan.save_to_file("meu_plano_com_zonas.json")

# 5. Obtenha volumes semanais para análise
volumes = plan.get_weekly_volumes()
print(f"Volumes: {volumes}")

# 6. Obtenha distribuição de zonas
distributions = plan.get_zone_distributions()
```

## ✅ Testes e Validação

- **Testes automatizados**: execute `python -m pytest` para validar geração de planos, integração de perfis e arredondamentos.
- **Sanidade manual**: gere um plano curto (4–6 semanas) e confira se volumes semanais sobem gradualmente e o taper reduz ~30% na última semana.
- **Conferência de paces**: compare a tabela de zonas com seus tempos recentes e ajuste o método (VDOT vs Velocidade Crítica) se notar discrepâncias de ritmo.
- **Validação de upload**: antes de enviar ao Intervals.icu, use `IntervalsUploader.test_connection()` para garantir que a API Key está correta.

### 📊 Visualizações (Jupyter Notebook)

```python
from plot_utils import plot_weekly_volume, plot_zone_distribution_stacked, print_zone_summary
import matplotlib.pyplot as plt

# Gráfico de volume semanal com gradiente de cores
fig, ax = plot_weekly_volume(plan)
plt.show()

# Gráfico de distribuição de zonas (empilhado)
fig, ax = plot_zone_distribution_stacked(plan)
plt.show()

# Resumo textual de distribuição
print_zone_summary(plan)
```

### 🔧 Uso Básico da API (Sem Zonas)

```python
from plan_generator import PlanGenerator
from datetime import datetime

# Gere um plano básico
plan = PlanGenerator.generate_plan(
    name="Meu Treino de Maratona",
    goal="Marathon",
    level="intermediate",
    weeks=16,
    days_per_week=5
)

# Defina a data de início
plan.set_start_date(datetime(2025, 1, 1))

# Salve em arquivo
plan.save_to_file("meu_plano_maratona.json")

# Exiba o plano
print(plan)

# Carregue de arquivo
from running_plan import RunningPlan
loaded_plan = RunningPlan.load_from_file("meu_plano_maratona.json")
```

## 🏋️ Estrutura do Plano de Treino

### 🎯 Tipos de Treino

- **🟢 Corrida Fácil (Easy Run)**: Ritmo confortável, esforço conversacional
- **🟡 Tempo Run**: Esforço sustentado em ritmo confortavelmente difícil
- **🟠 Treino Intervalado (Interval Training)**: Trabalho de velocidade com segmentos rápidos/recuperação
- **🌈 Fartlek**: Jogo de ritmos, alternando velocidades
- **🔵 Longão (Long Run)**: Construção de resistência em ritmo fácil
- **😴 Descanso (Rest)**: Dia de recuperação

### 📈 Fases de Treino

1. **🏗️ Fase de Construção** (70% do plano): Aumento gradual da quilometragem semanal
2. **⛰️ Fase de Manutenção**: Carga máxima de treino
3. **📉 Fase de Redução (Taper)** (últimas 2 semanas): Volume reduzido para recuperação

### 📏 Metas de Distância Semanal

A quilometragem semanal base varia por objetivo e nível:

| Objetivo | Iniciante | Intermediário | Avançado |
|----------|-----------|---------------|----------|
| 5K | 20 km | 30 km | 40 km |
| 10K | 30 km | 45 km | 60 km |
| Meia Maratona | 40 km | 60 km | 80 km |
| Maratona | 50 km | 75 km | 100 km |

## 📁 Estrutura de Arquivos

```
DecisionMaking/
├── 🖥️ cli.py                           # Interface de linha de comando
├── 🏃 running_plan.py                   # Classes principais (RunningPlan, Week, Workout, WorkoutSegment)
├── 🎯 plan_generator.py                 # Lógica de geração do plano de treino
├── 📊 training_zones.py                 # Calculadora de zonas de treino (VDOT & Velocidade Crítica)
├── 👤 user_profile.py                   # Sistema de perfil de usuário com lesões e personalização
├── 📈 plot_utils.py                     # Utilitários de visualização (gráficos)
├── 📓 create_plan_interactive.ipynb     # Notebook Jupyter (tutorial interativo)
├── 📓 running_plan_creator.ipynb        # Notebook Jupyter (versão educacional)
├── 🧪 test_example.py                   # Script básico de teste e demonstração
├── 🧪 test_enhanced.py                  # Script de teste de funcionalidades avançadas
├── 🧪 test_new_features.py              # Testes das novas funcionalidades (arredondamento, zonas)
├── 📝 example_with_zones.py             # Exemplo de uso com zonas de treino
├── 📖 GUIA_GOOGLE_COLAB.md              # Guia completo em português para Google Colab
├── 🙈 .gitignore                        # Arquivos ignorados pelo Git
└── 📄 README.md                         # Este arquivo
```

## 📋 Exemplo de Saída

### 🔤 Plano Básico (Sem Zonas)

```
==================================================
Plano de Corrida: Meu Treino de Maratona
Objetivo: Maratona
Nível: Intermediário
Duração: 16 semanas
Dias de Treino: 5 dias/semana
Data de Início: 2025-01-01
Data da Prova: 2025-04-30
==================================================

=== Semana 1 ===
Distância Total: 25 km
Notas: Bem-vindo ao seu plano de treino! Comece devagar e foque na consistência.

Segunda: Corrida Fácil - 5 km
  Comece a semana com ritmo confortável
Terça: Corrida Fácil - 5 km
  Ritmo de recuperação
Quarta: Descanso
  Dia de recuperação
Quinta: Corrida Fácil - 5 km
  Construa base aeróbica
Sexta: Corrida Fácil - 5 km
  Corrida curta de recuperação
Sábado: Descanso
  Dia de recuperação
Domingo: Longão - 10 km
  Construa resistência em ritmo conversacional
```

### 🆕 Plano Avançado (Com Zonas de Treino)

```
================================================================================
🏃‍♂️ SUAS ZONAS DE TREINAMENTO (JACK DANIELS)
================================================================================

💪 VDOT: 43.4

┌──────────────────────────────────────────────────────────────────────────────┐
│ Zona                 │ Emoji  │ Pace/km        │ % FCMax   │ Uso                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ 🟢 Easy/Recovery     │ 🟢      │ 5:28 - 6:33    │ 65-75%    │ Regeneração, base aeróbica │
│ 🔵 Marathon Pace     │ 🔵      │ 4:57 - 5:25    │ 75-84%    │ Resistência aeróbica │
│ 🟡 Threshold/Tempo   │ 🟡      │ 4:46 - 5:00    │ 84-88%    │ Limiar anaeróbico    │
│ 🟠 Interval/5K       │ 🟠      │ 4:18 - 4:29    │ 95-98%    │ VO2max               │
│ 🔴 Repetition/Fast   │ 🔴      │ 3:42 - 4:08    │ 98-100%   │ Velocidade máxima    │
└──────────────────────────────────────────────────────────────────────────────┘

💡 Dicas de uso:
  • 🟢 Easy: 70-80% do volume semanal
  • 🔵 Marathon: Treinos longos e ritmo de prova
  • 🟡 Threshold: 1-2x por semana, máx 60min total
  • 🟠 Interval: 1x por semana, séries curtas
  • 🔴 Repetition: Ocasional, velocidade pura

----------------------------------------------------------------------
SEMANA 4 - Com Treinos de Qualidade
----------------------------------------------------------------------

📍 Terça: 🟢 Fácil: 10.0km @ 5:16/km [52:40]

📍 Quinta: 🔴 Intervalos: 1.1km aquec + 4x500m @ 4:23/km c/ 2min rec + 1.2km volta calma

📍 Sexta: 🟢 Fácil: 5.0km @ 5:16/km [26:20]

📍 Domingo: 🔵 Longão: 15.0km @ 5:25/km [1:21:15]
```

### 📊 Resumo de Distribuição de Zonas

```
============================================================
📊 RESUMO DE DISTRIBUIÇÃO DE ZONAS - PLANO COMPLETO
============================================================

📏 Volume Total: 230.0km

🟢 Easy/Recovery        : 190.0km ( 82.6%)
🔵 Marathon Pace        :   0.0km (  0.0%)
🟡 Threshold/Tempo      :  20.0km (  8.7%)
🟠 Interval/5K          :  20.0km (  8.7%)
🔴 Repetition/Fast      :   0.0km (  0.0%)
============================================================
```

## 💡 Dicas para o Sucesso

1. **🐢 Comece Conservador**: Melhor treinar um pouco menos do que arriscar lesões
2. **👂 Ouça Seu Corpo**: Tire dias extras de descanso se necessário
3. **🔑 Consistência é a Chave**: Treino regular é mais importante que treinos individuais
4. **😴 Recuperação Importa**: Dias de descanso são quando seu corpo se adapta e fica mais forte
5. **🏊 Treino Cruzado**: Considere natação, ciclismo ou musculação nos dias de descanso
6. **🍎 Nutrição & Hidratação**: Alimente seu treino adequadamente
7. **🎯 Confie no Plano**: Especialmente durante o taper - resista à vontade de fazer mais

## 🔧 Personalização

O gerador de planos usa padrões inteligentes, mas você pode personalizar:
- Modifique `GOAL_TARGETS` em `plan_generator.py` para ajustar quilometragem semanal
- Edite distribuições de treino nos métodos `_generate_X_day_week`
- Ajuste percentagens de construção/taper no método `_generate_week`
- Use funções de arredondamento `round_to_nearest_5km()` e `round_to_nearest_30min()` para valores personalizados

## 🤝 Contribuindo

Sinta-se à vontade para enviar issues, solicitações de funcionalidades ou pull requests!

## 📜 Licença

Este projeto é código aberto e está disponível sob a Licença MIT.

## ⚠️ Aviso Legal

Este software gera planos de treino gerais. Sempre consulte um profissional de saúde antes de iniciar um novo programa de exercícios. Ouça seu corpo e ajuste o plano conforme necessário para prevenir lesões.

---

## 🎉 Recursos Recentes Adicionados

### ✨ Última Atualização

- ✅ **Arredondamento inteligente** de distâncias (múltiplos de 5km) e tempos (múltiplos de 30min)
- ✅ **Tabela visual de zonas** com emojis e formatação linda
- ✅ **Rastreamento de distribuição de zonas** por semana
- ✅ **Gráficos de visualização** com gradiente de cores
- ✅ **Sistema completo de perfil de usuário** com lesões e personalização
- ✅ **Notebook interativo** para Google Colab
- ✅ **Guia completo em português** para Google Colab

---

**🏃‍♂️ Bons treinos! 🎉**
