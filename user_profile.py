"""
User Profile module for Running Plan Creator.
Stores comprehensive user information for personalized training plans.
"""
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
import json


@dataclass
class RaceGoal:
    """Represents a race goal (main or test race)."""
    distance: str  # "5K", "10K", "Half Marathon", "Marathon"
    date: date
    name: str = ""
    location: str = ""
    is_main_goal: bool = False
    target_time: Optional[str] = None  # "HH:MM:SS" or "MM:SS"

    def to_dict(self) -> Dict:
        return {
            "distance": self.distance,
            "date": self.date.isoformat(),
            "name": self.name,
            "location": self.location,
            "is_main_goal": self.is_main_goal,
            "target_time": self.target_time
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RaceGoal':
        data_copy = data.copy()
        data_copy['date'] = date.fromisoformat(data['date'])
        return cls(**data_copy)


@dataclass
class UserProfile:
    """Comprehensive user profile for personalized training."""

    # Personal Information
    name: str = ""
    age: int = 0
    weight_kg: float = 0.0
    height_cm: float = 0.0
    gender: str = ""  # "M", "F", or ""

    # Running Experience
    years_running: float = 0.0
    current_weekly_km: float = 0.0
    average_weekly_km: float = 0.0  # Média de volume nas últimas semanas
    recent_peak_weekly_km: float = 0.0  # Maior volume recente
    consistent_days_per_week: int = 0  # Dias/semana já mantidos
    tolerated_workouts: List[str] = field(default_factory=list)  # Tipos de treinos já tolerados
    adherence_score: Optional[float] = None  # % de aderência a planos anteriores
    experience_level: str = "beginner"  # "beginner", "intermediate", "advanced"

    # Goals
    main_race: Optional[RaceGoal] = None
    test_races: List[RaceGoal] = field(default_factory=list)
    secondary_objectives: List[str] = field(default_factory=list)  # "performance", "health", "weight_loss", etc.

    # Time Availability
    days_per_week: int = 4
    hours_per_day: float = 1.0
    preferred_time: str = ""  # "morning", "afternoon", "evening"
    preferred_location: List[str] = field(default_factory=list)  # "track", "road", "trail", "treadmill"
    preferred_days: List[str] = field(default_factory=list)
    stressful_blocks: Dict[str, List[str]] = field(default_factory=dict)  # {"Monday": ["evening"], "Thursday": ["morning"]}
    long_run_preference_days: List[str] = field(default_factory=list)  # Days with more free time for long runs
    use_alternating_weeks: bool = False
    alternate_stressful_blocks: Dict[str, List[str]] = field(default_factory=dict)
    alternate_long_run_days: List[str] = field(default_factory=list)
    weekly_schedule: Dict[str, List[Dict[str, object]]] = field(default_factory=dict)

    # Session logistics
    default_warmup_minutes: int = 10
    default_cooldown_minutes: int = 10
    commute_minutes: int = 0

    # Training Zones (Recent Race Times)
    recent_race_times: Dict[str, str] = field(default_factory=dict)  # {"5K": "22:30", "10K": "47:15"}
    zones_calculation_method: str = "jack_daniels"  # "jack_daniels" or "critical_velocity"
    zone_mix_preference: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.55,
        "tempo": 0.25,
        "interval": 0.20,
    })
    vdot_estimate: Optional[float] = None

    # Heart Rate (optional)
    hr_resting: Optional[int] = None
    hr_max: Optional[int] = None

    # Training structure preferences
    initial_weekly_km: Optional[float] = None
    session_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "intervals": True,
        "tempo": True,
        "long_run": True,
        "cross_training": False,
    })

    # Injury History
    previous_injuries: List[str] = field(default_factory=list)
    current_injuries: List[str] = field(default_factory=list)
    injury_triggers: List[str] = field(default_factory=list)  # Gatilhos que agravam sintomas
    red_zones: List[str] = field(default_factory=list)  # Restrições críticas para evitar overload

    # Equipment Access
    available_equipment: List[str] = field(default_factory=list)

    # Prevention & Impact Management
    strength_routines: List[str] = field(default_factory=list)  # Exercícios de força/prevenção em uso
    impact_limitations: List[str] = field(default_factory=list)  # Ex.: evitar descidas, superfícies duras
    feedback_required: bool = True  # Solicitar feedback frequente para ajustes

    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # Common injury list for reference
    COMMON_INJURIES = [
        "Fascite Plantar",
        "Canelite (Periostite Tibial)",
        "Síndrome da Banda Iliotibial",
        "Tendinite Patelar",
        "Tendinite de Aquiles",
        "Fratura por Estresse",
        "Condromalácia Patelar",
        "Síndrome do Piriforme",
        "Bursite Trocantérica",
        "Estiramento Muscular (Posterior de Coxa)"
    ]

    SECONDARY_OBJECTIVES_OPTIONS = [
        "Performance/Tempo",
        "Saúde Geral",
        "Perda de Peso",
        "Manutenção de Peso",
        "Bem-estar Mental",
        "Socialização",
        "Desafio Pessoal",
        "Qualificação para Prova"
    ]

    EQUIPMENT_OPTIONS = [
        "Relógio GPS/Smartwatch",
        "Monitor de Frequência Cardíaca",
        "Acesso a Pista de Atletismo",
        "Esteira",
        "Rolo de Massagem/Foam Roller",
        "Faixas de Resistência",
        "Academia"
    ]

    TOLERATED_WORKOUT_OPTIONS = [
        "Corridas fáceis/rodagens",
        "Intervalos curtos",
        "Intervalos longos",
        "Tempo run",
        "Fartlek",
        "Longões progressivos",
        "Treino de trilha/terreno variado"
    ]

    def calculate_bmi(self) -> float:
        """Calculate Body Mass Index."""
        if self.weight_kg > 0 and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return 0.0

    def get_bmi_category(self) -> str:
        """Get BMI category."""
        bmi = self.calculate_bmi()
        if bmi == 0:
            return "Não calculado"
        elif bmi < 18.5:
            return "Abaixo do peso"
        elif bmi < 25:
            return "Peso normal"
        elif bmi < 30:
            return "Sobrepeso"
        else:
            return "Obesidade"

    def estimate_hr_max(self) -> int:
        """Estimate maximum heart rate if not provided."""
        if self.hr_max:
            return self.hr_max
        if self.age > 0:
            # Using Tanaka formula: 208 - (0.7 × age)
            return int(208 - (0.7 * self.age))
        return 0

    def get_initial_volume_km(self) -> float:
        """Return starting weekly volume used by the plan generator."""
        if self.initial_weekly_km and self.initial_weekly_km > 0:
            return float(self.initial_weekly_km)
        if self.current_weekly_km > 0:
            return round(self.current_weekly_km * 1.1, 1)
        # Fallback based on experience level
        level_defaults = {"beginner": 20.0, "intermediate": 30.0, "advanced": 40.0}
        return level_defaults.get(self.experience_level, 20.0)

    def get_weekly_time_budget(self) -> float:
        """Calculate total weekly time budget in hours."""
        return self.days_per_week * self.hours_per_day

    def get_zone_mix(self) -> Dict[str, float]:
        """Return normalized training zone mix preferences."""
        mix = {**self.zone_mix_preference}
        total = sum(mix.values()) or 1.0
        return {zone: round(value / total, 2) for zone, value in mix.items()}

    def get_session_preferences(self) -> Dict[str, bool]:
        """Return session-type selections with sensible defaults."""
        defaults = {
            "intervals": True,
            "tempo": True,
            "long_run": True,
            "cross_training": False,
        }
        combined = {**defaults, **self.session_preferences}
        # If injury risk is high, automatically reduce intensity
        if self.get_injury_risk_level() == "Alto":
            combined["intervals"] = False
        return combined

    def to_generator_params(self) -> Dict[str, object]:
        """Map profile information to PlanGenerator-friendly parameters."""
        return {
            "initial_volume_km": self.get_initial_volume_km(),
            "days_per_week": self.get_recommended_days_per_week(),
            "zone_mix": self.get_zone_mix(),
            "session_preferences": self.get_session_preferences(),
            "preferred_days": self.preferred_days,
            "time_budget_hours": self.get_weekly_time_budget(),
        }

    def has_injury_history(self, injury_type: str) -> bool:
        """Check if user has history of specific injury."""
        return injury_type in self.previous_injuries or injury_type in self.current_injuries

    def get_injury_risk_level(self) -> str:
        """Assess overall injury risk level."""
        risk_score = 0

        # Current injuries increase risk
        if self.current_injuries:
            risk_score += 3

        # Multiple previous injuries
        if len(self.previous_injuries) > 2:
            risk_score += 2

        # High BMI increases risk
        bmi = self.calculate_bmi()
        if bmi > 28:
            risk_score += 2

        # Low experience with high volume
        if self.years_running < 2 and self.current_weekly_km > 40:
            risk_score += 2

        # Determine risk level
        if risk_score >= 5:
            return "Alto"
        elif risk_score >= 3:
            return "Moderado"
        else:
            return "Baixo"

    def get_recommended_days_per_week(self) -> int:
        """Get recommended training days based on profile."""
        if self.experience_level == "beginner":
            return min(self.days_per_week, 4)
        elif self.experience_level == "intermediate":
            return min(self.days_per_week, 5)
        else:  # advanced
            return self.days_per_week

    def get_day_schedule(self, day: str) -> List[Dict[str, object]]:
        """Return time blocks for a given day name (case-insensitive)."""
        normalized_day = day.capitalize()
        return self.weekly_schedule.get(normalized_day, self.weekly_schedule.get(day, []))

    def get_max_session_minutes(self, day: str) -> Optional[int]:
        """Return the most restrictive max session duration for the day."""
        blocks = self.get_day_schedule(day)
        max_values = [b.get('max_minutes') for b in blocks if b.get('max_minutes')]
        if max_values:
            return min(int(v) for v in max_values)
        if self.hours_per_day:
            return int(self.hours_per_day * 60)
        return None

    def get_surfaces_for_day(self, day: str) -> List[str]:
        """Return available surfaces for the day (from schedule or preferences)."""
        blocks = self.get_day_schedule(day)
        surfaces = []
        for block in blocks:
            surfaces.extend(block.get('surfaces', []))
        # Fallback to general preference
        if not surfaces and self.preferred_location:
            surfaces.extend(self.preferred_location)
        # Normalize and deduplicate
        normalized = []
        for surface in surfaces:
            if surface and surface not in normalized:
                normalized.append(surface)
        return normalized

    def needs_modified_plan(self) -> Tuple[bool, List[str]]:
        """
        Check if plan needs modifications based on profile.

        Returns:
            (needs_modification, list_of_reasons)
        """
        modifications = []

        if self.current_injuries:
            modifications.append(f"Lesões atuais: {', '.join(self.current_injuries)}")

        if "Canelite (Periostite Tibial)" in self.previous_injuries:
            modifications.append("Histórico de canelite - reduzir volume inicial")

        if "Fascite Plantar" in self.previous_injuries:
            modifications.append("Histórico de fascite - incluir mais descanso")

        if self.calculate_bmi() > 28:
            modifications.append("IMC elevado - progressão mais gradual")

        if self.years_running < 1:
            modifications.append("Pouca experiência - plano conservador")

        if self.get_weekly_time_budget() < 3:
            modifications.append("Pouco tempo disponível - treinos mais curtos")

        if self.red_zones:
            modifications.append(f"Zonas vermelhas a respeitar: {', '.join(self.red_zones)}")

        if self.impact_limitations:
            modifications.append(f"Limites de impacto: {', '.join(self.impact_limitations)}")

        return (len(modifications) > 0, modifications)

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for serialization."""
        data = asdict(self)

        # Convert dates to ISO format
        if self.main_race:
            data['main_race'] = self.main_race.to_dict()

        data['test_races'] = [race.to_dict() for race in self.test_races]
        data['created_date'] = self.created_date.isoformat()
        data['last_updated'] = self.last_updated.isoformat()

        return data

    def save_to_file(self, filename: str):
        """Save profile to JSON file."""
        self.last_updated = datetime.now()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filename: str) -> 'UserProfile':
        """Load profile from JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct race goals
        if data.get('main_race'):
            data['main_race'] = RaceGoal.from_dict(data['main_race'])

        if data.get('test_races'):
            data['test_races'] = [RaceGoal.from_dict(race) for race in data['test_races']]

        # Reconstruct dates
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])

        return cls(**data)

    def __str__(self):
        """String representation of user profile."""
        result = "\n" + "="*70 + "\n"
        result += "👤 PERFIL DO ATLETA\n"
        result += "="*70 + "\n"

        # Personal info
        if self.name:
            result += f"Nome: {self.name}\n"
        if self.age:
            result += f"Idade: {self.age} anos\n"
        if self.weight_kg and self.height_cm:
            bmi = self.calculate_bmi()
            result += f"Peso: {self.weight_kg}kg | Altura: {self.height_cm}cm | IMC: {bmi} ({self.get_bmi_category()})\n"

        # Experience
        result += f"\n📊 Experiência: {self.years_running} anos correndo\n"
        result += f"Nível: {self.experience_level.capitalize()}\n"
        result += f"Kilometragem semanal atual: {self.current_weekly_km}km\n"
        if self.average_weekly_km:
            result += f"Volume médio recente: {self.average_weekly_km}km/sem\n"
        if self.recent_peak_weekly_km:
            result += f"Pico recente: {self.recent_peak_weekly_km}km/sem\n"
        if self.consistent_days_per_week:
            result += f"Dias mantidos por semana: {self.consistent_days_per_week}\n"
        if self.tolerated_workouts:
            result += f"Treinos já tolerados: {', '.join(self.tolerated_workouts)}\n"
        if self.adherence_score is not None:
            result += f"Aderência histórica: {self.adherence_score}%\n"

        # Goals
        if self.main_race:
            result += f"\n🎯 Prova Principal: {self.main_race.distance}"
            if self.main_race.name:
                result += f" - {self.main_race.name}"
            result += f"\n   Data: {self.main_race.date.strftime('%d/%m/%Y')}"
            if self.main_race.target_time:
                result += f" | Meta: {self.main_race.target_time}"
            result += "\n"

        if self.test_races:
            result += f"\n📝 Provas Teste:\n"
            for race in self.test_races:
                result += f"   • {race.distance} em {race.date.strftime('%d/%m/%Y')}"
                if race.name:
                    result += f" - {race.name}"
                result += "\n"

        if self.secondary_objectives:
            result += f"\n💡 Objetivos Secundários: {', '.join(self.secondary_objectives)}\n"

        # Availability
        result += f"\n⏰ Disponibilidade: {self.days_per_week} dias/semana"
        result += f" | {self.hours_per_day}h/dia (Total: {self.get_weekly_time_budget()}h/semana)\n"
        if self.preferred_time:
            result += f"Horário preferido: {self.preferred_time}\n"
        if self.preferred_location:
            result += f"Local preferido: {', '.join(self.preferred_location)}\n"
        if self.stressful_blocks:
            result += "Blocos de alto estresse (evitar treinos-chave):\n"
            for day, periods in self.stressful_blocks.items():
                label = f"   • {day}"
                if periods:
                    label += f" ({', '.join(periods)})"
                result += label + "\n"
        if self.long_run_preference_days:
            result += f"Dias com mais tempo para longões: {', '.join(self.long_run_preference_days)}\n"
        if self.use_alternating_weeks:
            result += "Agenda alternada (semanas A/B): ativa\n"
            if self.alternate_stressful_blocks:
                result += "  Semana B - blocos críticos: "
                formatted = [f"{day} ({', '.join(periods)})" if periods else day for day, periods in self.alternate_stressful_blocks.items()]
                result += ", ".join(formatted) + "\n"
            if self.alternate_long_run_days:
                result += f"  Semana B - longão preferido: {', '.join(self.alternate_long_run_days)}\n"

        if self.weekly_schedule:
            result += "Grade semanal:\n"
            for day, blocks in self.weekly_schedule.items():
                for block in blocks:
                    start = block.get('start', '')
                    end = block.get('end', '')
                    max_minutes = block.get('max_minutes')
                    surfaces = ", ".join(block.get('surfaces', []))
                    block_str = f"   • {day}: {start}-{end}" if start or end else f"   • {day}"
                    if max_minutes:
                        block_str += f" | Máx: {max_minutes}min"
                    if surfaces:
                        block_str += f" | Acessos: {surfaces}"
                    result += block_str + "\n"

        # Training zones
        if self.recent_race_times:
            result += f"\n🏃 Tempos Recentes:\n"
            for distance, time in self.recent_race_times.items():
                result += f"   • {distance}: {time}\n"
            result += f"Método de cálculo: {self.zones_calculation_method}\n"
        if self.vdot_estimate:
            result += f"Estimativa de VDOT (Jack Daniels): {self.vdot_estimate:.1f}\n"

        # Heart rate
        if self.hr_resting or self.hr_max:
            result += f"\n❤️  Frequência Cardíaca:\n"
            if self.hr_resting:
                result += f"   Repouso: {self.hr_resting} bpm\n"
            hr_max = self.estimate_hr_max()
            if hr_max:
                result += f"   Máxima: {hr_max} bpm"
                if not self.hr_max:
                    result += " (estimada)"
                result += "\n"

        # Injuries
        if self.previous_injuries or self.current_injuries:
            result += f"\n🩹 Histórico de Lesões:\n"
            if self.current_injuries:
                result += f"   Lesões Atuais: {', '.join(self.current_injuries)}\n"
            if self.previous_injuries:
                result += f"   Lesões Prévias: {', '.join(self.previous_injuries)}\n"
            if self.injury_triggers:
                result += f"   Gatilhos a evitar: {', '.join(self.injury_triggers)}\n"
            if self.red_zones:
                result += f"   Zonas Vermelhas (sobrecarga): {', '.join(self.red_zones)}\n"
            result += f"   Nível de Risco: {self.get_injury_risk_level()}\n"

        # Equipment
        if self.available_equipment:
            result += f"\n🔧 Equipamentos: {', '.join(self.available_equipment)}\n"

        # Prevention / Strength routines
        if self.strength_routines:
            result += f"\n🏋️  Força/Prevenção em uso: {', '.join(self.strength_routines)}\n"

        if self.impact_limitations:
            result += f"\n⬇️  Limites de Impacto: {', '.join(self.impact_limitations)}\n"

        if self.feedback_required:
            result += "\n💬 Feedback: Retornar sensações semanalmente para ajustes finos no plano.\n"

        # Recommendations
        needs_mod, mods = self.needs_modified_plan()
        if needs_mod:
            result += f"\n⚠️  Modificações Recomendadas:\n"
            for mod in mods:
                result += f"   • {mod}\n"

        result += "="*70 + "\n"

        return result
