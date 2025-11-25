"""Ferramentas para analisar ambiente de prova versus treinos.

Inclui utilitários para consolidar dados meteorológicos coletados em uma
estação local, gerar perfis de altimetria a partir dos percursos de treino
e produzir uma tabela de diferenças entre condições da prova e do histórico
de treinos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional
import statistics


def _filter_by_time_window(timestamp: datetime, start_hour: int, end_hour: int) -> bool:
    """Return True when the timestamp falls inside the hour window.

    The window is inclusive of the start hour and exclusive of the end hour.
    It also supports overnight windows (e.g., 20h→6h).
    """
    workout_time = timestamp.time()
    if start_hour == end_hour:
        return True  # covers full day when hours are equal

    if start_hour < end_hour:
        return start_hour <= workout_time.hour < end_hour
    return workout_time.hour >= start_hour or workout_time.hour < end_hour


@dataclass
class WeatherSample:
    """Single weather measurement collected near o horário de treino."""

    timestamp: datetime
    temperature_c: float
    humidity: float
    heat_index_c: Optional[float] = None
    wind_kmh: Optional[float] = None


@dataclass
class WeatherSummary:
    """Resumo consolidado das condições climáticas observadas."""

    window: str
    mean_temperature_c: float
    max_temperature_c: float
    mean_humidity: float
    max_humidity: float
    mean_heat_index_c: Optional[float]
    max_heat_index_c: Optional[float]
    mean_wind_kmh: Optional[float]
    max_wind_kmh: Optional[float]
    sample_count: int


@dataclass
class AltimetrySession:
    """Dados altimétricos de um percurso de treino."""

    distance_km: float
    total_gain_m: float
    grades: List[float] = field(default_factory=list)
    continuous_climbs_m: List[float] = field(default_factory=list)
    continuous_descents_m: List[float] = field(default_factory=list)
    start_altitude_m: Optional[float] = None


@dataclass
class AltimetryProfile:
    """Perfil agregado das sessões de altimetria de treino."""

    mean_gain_per_10k: float
    mean_total_gain_m: float
    typical_grade_percent: float
    percentile_75_grade_percent: float
    max_grade_percent: float
    mean_continuous_climb_m: Optional[float]
    mean_continuous_descent_m: Optional[float]
    mean_start_altitude_m: Optional[float]
    session_count: int


@dataclass
class EventConditions:
    """Condições previstas para a prova."""

    temperature_c: float
    humidity: float
    wind_kmh: float
    altitude_m: float
    distance_km: float
    elevation_gain_m: float
    max_grade_percent: float


def summarize_weather(
    samples: Iterable[WeatherSample],
    start_hour: int,
    end_hour: int,
) -> WeatherSummary:
    """Consolida estatísticas de clima para um intervalo de horário.

    Args:
        samples: Medições diárias coletadas na estação local.
        start_hour: Hora inicial (0–23) do horário usual de treino.
        end_hour: Hora final (0–23) do horário usual de treino.
    """
    filtered = [s for s in samples if _filter_by_time_window(s.timestamp, start_hour, end_hour)]
    if not filtered:
        raise ValueError("Nenhuma medição encontrada no intervalo informado")

    temperatures = [s.temperature_c for s in filtered]
    humidity = [s.humidity for s in filtered]
    heat_indexes = [s.heat_index_c for s in filtered if s.heat_index_c is not None]
    winds = [s.wind_kmh for s in filtered if s.wind_kmh is not None]

    window_label = f"{start_hour:02d}h–{end_hour:02d}h" if start_hour != end_hour else "24h"

    return WeatherSummary(
        window=window_label,
        mean_temperature_c=statistics.mean(temperatures),
        max_temperature_c=max(temperatures),
        mean_humidity=statistics.mean(humidity),
        max_humidity=max(humidity),
        mean_heat_index_c=statistics.mean(heat_indexes) if heat_indexes else None,
        max_heat_index_c=max(heat_indexes) if heat_indexes else None,
        mean_wind_kmh=statistics.mean(winds) if winds else None,
        max_wind_kmh=max(winds) if winds else None,
        sample_count=len(filtered),
    )


def _percentile(data: List[float], percentile: float) -> float:
    """Calcula percentil usando interpolação simples."""
    if not data:
        raise ValueError("Lista vazia para percentil")
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * percentile
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1


def generate_altimetry_profile(sessions: Iterable[AltimetrySession]) -> AltimetryProfile:
    """Produz estatísticas agregadas de altimetria de treino."""
    session_list = list(sessions)
    if not session_list:
        raise ValueError("Nenhuma sessão fornecida para gerar o perfil altimétrico")

    gains_per_10k = []
    total_gains = []
    grades = []
    climbs = []
    descents = []
    altitudes = []

    for session in session_list:
        if session.distance_km <= 0:
            raise ValueError("Distância deve ser maior que zero para calcular ganho por 10 km")
        gains_per_10k.append((session.total_gain_m / session.distance_km) * 10)
        total_gains.append(session.total_gain_m)
        grades.extend(session.grades)
        climbs.extend(session.continuous_climbs_m)
        descents.extend(session.continuous_descents_m)
        if session.start_altitude_m is not None:
            altitudes.append(session.start_altitude_m)

    typical_grade = statistics.median(grades) if grades else 0.0
    percentile_75 = _percentile(grades, 0.75) if grades else 0.0
    max_grade = max(grades) if grades else 0.0

    mean_climb = statistics.mean(climbs) if climbs else None
    mean_descent = statistics.mean(descents) if descents else None
    mean_altitude = statistics.mean(altitudes) if altitudes else None

    return AltimetryProfile(
        mean_gain_per_10k=statistics.mean(gains_per_10k),
        mean_total_gain_m=statistics.mean(total_gains),
        typical_grade_percent=typical_grade,
        percentile_75_grade_percent=percentile_75,
        max_grade_percent=max_grade,
        mean_continuous_climb_m=mean_climb,
        mean_continuous_descent_m=mean_descent,
        mean_start_altitude_m=mean_altitude,
        session_count=len(session_list),
    )


def build_difference_table(
    event: EventConditions,
    weather_summary: WeatherSummary,
    altimetry_profile: AltimetryProfile,
) -> List[dict]:
    """Monta tabela comparativa de condições da prova versus treinos."""

    def _format(value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        return round(value, 2)

    def _diff(race: Optional[float], training: Optional[float]) -> Optional[float]:
        if race is None or training is None:
            return None
        return round(race - training, 2)

    race_gain_per_10k = (event.elevation_gain_m / event.distance_km) * 10 if event.distance_km else 0.0

    table = [
        {
            "metric": "Temperatura (°C)",
            "treino": _format(weather_summary.mean_temperature_c),
            "prova": _format(event.temperature_c),
            "diferenca": _diff(event.temperature_c, weather_summary.mean_temperature_c),
        },
        {
            "metric": "Umidade (%)",
            "treino": _format(weather_summary.mean_humidity),
            "prova": _format(event.humidity),
            "diferenca": _diff(event.humidity, weather_summary.mean_humidity),
        },
        {
            "metric": "Vento (km/h)",
            "treino": _format(weather_summary.mean_wind_kmh),
            "prova": _format(event.wind_kmh),
            "diferenca": _diff(event.wind_kmh, weather_summary.mean_wind_kmh),
        },
        {
            "metric": "Altitude (m)",
            "treino": _format(altimetry_profile.mean_start_altitude_m),
            "prova": _format(event.altitude_m),
            "diferenca": _diff(event.altitude_m, altimetry_profile.mean_start_altitude_m),
        },
        {
            "metric": "Ganho por 10 km (m)",
            "treino": _format(altimetry_profile.mean_gain_per_10k),
            "prova": _format(race_gain_per_10k),
            "diferenca": _diff(race_gain_per_10k, altimetry_profile.mean_gain_per_10k),
        },
        {
            "metric": "Inclinação máxima (%)",
            "treino": _format(altimetry_profile.max_grade_percent),
            "prova": _format(event.max_grade_percent),
            "diferenca": _diff(event.max_grade_percent, altimetry_profile.max_grade_percent),
        },
    ]

    return table


def format_difference_table(table: List[dict]) -> str:
    """Converte a tabela comparativa em markdown simples."""
    headers = "| Métrica | Treino | Prova | Diferença |"
    divider = "| --- | --- | --- | --- |"
    lines = [headers, divider]
    for row in table:
        treino = "-" if row["treino"] is None else f"{row['treino']:.2f}"
        prova = "-" if row["prova"] is None else f"{row['prova']:.2f}"
        diff = "-" if row["diferenca"] is None else f"{row['diferenca']:.2f}"
        lines.append(f"| {row['metric']} | {treino} | {prova} | {diff} |")
    return "\n".join(lines)
