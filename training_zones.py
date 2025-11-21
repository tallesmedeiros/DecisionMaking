"""
Training Zones Calculator Module
Calculates training paces based on recent race times using:
1. Jack Daniels VDOT tables
2. Critical Velocity formula
"""
from datetime import timedelta
from typing import Dict, Optional, Tuple
import math


class RaceTime:
    """Represents a race time for a specific distance."""

    def __init__(self, distance_km: float, time_seconds: int):
        """
        Initialize a race time.

        Args:
            distance_km: Race distance in kilometers
            time_seconds: Time in seconds
        """
        self.distance_km = distance_km
        self.time_seconds = time_seconds
        self.pace_per_km = time_seconds / distance_km  # seconds per km

    @classmethod
    def from_time_string(cls, distance_km: float, time_str: str) -> 'RaceTime':
        """
        Create RaceTime from a time string (HH:MM:SS or MM:SS).

        Args:
            distance_km: Distance in km
            time_str: Time string in format "HH:MM:SS" or "MM:SS"
        """
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            total_seconds = minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid time format: {time_str}")

        return cls(distance_km, total_seconds)

    def to_pace_string(self) -> str:
        """Convert pace to MM:SS format per km."""
        minutes = int(self.pace_per_km // 60)
        seconds = int(self.pace_per_km % 60)
        return f"{minutes}:{seconds:02d}"

    def __str__(self):
        minutes = int(self.time_seconds // 60)
        seconds = int(self.time_seconds % 60)
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class TrainingZones:
    """Calculates and stores training zone paces."""

    ZONE_NAMES = {
        'easy': 'Easy/Recovery',
        'marathon': 'Marathon Pace',
        'threshold': 'Threshold/Tempo',
        'interval': 'Interval/5K',
        'repetition': 'Repetition/Fast',
    }

    def __init__(self, method: str = 'jack_daniels'):
        """
        Initialize training zones calculator.

        Args:
            method: 'jack_daniels' or 'critical_velocity'
        """
        self.method = method
        self.zones: Dict[str, Tuple[float, float]] = {}  # zone_name -> (min_pace, max_pace) in sec/km
        self.vdot: Optional[float] = None
        self.race_times: Dict[str, RaceTime] = {}

    def add_race_time(self, name: str, race_time: RaceTime):
        """Add a race time to the calculator."""
        self.race_times[name] = race_time

    def calculate_zones(self):
        """Calculate training zones based on race times and selected method."""
        if not self.race_times:
            raise ValueError("No race times provided")

        if self.method == 'jack_daniels':
            self._calculate_jack_daniels_zones()
        elif self.method == 'critical_velocity':
            self._calculate_critical_velocity_zones()
        else:
            raise ValueError(f"Unknown method: {self.method}")

    def _calculate_vdot_from_race(self, distance_km: float, time_seconds: int) -> float:
        """
        Calculate VDOT from a race performance using Jack Daniels' formula.

        VDOT formula: VO2 = -4.60 + 0.182258 * v + 0.000104 * v^2
        where v is velocity in meters/minute

        Adjusted for oxygen cost: VDOT = VO2 / percent_max
        """
        distance_m = distance_km * 1000
        time_min = time_seconds / 60.0
        velocity = distance_m / time_min  # meters per minute

        # Calculate VO2 at this pace
        vo2 = -4.60 + 0.182258 * velocity + 0.000104 * velocity * velocity

        # Calculate percentage of VO2max based on race duration
        # Longer races = lower percentage of VO2max
        percent_max = 0.8 + 0.1894393 * math.exp(-0.012778 * time_min) + 0.2989558 * math.exp(-0.1932605 * time_min)

        # VDOT is the VO2max
        vdot = vo2 / percent_max

        return vdot

    def _velocity_at_vdot(self, vdot: float, percent_vo2max: float) -> float:
        """
        Calculate velocity (m/min) at a given percentage of VO2max.

        Uses iterative solving of the Jack Daniels formula.
        """
        target_vo2 = vdot * percent_vo2max

        # Initial guess based on linear approximation
        velocity = (target_vo2 + 4.60) / 0.182258

        # Iteratively refine (Newton's method)
        for _ in range(10):
            vo2_current = -4.60 + 0.182258 * velocity + 0.000104 * velocity * velocity
            dvo2_dv = 0.182258 + 0.000208 * velocity
            velocity = velocity - (vo2_current - target_vo2) / dvo2_dv

        return velocity

    def _calculate_jack_daniels_zones(self):
        """Calculate training zones using Jack Daniels VDOT method."""
        # Use the best (shortest) race time to calculate VDOT
        best_vdot = 0

        for race_time in self.race_times.values():
            vdot = self._calculate_vdot_from_race(race_time.distance_km, race_time.time_seconds)
            if vdot > best_vdot:
                best_vdot = vdot

        self.vdot = best_vdot

        # Calculate paces for each training zone based on VDOT
        # Percentages of VO2max for each zone
        zone_percentages = {
            'easy': (0.59, 0.74),  # 59-74% of VO2max
            'marathon': (0.75, 0.84),  # 75-84% of VO2max
            'threshold': (0.83, 0.88),  # 83-88% of VO2max
            'interval': (0.95, 1.00),  # 95-100% of VO2max
            'repetition': (1.05, 1.20),  # 105-120% of VO2max (sprint)
        }

        for zone_name, (min_pct, max_pct) in zone_percentages.items():
            # Calculate velocities in m/min
            max_velocity = self._velocity_at_vdot(self.vdot, max_pct)  # Faster pace (higher %)
            min_velocity = self._velocity_at_vdot(self.vdot, min_pct)  # Slower pace (lower %)

            # Convert to seconds per km
            min_pace = 60000 / max_velocity  # Faster actual pace (less seconds)
            max_pace = 60000 / min_velocity  # Slower actual pace (more seconds)

            self.zones[zone_name] = (min_pace, max_pace)

    def _calculate_critical_velocity_zones(self):
        """Calculate training zones using Critical Velocity method."""
        # Need at least 2 race times
        if len(self.race_times) < 2:
            # Fall back to simple percentage-based calculation
            reference_race = list(self.race_times.values())[0]
            reference_pace = reference_race.pace_per_km

            # Simple percentages relative to race pace
            self.zones = {
                'easy': (reference_pace * 1.15, reference_pace * 1.35),
                'marathon': (reference_pace * 1.05, reference_pace * 1.15),
                'threshold': (reference_pace * 0.95, reference_pace * 1.03),
                'interval': (reference_pace * 0.90, reference_pace * 0.95),
                'repetition': (reference_pace * 0.85, reference_pace * 0.90),
            }
            return

        # Use two best times to calculate critical velocity
        race_list = sorted(self.race_times.values(), key=lambda r: r.pace_per_km)

        if len(race_list) >= 2:
            # Take two different distances
            race1 = race_list[0]
            race2 = race_list[-1]

            # Critical Velocity (CV) = (D2 - D1) / (T2 - T1)
            # where D is distance in meters, T is time in seconds
            d1 = race1.distance_km * 1000
            d2 = race2.distance_km * 1000
            t1 = race1.time_seconds
            t2 = race2.time_seconds

            if abs(t2 - t1) > 60:  # Need significant time difference
                cv = (d2 - d1) / (t2 - t1)  # meters per second
                cv_pace = 1000 / cv  # seconds per km

                # Training zones as percentages of CV
                self.zones = {
                    'easy': (cv_pace * 1.25, cv_pace * 1.45),  # Much slower than CV
                    'marathon': (cv_pace * 1.10, cv_pace * 1.25),  # Slower than CV
                    'threshold': (cv_pace * 0.98, cv_pace * 1.05),  # Around CV
                    'interval': (cv_pace * 0.92, cv_pace * 0.98),  # Faster than CV
                    'repetition': (cv_pace * 0.85, cv_pace * 0.92),  # Much faster than CV
                }
            else:
                # Fall back to simple method
                self._calculate_critical_velocity_zones()

    def get_zone_pace(self, zone_name: str, target: str = 'middle') -> float:
        """
        Get pace for a specific zone.

        Args:
            zone_name: Name of the zone
            target: 'min' (fastest), 'max' (slowest), or 'middle'

        Returns:
            Pace in seconds per km
        """
        if zone_name not in self.zones:
            raise ValueError(f"Unknown zone: {zone_name}")

        min_pace, max_pace = self.zones[zone_name]

        if target == 'min':
            return min_pace
        elif target == 'max':
            return max_pace
        else:  # middle
            return (min_pace + max_pace) / 2

    def get_zone_pace_range_str(self, zone_name: str) -> str:
        """Get zone pace as a formatted string range."""
        min_pace, max_pace = self.zones[zone_name]
        return f"{self._pace_to_string(min_pace)} - {self._pace_to_string(max_pace)}"

    def get_zone_pace_str(self, zone_name: str, target: str = 'middle') -> str:
        """Get zone pace as a formatted string."""
        pace = self.get_zone_pace(zone_name, target)
        return self._pace_to_string(pace)

    def _pace_to_string(self, pace_sec_per_km: float) -> str:
        """Convert pace in seconds per km to MM:SS format."""
        minutes = int(pace_sec_per_km // 60)
        seconds = int(pace_sec_per_km % 60)
        return f"{minutes}:{seconds:02d}"

    def get_time_for_distance(self, distance_km: float, pace_sec_per_km: float) -> int:
        """Calculate time in seconds for a given distance and pace."""
        return int(distance_km * pace_sec_per_km)

    def get_time_str(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS or MM:SS format."""
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"

    def __str__(self):
        """String representation of training zones."""
        result = f"\nTraining Zones (Method: {self.method})\n"
        result += "=" * 60 + "\n"

        if self.vdot:
            result += f"VDOT: {self.vdot:.1f}\n\n"

        result += "Recent Race Times:\n"
        for name, race_time in self.race_times.items():
            result += f"  {name}: {race_time.distance_km}km in {race_time} ({race_time.to_pace_string()}/km)\n"

        result += "\nTraining Zones (pace per km):\n"
        for zone_name in ['easy', 'marathon', 'threshold', 'interval', 'repetition']:
            if zone_name in self.zones:
                zone_label = self.ZONE_NAMES.get(zone_name, zone_name)
                pace_range = self.get_zone_pace_range_str(zone_name)
                result += f"  {zone_label:20s}: {pace_range}\n"

        return result
