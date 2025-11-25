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

    # Training Zones (Recent Race Times)
    recent_race_times: Dict[str, str] = field(default_factory=dict)  # {"5K": "22:30", "10K": "47:15"}
    zones_calculation_method: str = "jack_daniels"  # "jack_daniels" or "critical_velocity"
    zone_mix_preference: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.55,
        "tempo": 0.25,
        "interval": 0.20,
    })

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

    # Equipment Access
    available_equipment: List[str] = field(default_factory=list)

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

        # Training zones
        if self.recent_race_times:
            result += f"\n🏃 Tempos Recentes:\n"
            for distance, time in self.recent_race_times.items():
                result += f"   • {distance}: {time}\n"
            result += f"Método de cálculo: {self.zones_calculation_method}\n"

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
            result += f"   Nível de Risco: {self.get_injury_risk_level()}\n"

        # Equipment
        if self.available_equipment:
            result += f"\n🔧 Equipamentos: {', '.join(self.available_equipment)}\n"

        # Recommendations
        needs_mod, mods = self.needs_modified_plan()
        if needs_mod:
            result += f"\n⚠️  Modificações Recomendadas:\n"
            for mod in mods:
                result += f"   • {mod}\n"

        result += "="*70 + "\n"

        return result
