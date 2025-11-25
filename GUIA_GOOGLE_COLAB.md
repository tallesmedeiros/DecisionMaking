# 🏃‍♂️ Guia de Uso no Google Colab

## 📱 Como usar o Criador de Planos de Treino no Google Colab

### ✅ Passo a Passo Completo

Este roteiro cobre desde abrir o notebook até baixar o plano gerado. Cada item pode ser executado sequencialmente em novas sessões do Colab.

---

## 1️⃣ Abrir o Notebook no Google Colab

### **Opção A: Direto do GitHub (Recomendado)**

1. Acesse: https://colab.research.google.com/
2. Clique em **`File`** → **`Open notebook`**
3. Selecione a aba **`GitHub`**
4. Cole a URL: `https://github.com/tallesmedeiros/DecisionMaking`
5. Selecione o notebook: **`create_plan_interactive.ipynb`**
6. Clique para abrir

💡 **Dica:** Na aba GitHub é possível pesquisar pelo usuário/repo (`tallesmedeiros/DecisionMaking`) se a URL inteira não carregar.

### **Opção B: Upload Manual**

1. Baixe o arquivo `create_plan_interactive.ipynb` do repositório
2. No Google Colab, clique em **`File`** → **`Upload notebook`**
3. Faça upload do arquivo

---

## 2️⃣ Fazer Upload dos Arquivos Python

**Primeira célula a executar:**

```python
# Clone o repositório com todos os arquivos necessários
!git clone https://github.com/tallesmedeiros/DecisionMaking.git
%cd DecisionMaking

# Verificar se os arquivos foram carregados
!ls -la *.py
```

**Você verá:**
- ✅ `user_profile.py`
- ✅ `training_zones.py`
- ✅ `running_plan.py`
- ✅ `plan_generator.py`

Se você já tem um arquivo de perfil ou plano salvo (JSON), faça upload em **Files** → **Upload** antes de rodar as células que carregam esses arquivos.

Para manter os arquivos após fechar o notebook, conecte ao **Google Drive** (menu lateral esquerdo → guia *Files* → botão *Mount Drive*) e copie os JSONs para lá.

---

## 3️⃣ Executar o Notebook Interativo

### **Execute as células em ordem sequencial (Shift+Enter)**

O notebook tem **12 seções** que você preenche passo a passo:

### 📝 **Seção 1: Informações Pessoais**
```python
NOME = "João Silva"
IDADE = 30
PESO_KG = 70.0
ALTURA_CM = 175.0
SEXO = "M"  # "M", "F" ou ""
```

### 🏃 **Seção 2: Experiência em Corrida**
```python
ANOS_CORRENDO = 2.0
KM_SEMANAL_ATUAL = 30.0
NIVEL_EXPERIENCIA = "intermediate"  # beginner, intermediate, advanced
```

### 🎯 **Seção 3: Objetivos e Provas**
```python
PROVA_DISTANCIA = "10K"  # "5K", "10K", "Half Marathon", "Marathon"
PROVA_DATA = "2025-04-15"  # Formato: AAAA-MM-DD
PROVA_NOME = "Corrida da Cidade"
PROVA_LOCAL = "São Paulo"
PROVA_TEMPO_META = "45:00"  # Opcional: MM:SS ou HH:MM:SS

OBJETIVOS_SECUNDARIOS = [
    "Performance/Tempo",
    "Saúde Geral",
    # "Perda de Peso",
    # "Desafio Pessoal",
]
```

### 🏁 **Seção 3.1: Provas Teste (Opcional)**
```python
PROVAS_TESTE = [
    # ("5K", "2025-03-01", "Prova Teste 5K"),
]
```

### ⏰ **Seção 4: Disponibilidade de Tempo**
```python
DIAS_POR_SEMANA = 4
HORAS_POR_DIA = 1.0
HORARIO_PREFERIDO = "morning"  # morning, afternoon, evening
LOCAIS_PREFERIDOS = ["road"]  # road, track, trail, treadmill
```

### 🏃‍♂️ **Seção 5: Zonas de Treinamento**
```python
# Preencha APENAS os tempos que você TEM
TEMPO_5K = "22:30"    # Exemplo: 22min30s
TEMPO_10K = "47:15"   # Exemplo: 47min15s
TEMPO_21K = ""        # Deixe vazio se não tiver
TEMPO_42K = ""        # Deixe vazio se não tiver

METODO_ZONAS = "jack_daniels"  # ou "critical_velocity"
```

### ❤️ **Seção 5.1: Frequência Cardíaca (Opcional)**
```python
FC_REPOUSO = None  # Exemplo: 55, ou deixe None
FC_MAXIMA = None   # Deixe None para estimar automaticamente
```

### 🩹 **Seção 6: Histórico de Lesões**
```python
LESOES_ATUAIS = []  # Lesões que você TEM AGORA

LESOES_PREVIAS = [
    # Selecione as que já teve:
    # "Canelite (Periostite Tibial)",
    # "Fascite Plantar",
    # "Tendinite de Aquiles",
]
```

**Opções disponíveis:**
1. Fascite Plantar
2. Canelite (Periostite Tibial)
3. Síndrome da Banda Iliotibial
4. Tendinite Patelar
5. Tendinite de Aquiles
6. Fratura por Estresse
7. Condromalácia Patelar
8. Síndrome do Piriforme
9. Bursite Trocantérica
10. Estiramento Muscular (Posterior de Coxa)

### 🔧 **Seção 7: Equipamentos**
```python
EQUIPAMENTOS = [
    "Relógio GPS/Smartwatch",
    # "Monitor de Frequência Cardíaca",
    # "Acesso a Pista de Atletismo",
    # "Esteira",
    # "Rolo de Massagem/Foam Roller",
    # "Faixas de Resistência",
    # "Academia",
]
```

### 📊 **Seção 8: Resumo do Perfil**
Execute a célula para ver um resumo completo do seu perfil.

### 💾 **Seção 9: Salvar Perfil**
Salva seu perfil em formato JSON para reuso futuro.

### 🎯 **Seção 10: Gerar Plano**
**O sistema automaticamente:**
- ✅ Calcula suas zonas de treino baseado nos tempos de prova
- ✅ Ajusta volume se você tem lesões ou risco alto
- ✅ Reduz volume se seu IMC está elevado
- ✅ Limita duração dos treinos ao tempo disponível
- ✅ Recomenda dias de descanso adequados
- ✅ Adiciona avisos específicos para suas lesões

### 👀 **Seção 11: Visualizar Plano**
Mostra seu plano em formato visual compacto com emojis:

```
📍 Segunda (22/11): 😴 Descanso
📍 Terça (23/11): 🟢 Fácil: 10.0km @ 5:16/km [52:40]
📍 Quarta (24/11): 😴 Descanso
📍 Quinta (25/11): 🔴 Intervalos: 1.1km aquec + 4x500m @ 4:23/km c/ 2min rec + 1.2km volta calma
📍 Sexta (26/11): 🟢 Fácil: 8.0km @ 5:16/km [42:08]
```

### 💾 **Seção 12: Salvar Plano**
Salva o plano completo em JSON.

👉 **Ordem de execução recomendada:** clique em **Runtime → Run all** ou use `Ctrl+F9` para executar todas as células do notebook já conectado ao repositório. Caso edite alguma configuração, reexecute somente a partir da célula de perfil para evitar inconsistências.

---

## 4️⃣ Fazer Download dos Arquivos Gerados

Execute esta célula no final:

```python
# Download dos arquivos gerados
from google.colab import files

# Download do perfil
files.download('meu_perfil.json')

# Download do plano (o nome varia conforme seu perfil)
# Exemplo: plano_10k_joao_silva.json
import glob
planos = glob.glob('plano_*.json')
if planos:
    files.download(planos[0])
    print(f"✓ Baixado: {planos[0]}")
```

---

## 🎯 O Que Você Receberá

1. **Perfil Salvo** (`meu_perfil.json`)
   - Pode ser reutilizado para criar novos planos
   - Contém todas suas informações

2. **Plano Personalizado** (`plano_10k_joao_silva.json`)
   - Semanas detalhadas de treino
   - Zonas de pace calculadas
   - Avisos e recomendações
   - Formato visual para impressão

---

## 💡 Dicas Importantes

### ✅ **Faça:**
- Execute as células **em ordem sequencial** (de cima para baixo)
- Preencha **todos os campos obrigatórios**
- Seja **honesto sobre lesões** e condição física
- Informe tempos de prova **recentes** (últimos 6 meses)

### ❌ **Evite:**
- Pular seções
- Informar dados incorretos (peso, altura, tempos)
- Omitir lesões atuais
- Definir metas irrealistas de tempo

---

## 🔄 Como Reutilizar Seu Perfil

Se você já tem um perfil salvo:

```python
from user_profile import UserProfile

# Fazer upload do arquivo meu_perfil.json primeiro
from google.colab import files
uploaded = files.upload()

# Carregar perfil
profile = UserProfile.load_from_file('meu_perfil.json')
print(profile)

# Agora pode pular direto para a Seção 10 (gerar novo plano)
```

---

## 🆘 Resolução de Problemas

### **Erro: "ModuleNotFoundError"**
**Solução:** Execute a célula de clone do repositório:
```python
!git clone https://github.com/tallesmedeiros/DecisionMaking.git
%cd DecisionMaking
```

### **Erro: "No such file or directory"**
**Solução:** Você está tentando rodar células fora de ordem. Volte e execute desde o início.

### **Plano não aparece com zonas de pace**
**Solução:** Você precisa informar pelo menos **um tempo de prova** na Seção 5.

### **Volume do plano está muito baixo**
**Isso é intencional!** O sistema reduziu baseado em:
- Lesões atuais ou históricas
- IMC elevado
- Pouca experiência
- Alto risco de lesão

---

## 📱 Link Direto para Google Colab

**Abrir notebook diretamente:**
```
https://colab.research.google.com/github/tallesmedeiros/DecisionMaking/blob/claude/build-basic-software-01X41XJpgLktdj8FhFWitNo3/create_plan_interactive.ipynb
```

---

## 🏃‍♂️ Pronto para Começar!

1. Abra o link acima no Google Colab
2. Execute a célula de clone do repositório
3. Preencha suas informações nas 12 seções
4. Receba seu plano personalizado!

**Bons treinos! 🎉**
