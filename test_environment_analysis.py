from datetime import datetime

import pytest

from environment_analysis import (
    AltimetryProfile,
    AltimetrySession,
    EventConditions,
    WeatherSample,
    build_difference_table,
    format_difference_table,
    generate_altimetry_profile,
    summarize_weather,
)


def test_summarize_weather_filters_by_window():
    samples = [
        WeatherSample(datetime(2024, 5, 1, 6), 18.0, 80, 20.0, 5.0),
        WeatherSample(datetime(2024, 5, 1, 19), 26.0, 60, 27.0, 12.0),
        WeatherSample(datetime(2024, 5, 2, 6, 30), 19.0, 78, 21.0, 4.0),
    ]

    summary = summarize_weather(samples, 5, 8)

    assert summary.window == "05h–08h"
    assert summary.sample_count == 2
    assert summary.mean_temperature_c == pytest.approx(18.5)
    assert summary.max_temperature_c == 19.0
    assert summary.mean_humidity == pytest.approx(79.0)
    assert summary.max_humidity == 80
    assert summary.mean_heat_index_c == pytest.approx(20.5)
    assert summary.max_heat_index_c == 21.0
    assert summary.mean_wind_kmh == pytest.approx(4.5)
    assert summary.max_wind_kmh == 5.0


def test_generate_altimetry_profile_calculates_grades_and_gain():
    sessions = [
        AltimetrySession(
            distance_km=12,
            total_gain_m=240,
            grades=[2.0, 4.0, 6.0],
            continuous_climbs_m=[800, 1200],
            continuous_descents_m=[700, 1000],
            start_altitude_m=600,
        ),
        AltimetrySession(
            distance_km=10,
            total_gain_m=150,
            grades=[1.0, 5.0],
            continuous_climbs_m=[500],
            continuous_descents_m=[400],
            start_altitude_m=650,
        ),
    ]

    profile = generate_altimetry_profile(sessions)

    assert profile.mean_gain_per_10k == pytest.approx(((240 / 12) * 10 + (150 / 10) * 10) / 2)
    assert profile.mean_total_gain_m == pytest.approx((240 + 150) / 2)
    assert profile.typical_grade_percent == pytest.approx(4.0)
    assert profile.percentile_75_grade_percent == pytest.approx(5.0)
    assert profile.max_grade_percent == 6.0
    assert profile.mean_continuous_climb_m == pytest.approx((800 + 1200 + 500) / 3)
    assert profile.mean_continuous_descent_m == pytest.approx((700 + 1000 + 400) / 3)
    assert profile.mean_start_altitude_m == pytest.approx((600 + 650) / 2)
    assert profile.session_count == 2


def test_build_and_format_difference_table():
    weather_summary = summarize_weather(
        [
            WeatherSample(datetime(2024, 6, 1, 6), 20.0, 75, 22.0, 5.0),
            WeatherSample(datetime(2024, 6, 2, 6), 21.0, 70, 23.0, 6.0),
        ],
        5,
        8,
    )

    altimetry_profile = generate_altimetry_profile(
        [
            AltimetrySession(10, 200, grades=[2.0, 4.0, 8.0], continuous_climbs_m=[600], continuous_descents_m=[550], start_altitude_m=500),
        ]
    )

    event = EventConditions(
        temperature_c=28.0,
        humidity=65,
        wind_kmh=10.0,
        altitude_m=50.0,
        distance_km=21.1,
        elevation_gain_m=320.0,
        max_grade_percent=10.0,
    )

    table = build_difference_table(event, weather_summary, altimetry_profile)

    expected_metrics = {
        "Temperatura (°C)": event.temperature_c - weather_summary.mean_temperature_c,
        "Umidade (%)": event.humidity - weather_summary.mean_humidity,
        "Vento (km/h)": event.wind_kmh - weather_summary.mean_wind_kmh,
        "Altitude (m)": event.altitude_m - altimetry_profile.mean_start_altitude_m,
        "Ganho por 10 km (m)": (event.elevation_gain_m / event.distance_km) * 10 - altimetry_profile.mean_gain_per_10k,
        "Inclinação máxima (%)": event.max_grade_percent - altimetry_profile.max_grade_percent,
    }

    for row in table:
        assert row["metric"] in expected_metrics
        assert row["diferenca"] == pytest.approx(round(expected_metrics[row["metric"]], 2))

    markdown = format_difference_table(table)
    assert "| Métrica | Treino | Prova | Diferença |" in markdown
    assert "Temperatura" in markdown
