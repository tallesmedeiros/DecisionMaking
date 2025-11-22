"""
Plotting utilities for running plans.
Helper functions for visualization in Jupyter notebooks.
"""
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np


def plot_weekly_volume(plan, figsize=(12, 6)):
    """
    Plot weekly training volume as a bar chart with gradient colors.

    Args:
        plan: RunningPlan object
        figsize: Figure size (width, height)

    Returns:
        matplotlib figure and axis objects
    """
    weeks = list(range(1, plan.weeks + 1))
    volumes = plan.get_weekly_volumes()

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Color gradient from cool (low volume) to warm (high volume)
    # Normalize volumes to 0-1 range for color mapping
    max_volume = max(volumes) if volumes else 1
    normalized_volumes = [v / max_volume for v in volumes]

    # Create color gradient: blue (cool) -> yellow -> orange -> red (hot)
    colors = []
    for norm_vol in normalized_volumes:
        if norm_vol < 0.33:
            # Blue to light blue
            r = 0.3 + (norm_vol / 0.33) * 0.2
            g = 0.6 + (norm_vol / 0.33) * 0.3
            b = 0.9
        elif norm_vol < 0.67:
            # Light blue to yellow
            progress = (norm_vol - 0.33) / 0.34
            r = 0.5 + progress * 0.5
            g = 0.9
            b = 0.9 - progress * 0.6
        else:
            # Yellow to orange/red
            progress = (norm_vol - 0.67) / 0.33
            r = 1.0
            g = 0.9 - progress * 0.45
            b = 0.3 - progress * 0.3

        colors.append((r, g, b))

    # Plot bars
    bars = ax.bar(weeks, volumes, color=colors, edgecolor='black', linewidth=0.5, alpha=0.8)

    # Add value labels on bars
    for bar, volume in zip(bars, volumes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{volume:.0f}km',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Styling
    ax.set_xlabel('Semana', fontsize=12, fontweight='bold')
    ax.set_ylabel('Volume (km)', fontsize=12, fontweight='bold')
    ax.set_title(f'📊 Volume Semanal - {plan.name}', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Set x-axis ticks
    ax.set_xticks(weeks)
    ax.set_xticklabels([f'S{w}' for w in weeks])

    # Add average line
    avg_volume = np.mean(volumes)
    ax.axhline(y=avg_volume, color='gray', linestyle='--', linewidth=2, alpha=0.5, label=f'Média: {avg_volume:.1f}km')
    ax.legend(loc='upper left')

    plt.tight_layout()
    return fig, ax


def plot_zone_distribution_stacked(plan, figsize=(14, 7)):
    """
    Plot weekly volume with zone distribution as stacked bar chart.

    Args:
        plan: RunningPlan object
        figsize: Figure size (width, height)

    Returns:
        matplotlib figure and axis objects
    """
    weeks = list(range(1, plan.weeks + 1))
    zone_distributions = plan.get_zone_distributions()

    # Zone colors (matching emojis: cool to hot)
    zone_colors = {
        'easy': '#90EE90',       # Light green (🟢)
        'marathon': '#4169E1',   # Royal blue (🔵)
        'threshold': '#FFD700',  # Gold (🟡)
        'interval': '#FF8C00',   # Dark orange (🟠)
        'repetition': '#DC143C'  # Crimson red (🔴)
    }

    zone_labels = {
        'easy': '🟢 Easy',
        'marathon': '🔵 Marathon',
        'threshold': '🟡 Threshold',
        'interval': '🟠 Interval',
        'repetition': '🔴 Repetition'
    }

    # Prepare data for stacked bars
    zones_data = {zone: [] for zone in zone_colors.keys()}

    for dist in zone_distributions:
        for zone in zones_data.keys():
            zones_data[zone].append(dist.get(zone, 0))

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Plot stacked bars
    bottom = np.zeros(len(weeks))
    for zone in ['easy', 'marathon', 'threshold', 'interval', 'repetition']:
        values = zones_data[zone]
        ax.bar(weeks, values, bottom=bottom,
               label=zone_labels[zone],
               color=zone_colors[zone],
               edgecolor='black',
               linewidth=0.5,
               alpha=0.85)
        bottom += np.array(values)

    # Add total volume labels on top
    totals = [sum(dist.values()) for dist in zone_distributions]
    for week, total in zip(weeks, totals):
        ax.text(week, total, f'{total:.0f}km',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Styling
    ax.set_xlabel('Semana', fontsize=12, fontweight='bold')
    ax.set_ylabel('Volume (km)', fontsize=12, fontweight='bold')
    ax.set_title(f'📊 Distribuição de Zonas por Semana - {plan.name}', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.legend(loc='upper left', framealpha=0.9)

    # Set x-axis ticks
    ax.set_xticks(weeks)
    ax.set_xticklabels([f'S{w}' for w in weeks])

    plt.tight_layout()
    return fig, ax


def print_zone_summary(plan):
    """
    Print a text summary of zone distribution across the entire plan.

    Args:
        plan: RunningPlan object
    """
    zone_distributions = plan.get_zone_distributions()

    # Calculate totals
    total_km = sum(sum(dist.values()) for dist in zone_distributions)
    zone_totals = {
        'easy': 0,
        'marathon': 0,
        'threshold': 0,
        'interval': 0,
        'repetition': 0
    }

    for dist in zone_distributions:
        for zone, km in dist.items():
            if zone in zone_totals:
                zone_totals[zone] += km

    # Print summary
    print("\n" + "="*60)
    print("📊 RESUMO DE DISTRIBUIÇÃO DE ZONAS - PLANO COMPLETO")
    print("="*60)
    print(f"\n📏 Volume Total: {total_km:.1f}km\n")

    zone_info = {
        'easy': ('🟢', 'Easy/Recovery'),
        'marathon': ('🔵', 'Marathon Pace'),
        'threshold': ('🟡', 'Threshold/Tempo'),
        'interval': ('🟠', 'Interval/5K'),
        'repetition': ('🔴', 'Repetition/Fast')
    }

    for zone, km in zone_totals.items():
        if km > 0:
            percentage = (km / total_km) * 100
            emoji, name = zone_info[zone]
            print(f"{emoji} {name:20s}: {km:6.1f}km ({percentage:5.1f}%)")

    print("="*60 + "\n")
