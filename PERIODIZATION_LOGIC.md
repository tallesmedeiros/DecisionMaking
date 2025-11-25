# 📊 Documentação: Lógica de Periodização e Geração de Treinos

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Periodização Linear](#periodização-linear)
3. [Distribuição de Volume](#distribuição-de-volume)
4. [Tipos de Treinos](#tipos-de-treinos)
5. [Estrutura Detalhada dos Treinos](#estrutura-detalhada-dos-treinos)
6. [Algoritmos de Geração](#algoritmos-de-geração)
7. [Oportunidades de Melhoria](#oportunidades-de-melhoria)

---

## 🎯 Visão Geral

O sistema utiliza **Periodização Linear** com 3 fases distintas:
- **Fase de Construção (70% do plano)**: Aumento progressivo de volume
- **Fase de Manutenção**: Volume constante no pico
- **Fase de Taper (últimas 2 semanas)**: Redução para recuperação pré-prova

**Localização no código:** `plan_generator.py:240-249`

### Raciocínio da periodização
- **Segurança primeiro**: o volume começa baixo e sobe de forma quase linear, evitando saltos abruptos para reduzir risco de lesão.
- **Pico sustentado**: manter 2-3 semanas em volume máximo ajuda a consolidar adaptações aeróbicas sem sobrecarregar o atleta.
- **Taper agressivo**: queda de 30% e depois 50% antes da prova maximiza recuperação mantendo estímulo neuromuscular.
- **Dias/semana adaptativos**: a distribuição de volume por dia varia conforme disponibilidade declarada, priorizando longão e sessões de qualidade.
- **Limites de tempo**: treinos são ajustados ao tempo disponível informado; se não cabe, o volume é redistribuído para não exceder duração.

---

## 📈 Periodização Linear

### 1. Volume Base por Objetivo e Nível

**Código:** `plan_generator.py:16-22`

```python
GOAL_TARGETS = {
    "5K": {"beginner": 20, "intermediate": 30, "advanced": 40},
    "10K": {"beginner": 30, "intermediate": 45, "advanced": 60},
    "Half Marathon": {"beginner": 40, "intermediate": 60, "advanced": 80},
    "Marathon": {"beginner": 50, "intermediate": 75, "advanced": 100},
}
```

**Interpretação:**
- Valores em **km/semana** no pico do treinamento
- Iniciantes têm 50% do volume de avançados
- Volume cresce 50% entre iniciante → intermediário
- Volume cresce 33% entre intermediário → avançado

### 2. Progressão Semanal

**Código:** `plan_generator.py:240-249`

```python
if week_number <= total_weeks * 0.7:  # Build phase (70%)
    weekly_distance = target_distance * (week_number / (total_weeks * 0.7)) * progression_factor
elif week_number <= total_weeks - 2:  # Maintenance phase
    weekly_distance = target_distance
else:  # Taper phase (últimas 2 semanas)
    taper_factor = 0.7 if week_number == total_weeks - 1 else 0.5
    weekly_distance = target_distance * taper_factor
```

**Exemplo Prático (Plano de 16 semanas, 10K intermediário, target = 45km):**

| Semana | Fase | Cálculo | Volume | % do Pico |
|--------|------|---------|--------|-----------|
| 1 | Construção | 45 × (1/11.2) | 4.0 km | 9% |
| 2 | Construção | 45 × (2/11.2) | 8.0 km | 18% |
| 4 | Construção | 45 × (4/11.2) | 16.1 km | 36% |
| 8 | Construção | 45 × (8/11.2) | 32.1 km | 71% |
| 11 | Construção | 45 × (11/11.2) | 44.2 km | 98% |
| 12 | Manutenção | 45 | 45.0 km | 100% |
| 13 | Manutenção | 45 | 45.0 km | 100% |
| 14 | Manutenção | 45 | 45.0 km | 100% |
| 15 | Taper | 45 × 0.7 | 31.5 km | 70% |
| 16 | Taper | 45 × 0.5 | 22.5 km | 50% |

**Características:**
- ✅ Aumento gradual e seguro
- ✅ Mantém pico por 3 semanas
- ✅ Taper agressivo (50% na semana da prova)
- ⚠️ **Limitação**: Não segue regra de 10% de aumento semanal

### 3. Semanas de Recuperação

**Código:** `plan_generator.py:283-284`

```python
elif week_number % 4 == 0 and week_number < total_weeks - 2:
    notes = "Recovery week - slightly reduced volume to absorb training."
```

**Problema Identificado:**
- ❌ Apenas adiciona **nota**, mas NÃO reduz volume efetivamente
- 💡 **Melhoria sugerida**: Reduzir volume em 20-30% a cada 4 semanas

---

## 📊 Distribuição de Volume

### Distribuição por Número de Dias/Semana

#### 3 Dias/Semana (`plan_generator.py:568-591`)

| Dia | Tipo | % Volume |
|-----|------|----------|
| Terça | Easy Run | 30% |
| Quinta | Tempo/Easy | 25% |
| Sábado | Long Run | 45% |

**Lógica:**
- Semanas 1-3: Todos easy runs
- Semana 4+: Introduz tempo run na quinta

#### 4 Dias/Semana (`plan_generator.py:594-623`)

| Dia | Tipo | % Volume |
|-----|------|----------|
| Terça | Easy Run | 25% |
| Quinta | Quality* | 22% |
| Sexta | Easy Run | 18% |
| Domingo | Long Run | 35% |

**Quality = Qualidade (depende da semana):**
- Semanas 1-2: Easy Run
- Semanas pares: Interval Training
- Semanas ímpares: Tempo Run

#### 5 Dias/Semana (`plan_generator.py:626-657`)

| Dia | Tipo | % Volume |
|-----|------|----------|
| Segunda | Easy Run | 20% |
| Terça | Easy Run | 18% |
| Quinta | Quality* | 20% |
| Sexta | Easy Run | 15% |
| Domingo | Long Run | 27% |

#### 6 Dias/Semana (`plan_generator.py:660-694`)

| Dia | Tipo | % Volume |
|-----|------|----------|
| Segunda | Easy Run | 18% |
| Terça | Easy Run | 16% |
| Quarta | Quality* | 18% |
| Quinta | Easy Run | 14% |
| Sexta | Easy Run | 12% |
| Domingo | Long Run | 22% |

**Quality (rotação a cada 3 semanas):**
- Semana % 3 == 0: Fartlek
- Semana % 3 == 1: Interval
- Semana % 3 == 2: Tempo

---

## 🏃 Tipos de Treinos

### 1. Easy Run (Corrida Fácil)

**Código:** `plan_generator.py:332-351`

**Estrutura:**
- **Zona:** Easy (Z1)
- **Pace alvo:** Middle of easy zone
- **Descrição:** "Ritmo confortável, esforço conversacional"

**Sem estrutura de segmentos** - treino contínuo

**Quando usado:**
- ✅ Base do treinamento (70-80% do volume)
- ✅ Dias entre treinos de qualidade
- ✅ Primeiras semanas do plano

### 2. Long Run (Longão)

**Código:** `plan_generator.py:354-373`

**Estrutura:**
- **Zona:** Easy (Z1)
- **Pace alvo:** Slower end of easy zone (mais devagar que easy run normal)
- **Descrição:** "Construir resistência em ritmo fácil"

**Sem estrutura de segmentos** - treino contínuo

**Características:**
- ✅ Treino mais longo da semana
- ✅ Ritmo mais lento que easy runs normais
- ✅ Foco em resistência aeróbica

**Distribuição típica:**
- 3 dias/semana: 45% do volume
- 4 dias/semana: 35% do volume
- 5 dias/semana: 27% do volume
- 6 dias/semana: 22% do volume

### 3. Tempo Run (Treino de Limiar)

**Código:** `plan_generator.py:376-435`

**Estrutura completa com 3 segmentos:**

| Segmento | % Distância | Zona | Pace |
|----------|-------------|------|------|
| Aquecimento | 18% | Easy | Middle easy |
| Tempo (Principal) | 60% | Threshold | Middle threshold |
| Desaquecimento | 22% | Easy | Middle easy |

**Exemplo prático (10km total):**
```
Aquecimento:     1.8 km @ 6:00/km (Easy)
Tempo:           6.0 km @ 5:00/km (Threshold)
Desaquecimento:  2.2 km @ 6:00/km (Easy)
```

**Objetivo:**
- Treinar limiar anaeróbico (lactato threshold)
- Ritmo "confortavelmente difícil"
- Pode manter conversa curta

### 4. Interval Training (Treino Intervalado)

**Código:** `plan_generator.py:438-517`

**Estrutura completa com 4 segmentos:**

| Segmento | % Distância | Zona | Descrição |
|----------|-------------|------|-----------|
| Aquecimento | 20% | Easy | Preparação |
| Tiros | 36% (60% × 60%) | Interval (Z4) | 4-8 repetições |
| Recuperação | 24% (60% × 40%) | Easy | Entre tiros |
| Desaquecimento | 20% | Easy | Volta à calma |

**Lógica de Repetições:**

```python
num_repeats = max(4, min(8, int(work_km / 0.8)))
```

**Exemplo prático (10km total):**
```
Aquecimento:     2.0 km @ 6:00/km (Easy)
----
6x Tiros:        0.6 km @ 4:30/km (Interval - ritmo 5K)
6x Recuperação:  2 min trote/caminhada
----
Desaquecimento:  2.0 km @ 6:00/km (Easy)

Total: 6×0.6km = 3.6km de trabalho intenso
```

**Características:**
- Ritmo de 5K (VO2max)
- Recuperação de 2 minutos entre tiros
- 4-8 repetições dependendo do volume

**Problema Identificado:**
- ⚠️ Recuperação fixa em 2 minutos (não considera nível do atleta)
- 💡 **Melhoria**: Recuperação proporcional ao trabalho (1:1 para iniciantes, 1:0.5 para avançados)

### 5. Fartlek (Jogo de Ritmos)

**Código:** `plan_generator.py:520-565`

**Estrutura com 3 segmentos:**

| Segmento | % Distância | Zona | Descrição |
|----------|-------------|------|-----------|
| Aquecimento | 20% | Easy | Começar devagar |
| Fartlek | 65% | Variável | Alternar ritmos livremente |
| Desaquecimento | 15% | Easy | Finalizar com calma |

**Exemplo prático (10km total):**
```
Aquecimento:     2.0 km @ 6:00/km (Easy)
Fartlek:         6.5 km alternando:
                 - 1-3 min @ 4:30/km (Interval pace)
                 - 1-2 min @ 6:00/km (Easy pace)
Desaquecimento:  1.5 km @ 6:00/km (Easy)
```

**Características:**
- ✅ Sem estrutura rígida
- ✅ Variações de ritmo não planejadas
- ✅ Divertido e menos mental

**Problema:**
- ⚠️ Apenas descritivo - não tem segmentos estruturados para Intervals.icu
- 💡 **Melhoria**: Adicionar sugestão de estrutura (ex: 8×2min rápido + 1min fácil)

---

## 🔧 Algoritmos de Geração

### Fluxo de Decisão para Treinos de Qualidade

#### Plano de 4 Dias/Semana

```
INÍCIO
│
├─ Semana 1-2?
│  └─ SIM → Easy Run
│  └─ NÃO → Continua
│
├─ Semana % 2 == 0? (Par)
│  └─ SIM → Interval Training
│  └─ NÃO → Tempo Run
```

**Código:** `plan_generator.py:604-609`

```python
if week_num <= 2:
    workouts.append(cls._create_easy_run("Thursday", quality_distance, training_zones))
elif week_num % 2 == 0:
    workouts.append(cls._create_interval_run("Thursday", quality_distance, training_zones))
else:
    workouts.append(cls._create_tempo_run("Thursday", quality_distance, training_zones))
```

**Resultado em 16 semanas:**

| Semana | Treino de Qualidade |
|--------|---------------------|
| 1-2 | Easy Run |
| 3 | Tempo Run |
| 4 | Interval |
| 5 | Tempo Run |
| 6 | Interval |
| ... | Alternando |
| 15 | Tempo Run |
| 16 | Interval |

#### Plano de 6 Dias/Semana

```
INÍCIO
│
├─ Semana 1-2?
│  └─ SIM → Easy Run
│  └─ NÃO → Continua
│
├─ Semana % 3 == 0?
│  └─ SIM → Fartlek
│  └─ NÃO → Continua
│
├─ Semana % 3 == 1?
│  └─ SIM → Interval
│  └─ NÃO → Tempo Run
```

**Código:** `plan_generator.py:678-685`

**Resultado em 16 semanas:**

| Semana | Treino de Qualidade |
|--------|---------------------|
| 1-2 | Easy Run |
| 3 | Fartlek |
| 4 | Interval |
| 5 | Tempo |
| 6 | Fartlek |
| 7 | Interval |
| 8 | Tempo |
| 9 | Fartlek |
| ... | Rotação |

### Arredondamento Inteligente

**Distâncias:** Arredonda para múltiplos de 5km

```python
round_to_nearest_5km(distance_km)
```

**Exemplos:**
- 23.4 km → 25 km
- 18.2 km → 20 km
- 7.8 km → 10 km

**Tempos:** Arredonda para múltiplos de 30 minutos

```python
round_to_nearest_30min(time_minutes)
```

**Exemplos:**
- 47 min → 30 min
- 52 min → 60 min (1h)
- 83 min → 90 min (1h30)

---

## ⚠️ Problemas Identificados e Oportunidades de Melhoria

### 1. **Semanas de Recuperação Não Implementadas**

**Problema:**
```python
# Apenas adiciona nota, mas NÃO reduz volume
elif week_number % 4 == 0 and week_number < total_weeks - 2:
    notes = "Recovery week - slightly reduced volume to absorb training."
```

**Solução Sugerida:**
```python
# Reduzir volume efetivamente
if week_number % 4 == 0 and week_number < total_weeks - 2:
    weekly_distance *= 0.75  # Redução de 25%
    notes = "Recovery week - reduced volume (75%) to absorb training."
```

### 2. **Progressão Não Respeita Regra de 10%**

**Problema:**
- Semana 1→2 pode ter aumento de 100% (de 4km para 8km)
- Não há limite de progressão semanal

**Solução Sugerida:**
```python
# Limitar aumento máximo a 10% por semana
if week_number > 1:
    previous_distance = calculate_previous_week_distance(week_number - 1)
    max_allowed = previous_distance * 1.10
    weekly_distance = min(weekly_distance, max_allowed)
```

### 3. **Falta de Variação nos Treinos Intervalados**

**Problema Atual:**
- Sempre mesma estrutura de intervalos
- Sempre 400m-1km repeats
- Recuperação sempre 2 minutos

**Melhorias Possíveis:**

#### a) Periodização dos Intervalos

```python
# Intervalos curtos (400-600m) para velocidade
if week_num <= total_weeks * 0.4:
    repeat_distance = 0.5  # 500m
    num_repeats = 8-10
    pace = 'repetition'  # Mais rápido que 5K

# Intervalos médios (800-1200m) para VO2max
elif week_num <= total_weeks * 0.7:
    repeat_distance = 1.0  # 1000m
    num_repeats = 5-6
    pace = 'interval'  # Ritmo 5K

# Intervalos longos (1600-2000m) para transição aeróbica
else:
    repeat_distance = 1.6  # 1600m (milha)
    num_repeats = 4-5
    pace = 'threshold'  # Mais lento
```

#### b) Tipos de Intervalos Diferentes

**Pirâmide:**
```
200m - 400m - 800m - 1200m - 800m - 400m - 200m
```

**Ladder (Escada):**
```
400m - 800m - 1200m - 1600m - 1200m - 800m - 400m
```

**Cruise Intervals (Intervals de Cruzeiro):**
```
5 × 1600m @ threshold pace com 1min recuperação
```

**Yasso 800s (para maratona):**
```
10 × 800m @ tempo-alvo-maratona em minutos:segundos
Exemplo: Meta 4h marathon → 10×800m @ 4:00
```

### 4. **Falta de Progressão Específica para a Prova**

**Problema:**
- Não há treinos específicos de pace de prova
- Marathon pace, 10K pace não são treinados especificamente

**Solução Sugerida:**

```python
# Adicionar treinos específicos nas últimas 4-6 semanas
race_specific_weeks = range(total_weeks - 6, total_weeks - 2)

if week_num in race_specific_weeks:
    # Para maratona: Marathon Pace Runs
    if goal == "Marathon":
        create_marathon_pace_run(20km, pace='marathon')

    # Para 10K: 10K Pace Intervals
    elif goal == "10K":
        create_pace_intervals(8 × 1000m, pace='10K')

    # Para 5K: 5K Pace Repeats
    elif goal == "5K":
        create_pace_intervals(6 × 800m, pace='5K')
```

### 5. **Falta de Treinos de Força/Técnica**

**Melhorias Possíveis:**

```python
# Strides (tiros curtos de técnica)
def add_strides_to_easy_run(workout):
    """Adiciona 4-6 × 100m strides ao final de easy runs."""
    workout.add_segment(WorkoutSegment(
        name="Strides (técnica)",
        repetitions=4,
        distance_km=0.1,
        pace_per_km="rápido controlado",
        description="Acelerações de 100m para técnica de corrida"
    ))

# Hill Repeats (tiros de subida)
def create_hill_workout(distance_km):
    """Treino de subida para força."""
    return Workout(
        type="Hill Repeats",
        description="8 × 90s subida forte + descida fácil"
    )
```

### 6. **Não Considera Semanas de Competição**

**Problema:**
- Se atleta tem prova teste durante o ciclo, não ajusta o plano

**Solução:**
```python
# Reduzir volume na semana da prova teste
if week_has_test_race:
    weekly_distance *= 0.6  # Apenas 60% do volume
    # Substituir treino de qualidade pela prova
```

### 7. **Recuperação nos Intervalos é Genérica**

**Problema Atual:**
- Sempre 2 minutos, independente do nível

**Solução por Nível:**

```python
recovery_ratios = {
    'beginner': 1.0,      # Recuperação = Trabalho
    'intermediate': 0.75,  # Recuperação = 75% do trabalho
    'advanced': 0.5        # Recuperação = 50% do trabalho
}

# Se trabalho = 3min, recuperação:
# Iniciante: 3min
# Intermediário: 2:15min
# Avançado: 1:30min
```

### 8. **Long Runs Não Têm Variação**

**Melhorias Possíveis:**

**Progressive Long Run:**
```
75% do longão @ easy pace
25% final @ marathon pace ou threshold
```

**Long Run com Fast Finish:**
```
80% @ easy pace
20% @ tempo pace
```

**Long Run com Mid-tempo:**
```
25% @ easy
50% @ marathon pace
25% @ easy
```

---

## 📊 Resumo Visual da Periodização

### Gráfico de Volume (16 semanas, 10K Intermediário)

```
Volume (km)
50│                    ████████
  │                ████        ████
45│            ████
  │        ████
40│    ████
  │████                            ███
35│                                    ███
  │
30│                                        ██
  │                                          ██
25│
  │                                            ███
20│
  │
15│
  │
10│
  │
 5│
  │
 0└─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─
   1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
   │         │         │         │    │
   Build     Build     Maintain  Tap  Race
```

### Distribuição de Tipos de Treino (16 semanas, 4 dias/semana)

```
Semana │ Ter    │ Qui        │ Sex    │ Dom    │
───────┼────────┼────────────┼────────┼────────┤
1      │ Easy   │ Easy       │ Easy   │ Long   │
2      │ Easy   │ Easy       │ Easy   │ Long   │
3      │ Easy   │ Tempo      │ Easy   │ Long   │
4      │ Easy   │ Interval   │ Easy   │ Long   │
5      │ Easy   │ Tempo      │ Easy   │ Long   │
6      │ Easy   │ Interval   │ Easy   │ Long   │
7      │ Easy   │ Tempo      │ Easy   │ Long   │
8      │ Easy   │ Interval   │ Easy   │ Long   │
9      │ Easy   │ Tempo      │ Easy   │ Long   │
10     │ Easy   │ Interval   │ Easy   │ Long   │
11     │ Easy   │ Tempo      │ Easy   │ Long   │
12     │ Easy   │ Interval   │ Easy   │ Long   │
13     │ Easy   │ Tempo      │ Easy   │ Long   │
14     │ Easy   │ Interval   │ Easy   │ Long   │
15     │ Easy   │ Tempo      │ Easy   │ Long   │ ← Taper
16     │ Easy   │ Easy       │ Rest   │ RACE   │ ← Prova
```

---

## 🚀 Próximos Passos Recomendados

### Prioridade Alta (Implementação Imediata)

1. **✅ Implementar semanas de recuperação efetivas**
   - Reduzir volume a cada 4 semanas
   - Código em `plan_generator.py:240-249`

2. **✅ Adicionar limite de progressão de 10%**
   - Evitar lesões por sobrecarga
   - Código em `plan_generator.py:240-249`

3. **✅ Recuperação proporcional ao nível nos intervalos**
   - Ajustar tempo de recuperação por nível
   - Código em `plan_generator.py:470`

### Prioridade Média (Melhorias Incrementais)

4. **📊 Periodização dos intervalos**
   - Curtos → Médios → Longos
   - Adicionar em `plan_generator.py:438-517`

5. **🎯 Treinos específicos de pace de prova**
   - Marathon pace runs
   - Race pace intervals
   - Criar novos métodos `_create_marathon_pace_run()`, etc.

6. **📈 Variação nos long runs**
   - Progressive runs
   - Fast finish
   - Mid-tempo
   - Adicionar em `plan_generator.py:354-373`

### Prioridade Baixa (Refinamentos)

7. **💪 Treinos de força e técnica**
   - Strides
   - Hill repeats
   - Criar novos métodos

8. **🏁 Integração de provas teste**
   - Ajustar volume nas semanas de prova
   - Usar em `plan_generator.py:287-294`

9. **📊 Análise de carga de treino**
   - TRIMP score
   - TSS (Training Stress Score)
   - Criar módulo `training_load.py`

---

## 📚 Referências Utilizadas

1. **Jack Daniels' Running Formula**
   - VDOT e zonas de treino
   - Estrutura de intervalos

2. **Periodização Linear Clássica**
   - Build → Peak → Taper
   - Volume progressivo

3. **Princípios de Lydiard**
   - Base aeróbica (Easy runs)
   - Long runs consistentes

4. **Regra dos 10%**
   - Progressão segura de volume
   - Prevenção de lesões

---

**Documento gerado:** `PERIODIZATION_LOGIC.md`
**Versão:** 1.0
**Data:** 2025-11-23
**Autor:** Análise do código `plan_generator.py`
