"""
Biblioteca de Rotinas de Treino
Contém sessões pré-definidas para cada categoria de treino.
As sessões são selecionadas com base no nível do atleta e fase do treinamento.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import random


class WorkoutCategory(Enum):
    """Categorias de treino disponíveis."""
    EASY = "easy"
    LONG = "long"
    TEMPO = "tempo"
    INTERVAL = "interval"
    RECOVERY = "recovery"
    THRESHOLD = "threshold"


class TrainingPhase(Enum):
    """Fases do ciclo de treinamento."""
    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RECOVERY = "recovery"


class AthleteLevel(Enum):
    """Níveis de experiência do atleta."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class WorkoutSession:
    """
    Representa uma sessão de treino pré-definida.

    Attributes:
        id: Identificador único da sessão
        name: Nome da sessão (ex: "Fartlek Pirâmide")
        category: Categoria do treino
        description: Descrição detalhada do treino
        emoji: Emoji representativo
        min_level: Nível mínimo requerido
        phases: Fases do treinamento onde é apropriado
        structure: Estrutura detalhada do treino
        duration_range: (min, max) duração em minutos
        distance_range: (min, max) distância em km
        intensity: Intensidade geral (1-10)
        benefits: Lista de benefícios do treino
        tips: Dicas para execução
    """
    id: str
    name: str
    category: WorkoutCategory
    description: str
    emoji: str
    min_level: AthleteLevel
    phases: List[TrainingPhase]
    structure: List[Dict]
    duration_range: tuple
    distance_range: tuple
    intensity: int
    benefits: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)

    def is_suitable_for(self, level: AthleteLevel, phase: TrainingPhase) -> bool:
        """Verifica se a sessão é adequada para o nível e fase."""
        level_order = [AthleteLevel.BEGINNER, AthleteLevel.INTERMEDIATE, AthleteLevel.ADVANCED]
        return (level_order.index(level) >= level_order.index(self.min_level)
                and phase in self.phases)

    def to_description(self, distance_km: float = None, duration_min: int = None) -> str:
        """Gera descrição formatada do treino."""
        parts = [f"{self.emoji} {self.name}"]

        if distance_km:
            parts.append(f"📏 {distance_km:.1f}km")
        if duration_min:
            parts.append(f"⏱️ {duration_min}min")

        return " | ".join(parts) + f"\n{self.description}"


# =============================================================================
# 🚶 SESSÕES EASY (Corrida Leve)
# =============================================================================

EASY_SESSIONS = [
    WorkoutSession(
        id="easy_01",
        name="Corrida Leve Básica",
        category=WorkoutCategory.EASY,
        description="Corrida contínua em ritmo confortável, onde você consegue manter uma conversa",
        emoji="🚶",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.PEAK, TrainingPhase.TAPER, TrainingPhase.RECOVERY],
        structure=[
            {"segment": "Corrida leve", "zone": "Z2", "effort": "Conversação fácil"}
        ],
        duration_range=(30, 60),
        distance_range=(5, 10),
        intensity=3,
        benefits=["Recuperação ativa", "Base aeróbica", "Queima de gordura"],
        tips=["Mantenha ritmo onde consegue conversar", "Não se preocupe com pace"]
    ),
    WorkoutSession(
        id="easy_02",
        name="Corrida Regenerativa",
        category=WorkoutCategory.EASY,
        description="Corrida muito leve focada em recuperação, ritmo bem tranquilo",
        emoji="🧘",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.PEAK, TrainingPhase.TAPER, TrainingPhase.RECOVERY],
        structure=[
            {"segment": "Corrida regenerativa", "zone": "Z1-Z2", "effort": "Muito fácil"}
        ],
        duration_range=(20, 40),
        distance_range=(3, 7),
        intensity=2,
        benefits=["Recuperação muscular", "Fluxo sanguíneo", "Relaxamento"],
        tips=["Pode ser mais lento que o normal", "Foco em sensação, não velocidade"]
    ),
    WorkoutSession(
        id="easy_03",
        name="Corrida com Strides",
        category=WorkoutCategory.EASY,
        description="Corrida leve com 4-6 acelerações curtas (strides) de 20-30 segundos no final",
        emoji="⚡",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Corrida leve", "duration": "80%", "zone": "Z2"},
            {"segment": "Strides", "reps": "4-6x", "duration": "20-30s", "recovery": "60s caminhada"}
        ],
        duration_range=(35, 50),
        distance_range=(6, 9),
        intensity=4,
        benefits=["Trabalho neuromuscular", "Economia de corrida", "Ativação muscular"],
        tips=["Strides são acelerações suaves, não sprints", "Mantenha boa postura nos strides"]
    ),
    WorkoutSession(
        id="easy_04",
        name="Corrida em Trilha Leve",
        category=WorkoutCategory.EASY,
        description="Corrida em terreno variado (trilha, parque) em ritmo confortável",
        emoji="🌲",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.RECOVERY],
        structure=[
            {"segment": "Corrida em trilha", "zone": "Z2", "terrain": "variado"}
        ],
        duration_range=(30, 60),
        distance_range=(5, 10),
        intensity=3,
        benefits=["Fortalecimento de tornozelos", "Variedade mental", "Trabalho de propriocepção"],
        tips=["Cuidado com o terreno irregular", "Ajuste o ritmo conforme necessário"]
    ),
    WorkoutSession(
        id="easy_05",
        name="Corrida Progressiva Leve",
        category=WorkoutCategory.EASY,
        description="Começa bem leve e termina em ritmo moderado (ainda conversacional)",
        emoji="📈",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD],
        structure=[
            {"segment": "Primeiro terço", "zone": "Z1", "effort": "Muito fácil"},
            {"segment": "Segundo terço", "zone": "Z2", "effort": "Fácil"},
            {"segment": "Terço final", "zone": "Z2-Z3", "effort": "Moderado"}
        ],
        duration_range=(40, 60),
        distance_range=(7, 12),
        intensity=4,
        benefits=["Ensina controle de ritmo", "Prepara para progressivos", "Simulação de corrida"],
        tips=["Progressão deve ser gradual", "Termine sentindo que poderia continuar"]
    ),
]


# =============================================================================
# 🏃‍♂️ SESSÕES LONG (Longão)
# =============================================================================

LONG_SESSIONS = [
    WorkoutSession(
        id="long_01",
        name="Longão Clássico",
        category=WorkoutCategory.LONG,
        description="Corrida longa contínua em ritmo confortável para construir resistência aeróbica",
        emoji="🏃‍♂️",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Corrida contínua", "zone": "Z2", "effort": "Conversacional"}
        ],
        duration_range=(60, 150),
        distance_range=(12, 32),
        intensity=4,
        benefits=["Resistência aeróbica", "Eficiência metabólica", "Fortalecimento mental"],
        tips=["Hidrate-se bem", "Considere gel/carboidrato após 60-90min"]
    ),
    WorkoutSession(
        id="long_02",
        name="Longão Progressivo",
        category=WorkoutCategory.LONG,
        description="Longão que inicia leve e acelera nos últimos 20-30% para ritmo de prova",
        emoji="🔥",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z1"},
            {"segment": "Parte principal", "distance": "70%", "zone": "Z2"},
            {"segment": "Progressão", "distance": "20-30%", "zone": "Z3-Z4", "effort": "Ritmo de prova"}
        ],
        duration_range=(75, 150),
        distance_range=(15, 35),
        intensity=6,
        benefits=["Simula corrida de prova", "Ensina pacing negativo", "Resistência à fadiga"],
        tips=["Não acelere cedo demais", "Os últimos km devem ser desafiadores mas controlados"]
    ),
    WorkoutSession(
        id="long_03",
        name="Longão com Blocos de Ritmo",
        category=WorkoutCategory.LONG,
        description="Longão com inserções de blocos em ritmo de prova (ex: 3x10min)",
        emoji="⚡",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "3km", "zone": "Z2"},
            {"segment": "Bloco 1", "duration": "10-15min", "zone": "Z3-Z4", "effort": "Ritmo de prova"},
            {"segment": "Recuperação", "duration": "5min", "zone": "Z2"},
            {"segment": "Bloco 2", "duration": "10-15min", "zone": "Z3-Z4"},
            {"segment": "Recuperação", "duration": "5min", "zone": "Z2"},
            {"segment": "Bloco 3", "duration": "10-15min", "zone": "Z3-Z4"},
            {"segment": "Volta calma", "distance": "2km", "zone": "Z1"}
        ],
        duration_range=(90, 150),
        distance_range=(18, 32),
        intensity=7,
        benefits=["Resistência específica", "Capacidade de manter ritmo cansado", "Simulação de prova"],
        tips=["Mantenha os blocos consistentes", "Não vá forte demais nos primeiros blocos"]
    ),
    WorkoutSession(
        id="long_04",
        name="Longão em Terreno Variado",
        category=WorkoutCategory.LONG,
        description="Longão em percurso com subidas e descidas para simular provas onduladas",
        emoji="⛰️",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD],
        structure=[
            {"segment": "Corrida em terreno variado", "zone": "Z2-Z3", "terrain": "ondulado"}
        ],
        duration_range=(75, 140),
        distance_range=(14, 28),
        intensity=5,
        benefits=["Força em subidas", "Técnica em descidas", "Preparação para provas onduladas"],
        tips=["Economize nas subidas", "Use as descidas para recuperar"]
    ),
    WorkoutSession(
        id="long_05",
        name="Longão com Finish Fast",
        category=WorkoutCategory.LONG,
        description="Longão com os últimos 3-5km em ritmo forte, simulando sprint final de prova",
        emoji="🏁",
        min_level=AthleteLevel.ADVANCED,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Corrida principal", "distance": "85%", "zone": "Z2"},
            {"segment": "Finish fast", "distance": "3-5km", "zone": "Z4", "effort": "Forte"}
        ],
        duration_range=(90, 150),
        distance_range=(20, 35),
        intensity=7,
        benefits=["Capacidade de acelerar cansado", "Confiança mental", "Simulação de sprint final"],
        tips=["Reserve energia para o final", "O finish deve ser desafiador mas sustentável"]
    ),
    WorkoutSession(
        id="long_06",
        name="Longão de Recuperação",
        category=WorkoutCategory.LONG,
        description="Longão mais curto em ritmo muito leve, usado em semanas de recuperação",
        emoji="🧘",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.RECOVERY, TrainingPhase.TAPER],
        structure=[
            {"segment": "Corrida leve", "zone": "Z1-Z2", "effort": "Muito confortável"}
        ],
        duration_range=(50, 90),
        distance_range=(10, 18),
        intensity=3,
        benefits=["Manutenção da resistência", "Recuperação ativa", "Preparação mental"],
        tips=["Não acelere mesmo se sentir bem", "Foco em relaxamento"]
    ),
]


# =============================================================================
# 💨 SESSÕES INTERVAL (Intervalado)
# =============================================================================

INTERVAL_SESSIONS = [
    WorkoutSession(
        id="interval_01",
        name="Intervalos Curtos 400m",
        category=WorkoutCategory.INTERVAL,
        description="8-12x 400m com recuperação de 200m trote ou 90s",
        emoji="💨",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "Tiros", "reps": "8-12x", "distance": "400m", "zone": "Z5", "recovery": "200m trote"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(45, 60),
        distance_range=(8, 12),
        intensity=8,
        benefits=["VO2max", "Velocidade", "Economia de corrida"],
        tips=["Mantenha ritmo consistente em todos os tiros", "A recuperação é ativa, não pare"]
    ),
    WorkoutSession(
        id="interval_02",
        name="Intervalos Médios 800m",
        category=WorkoutCategory.INTERVAL,
        description="5-8x 800m com 400m de recuperação em trote",
        emoji="🔄",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "Tiros", "reps": "5-8x", "distance": "800m", "zone": "Z4-Z5", "recovery": "400m trote"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(50, 70),
        distance_range=(10, 14),
        intensity=8,
        benefits=["Capacidade anaeróbica", "Resistência de velocidade", "Limiar de lactato"],
        tips=["Primeiro tiro não deve ser o mais rápido", "Mantenha boa forma mesmo cansado"]
    ),
    WorkoutSession(
        id="interval_03",
        name="Intervalos Longos 1000m",
        category=WorkoutCategory.INTERVAL,
        description="4-6x 1000m com 400-600m de recuperação",
        emoji="🎯",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "Tiros", "reps": "4-6x", "distance": "1000m", "zone": "Z4", "recovery": "400-600m trote"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(55, 75),
        distance_range=(11, 15),
        intensity=8,
        benefits=["Limiar de lactato", "Resistência específica", "Controle de ritmo"],
        tips=["Ritmo de 5K ou ligeiramente mais rápido", "Foco em manter o ritmo constante"]
    ),
    WorkoutSession(
        id="interval_04",
        name="Pirâmide",
        category=WorkoutCategory.INTERVAL,
        description="Pirâmide: 400-800-1200-800-400m com recuperação igual à metade da distância",
        emoji="🔺",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "400m", "zone": "Z5", "recovery": "200m"},
            {"segment": "800m", "zone": "Z4-Z5", "recovery": "400m"},
            {"segment": "1200m", "zone": "Z4", "recovery": "600m"},
            {"segment": "800m", "zone": "Z4-Z5", "recovery": "400m"},
            {"segment": "400m", "zone": "Z5", "recovery": "200m"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(55, 70),
        distance_range=(10, 13),
        intensity=8,
        benefits=["Variedade de estímulos", "Controle de ritmo", "Engajamento mental"],
        tips=["Os 1200m são o pico - não vá rápido demais", "Cada distância tem seu ritmo ideal"]
    ),
    WorkoutSession(
        id="interval_05",
        name="Fartlek Estruturado",
        category=WorkoutCategory.INTERVAL,
        description="Fartlek com estrutura: alternar 3min forte / 2min fácil por 20-30min",
        emoji="🎲",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD],
        structure=[
            {"segment": "Aquecimento", "duration": "10min", "zone": "Z2"},
            {"segment": "Bloco Fartlek", "duration": "20-30min", "pattern": "3min Z4 / 2min Z2"},
            {"segment": "Volta calma", "duration": "10min", "zone": "Z1"}
        ],
        duration_range=(40, 55),
        distance_range=(8, 11),
        intensity=6,
        benefits=["Introdução a intervalos", "Flexibilidade", "Trabalho aeróbico/anaeróbico"],
        tips=["Não precisa de pista", "Ajuste o esforço conforme sensação"]
    ),
    WorkoutSession(
        id="interval_06",
        name="Repetições de 200m",
        category=WorkoutCategory.INTERVAL,
        description="12-16x 200m rápidos com 200m de recuperação",
        emoji="🚀",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "Tiros", "reps": "12-16x", "distance": "200m", "zone": "Z5+", "recovery": "200m trote"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(45, 60),
        distance_range=(9, 13),
        intensity=9,
        benefits=["Velocidade pura", "Economia de corrida", "Recrutamento muscular"],
        tips=["Velocidade de 800m/1500m", "Mantenha boa técnica mesmo no final"]
    ),
    WorkoutSession(
        id="interval_07",
        name="Intervalos Cruise (Tempo)",
        category=WorkoutCategory.INTERVAL,
        description="4-5x 1600m em ritmo de limiar com 60-90s de recuperação",
        emoji="⏱️",
        min_level=AthleteLevel.ADVANCED,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "Tiros", "reps": "4-5x", "distance": "1600m", "zone": "Z4", "recovery": "60-90s parado"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(55, 75),
        distance_range=(12, 16),
        intensity=7,
        benefits=["Limiar de lactato", "Resistência de ritmo", "Eficiência metabólica"],
        tips=["Ritmo de 10K ou half marathon", "Recuperação curta é proposital"]
    ),
    WorkoutSession(
        id="interval_08",
        name="Escada Descendente",
        category=WorkoutCategory.INTERVAL,
        description="1600-1200-800-400m com velocidade aumentando e recuperação decrescente",
        emoji="📉",
        min_level=AthleteLevel.ADVANCED,
        phases=[TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "distance": "2km", "zone": "Z2"},
            {"segment": "1600m", "zone": "Z4", "recovery": "400m"},
            {"segment": "1200m", "zone": "Z4-Z5", "recovery": "300m"},
            {"segment": "800m", "zone": "Z5", "recovery": "200m"},
            {"segment": "400m", "zone": "Z5+", "recovery": "nenhuma"},
            {"segment": "Volta calma", "distance": "1.5km", "zone": "Z1"}
        ],
        duration_range=(50, 65),
        distance_range=(10, 13),
        intensity=9,
        benefits=["Velocidade progressiva", "Capacidade de acelerar cansado", "Simulação de sprint final"],
        tips=["Guarde energia para os últimos tiros", "O 400m final é all-out"]
    ),
]


# =============================================================================
# ⚡ SESSÕES TEMPO
# =============================================================================

TEMPO_SESSIONS = [
    WorkoutSession(
        id="tempo_01",
        name="Tempo Run Clássico",
        category=WorkoutCategory.TEMPO,
        description="20-40min contínuos em ritmo de limiar (confortavelmente desconfortável)",
        emoji="⚡",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "duration": "10-15min", "zone": "Z2"},
            {"segment": "Tempo", "duration": "20-40min", "zone": "Z4", "effort": "Confortavelmente difícil"},
            {"segment": "Volta calma", "duration": "10min", "zone": "Z1"}
        ],
        duration_range=(45, 70),
        distance_range=(10, 15),
        intensity=7,
        benefits=["Limiar de lactato", "Eficiência em ritmo de prova", "Resistência mental"],
        tips=["Ritmo onde falar é difícil mas possível", "Não comece rápido demais"]
    ),
    WorkoutSession(
        id="tempo_02",
        name="Tempo Intervalado",
        category=WorkoutCategory.TEMPO,
        description="3-4x 10min em ritmo de limiar com 2-3min de recuperação",
        emoji="🔁",
        min_level=AthleteLevel.INTERMEDIATE,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD],
        structure=[
            {"segment": "Aquecimento", "duration": "10min", "zone": "Z2"},
            {"segment": "Bloco tempo", "reps": "3-4x", "duration": "10min", "zone": "Z4", "recovery": "2-3min Z2"},
            {"segment": "Volta calma", "duration": "10min", "zone": "Z1"}
        ],
        duration_range=(55, 75),
        distance_range=(11, 16),
        intensity=7,
        benefits=["Acúmulo de tempo em limiar", "Mais acessível que tempo contínuo", "Progressão gradual"],
        tips=["Ideal para quem está começando com tempo runs", "Mantenha ritmo consistente nos blocos"]
    ),
    WorkoutSession(
        id="tempo_03",
        name="Tempo Progressivo",
        category=WorkoutCategory.TEMPO,
        description="30min começando em ritmo de maratona e terminando em ritmo de 10K",
        emoji="📈",
        min_level=AthleteLevel.ADVANCED,
        phases=[TrainingPhase.BUILD, TrainingPhase.PEAK],
        structure=[
            {"segment": "Aquecimento", "duration": "10min", "zone": "Z2"},
            {"segment": "Progressão", "duration": "30min", "zones": "Z3→Z4→Z4+", "pattern": "10min cada zona"},
            {"segment": "Volta calma", "duration": "10min", "zone": "Z1"}
        ],
        duration_range=(50, 60),
        distance_range=(11, 14),
        intensity=8,
        benefits=["Controle de ritmo", "Capacidade de acelerar", "Simulação de negative split"],
        tips=["Primeira parte deve parecer fácil", "Termine forte mas não destruído"]
    ),
]


# =============================================================================
# 🧘 SESSÕES RECOVERY
# =============================================================================

RECOVERY_SESSIONS = [
    WorkoutSession(
        id="recovery_01",
        name="Corrida de Recuperação",
        category=WorkoutCategory.RECOVERY,
        description="Corrida muito leve focada exclusivamente em recuperação",
        emoji="🧘",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.BASE, TrainingPhase.BUILD, TrainingPhase.PEAK, TrainingPhase.TAPER, TrainingPhase.RECOVERY],
        structure=[
            {"segment": "Corrida leve", "zone": "Z1", "effort": "Muito fácil, pode caminhar se necessário"}
        ],
        duration_range=(20, 40),
        distance_range=(3, 6),
        intensity=2,
        benefits=["Recuperação ativa", "Fluxo sanguíneo", "Recuperação mental"],
        tips=["Mais lento é melhor", "Pode alternar corrida e caminhada"]
    ),
    WorkoutSession(
        id="recovery_02",
        name="Shake-out Run",
        category=WorkoutCategory.RECOVERY,
        description="Corrida curta e leve, ideal para dia antes de prova ou treino forte",
        emoji="🌅",
        min_level=AthleteLevel.BEGINNER,
        phases=[TrainingPhase.TAPER, TrainingPhase.PEAK],
        structure=[
            {"segment": "Corrida leve", "duration": "15-25min", "zone": "Z1-Z2"},
            {"segment": "Strides opcionais", "reps": "2-4x", "duration": "15s", "zone": "Z4"}
        ],
        duration_range=(15, 30),
        distance_range=(2, 5),
        intensity=2,
        benefits=["Ativação muscular", "Soltar as pernas", "Preparação mental"],
        tips=["Não se preocupe com ritmo", "Strides são opcionais e curtos"]
    ),
]


# =============================================================================
# BIBLIOTECA COMPLETA
# =============================================================================

class WorkoutLibrary:
    """
    Biblioteca central de todas as sessões de treino.
    Permite buscar e selecionar sessões por categoria, nível e fase.
    """

    def __init__(self):
        self.sessions: Dict[WorkoutCategory, List[WorkoutSession]] = {
            WorkoutCategory.EASY: EASY_SESSIONS,
            WorkoutCategory.LONG: LONG_SESSIONS,
            WorkoutCategory.INTERVAL: INTERVAL_SESSIONS,
            WorkoutCategory.TEMPO: TEMPO_SESSIONS,
            WorkoutCategory.RECOVERY: RECOVERY_SESSIONS,
        }

    def get_sessions(self, category: WorkoutCategory) -> List[WorkoutSession]:
        """Retorna todas as sessões de uma categoria."""
        return self.sessions.get(category, [])

    def get_suitable_sessions(
        self,
        category: WorkoutCategory,
        level: AthleteLevel,
        phase: TrainingPhase
    ) -> List[WorkoutSession]:
        """Retorna sessões adequadas para o nível e fase especificados."""
        sessions = self.get_sessions(category)
        return [s for s in sessions if s.is_suitable_for(level, phase)]

    def select_session(
        self,
        category: WorkoutCategory,
        level: AthleteLevel,
        phase: TrainingPhase,
        exclude_ids: List[str] = None
    ) -> Optional[WorkoutSession]:
        """
        Seleciona uma sessão aleatória adequada para os parâmetros.

        Args:
            category: Categoria do treino
            level: Nível do atleta
            phase: Fase do treinamento
            exclude_ids: IDs de sessões a excluir (para evitar repetição)

        Returns:
            Uma sessão de treino ou None se não houver disponível
        """
        suitable = self.get_suitable_sessions(category, level, phase)

        if exclude_ids:
            suitable = [s for s in suitable if s.id not in exclude_ids]

        if not suitable:
            # Fallback: retorna qualquer sessão da categoria
            suitable = self.get_sessions(category)
            if exclude_ids:
                suitable = [s for s in suitable if s.id not in exclude_ids]

        return random.choice(suitable) if suitable else None

    def get_session_by_id(self, session_id: str) -> Optional[WorkoutSession]:
        """Busca uma sessão pelo ID."""
        for sessions in self.sessions.values():
            for session in sessions:
                if session.id == session_id:
                    return session
        return None

    def list_all_sessions(self) -> List[WorkoutSession]:
        """Lista todas as sessões disponíveis."""
        all_sessions = []
        for sessions in self.sessions.values():
            all_sessions.extend(sessions)
        return all_sessions

    def get_session_summary(self) -> Dict[str, int]:
        """Retorna um resumo da quantidade de sessões por categoria."""
        return {
            cat.value: len(sessions)
            for cat, sessions in self.sessions.items()
        }


# Instância global da biblioteca
workout_library = WorkoutLibrary()


def get_workout_session(
    category: str,
    level: str = "intermediate",
    phase: str = "build",
    exclude_ids: List[str] = None
) -> Optional[WorkoutSession]:
    """
    Função de conveniência para obter uma sessão de treino.

    Args:
        category: "easy", "long", "interval", "tempo", "recovery"
        level: "beginner", "intermediate", "advanced"
        phase: "base", "build", "peak", "taper", "recovery"
        exclude_ids: Lista de IDs a excluir

    Returns:
        WorkoutSession ou None
    """
    try:
        cat = WorkoutCategory(category.lower())
        lvl = AthleteLevel(level.lower())
        ph = TrainingPhase(phase.lower())
        return workout_library.select_session(cat, lvl, ph, exclude_ids)
    except (ValueError, KeyError):
        return None


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Demonstração da biblioteca
    print("=" * 60)
    print("📚 BIBLIOTECA DE ROTINAS DE TREINO")
    print("=" * 60)

    # Resumo
    summary = workout_library.get_session_summary()
    print("\n📊 Sessões disponíveis:")
    for category, count in summary.items():
        print(f"  • {category}: {count} sessões")

    # Exemplo de seleção
    print("\n🎯 Exemplo de seleção (Intervalado, Intermediário, Build):")
    session = get_workout_session("interval", "intermediate", "build")
    if session:
        print(f"  {session.emoji} {session.name}")
        print(f"  📝 {session.description}")
        print(f"  ⚡ Intensidade: {session.intensity}/10")
        print(f"  ✅ Benefícios: {', '.join(session.benefits[:2])}")

    print("\n🏃 Exemplo de seleção (Longão, Avançado, Peak):")
    session = get_workout_session("long", "advanced", "peak")
    if session:
        print(f"  {session.emoji} {session.name}")
        print(f"  📝 {session.description}")
