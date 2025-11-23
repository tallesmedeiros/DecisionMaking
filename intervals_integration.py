"""
Integração com Intervals.icu para upload de planos de treino.

Este módulo permite enviar automaticamente os treinos gerados para sua conta
no Intervals.icu, facilitando o acompanhamento e execução do plano.

Configuração:
-----------
Crie um arquivo 'intervals_config.json' com suas credenciais:

{
    "api_key": "sua_chave_api_aqui",
    "athlete_id": "seu_athlete_id_aqui"
}

Para obter suas credenciais:
1. Acesse https://intervals.icu/
2. Vá em Settings → Developer → API Key
3. Copie sua API Key (formato: athlete_12345:xxxxxxxxxxxxxxxx)
4. O athlete_id é a primeira parte antes dos dois pontos

Uso:
----
from intervals_integration import IntervalsUploader
from running_plan import RunningPlan

# Carregar plano
plan = RunningPlan.load_from_file("meu_plano.json")

# Upload para Intervals.icu
uploader = IntervalsUploader()
success = uploader.upload_plan(plan)
"""

import json
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from running_plan import RunningPlan, Week, Workout, WorkoutSegment


class IntervalsConfig:
    """Gerencia configurações de autenticação do Intervals.icu."""

    def __init__(self, config_file: str = "intervals_config.json"):
        """
        Inicializa configuração.

        Args:
            config_file: Caminho para arquivo JSON com credenciais
        """
        self.config_file = config_file
        self.api_key: Optional[str] = None
        self.athlete_id: Optional[str] = None
        self._load_config()

    def _load_config(self) -> None:
        """Carrega configurações do arquivo JSON."""
        config_path = Path(self.config_file)

        if not config_path.exists():
            print(f"⚠️  Arquivo de configuração '{self.config_file}' não encontrado.")
            print(f"\n📝 Crie o arquivo com o seguinte formato:\n")
            print(json.dumps({
                "api_key": "athlete_12345:xxxxxxxxxxxxxxxx",
                "athlete_id": "12345"
            }, indent=2))
            print(f"\n💡 Para obter suas credenciais:")
            print(f"   1. Acesse https://intervals.icu/")
            print(f"   2. Settings → Developer → API Key")
            print(f"   3. Copie a API Key completa")
            print(f"   4. O athlete_id é o número após 'athlete_'")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                self.athlete_id = config.get('athlete_id')

                if not self.api_key or not self.athlete_id:
                    print("❌ Configuração incompleta. Verifique api_key e athlete_id.")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler configuração: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    def is_configured(self) -> bool:
        """Verifica se as credenciais estão configuradas."""
        return bool(self.api_key and self.athlete_id)


class IntervalsUploader:
    """Faz upload de planos de treino para Intervals.icu."""

    BASE_URL = "https://intervals.icu/api/v1/athlete"

    def __init__(self, config_file: str = "intervals_config.json"):
        """
        Inicializa uploader.

        Args:
            config_file: Caminho para arquivo de configuração
        """
        self.config = IntervalsConfig(config_file)

    def _encode_auth(self) -> str:
        """
        Codifica credenciais para autenticação Basic.

        Returns:
            Token base64 para header Authorization
        """
        token = f"API_KEY:{self.config.api_key}".encode("utf-8")
        return base64.b64encode(token).decode("utf-8")

    def _get_headers(self) -> Dict[str, str]:
        """
        Prepara headers HTTP para requisições.

        Returns:
            Dicionário com headers de autenticação
        """
        return {
            "Authorization": f"Basic {self._encode_auth()}",
            "Content-Type": "application/json"
        }

    def _map_workout_type_to_intervals(self, workout_type: str) -> str:
        """
        Mapeia tipos de treino do sistema para tipos do Intervals.icu.

        Args:
            workout_type: Tipo interno (Easy Run, Tempo Run, etc)

        Returns:
            Tipo compatível com Intervals.icu
        """
        type_mapping = {
            "Easy Run": "Run",
            "Tempo Run": "Run",
            "Interval Training": "Run",
            "Fartlek": "Run",
            "Long Run": "Run",
            "Rest": "Rest"
        }
        return type_mapping.get(workout_type, "Run")

    def _get_workout_zone(self, segment: WorkoutSegment) -> str:
        """
        Extrai zona de treino do segmento.

        Args:
            segment: Segmento do treino

        Returns:
            Zona no formato Intervals.icu (Z1, Z2, etc)
        """
        # Tentar extrair zona do nome ou descrição
        name_lower = segment.name.lower()

        # Mapeamento de termos para zonas
        zone_keywords = {
            "z1": "Z1",
            "z2": "Z2",
            "z3": "Z3",
            "z4": "Z4",
            "z5": "Z5",
            "easy": "Z1",
            "recovery": "Z1",
            "moderate": "Z2",
            "tempo": "Z3",
            "threshold": "Z3",
            "interval": "Z4",
            "vo2max": "Z5",
            "sprint": "Z5"
        }

        for keyword, zone in zone_keywords.items():
            if keyword in name_lower:
                return zone

        # Default para Easy/Z1 se não identificar
        return "Z1"

    def _convert_segment_to_step(self, segment: WorkoutSegment) -> Dict[str, Any]:
        """
        Converte segmento de treino para formato step do Intervals.icu.

        Args:
            segment: Segmento do treino

        Returns:
            Dicionário com dados do step
        """
        # Duração em minutos
        duration_minutes = int(segment.duration_minutes)

        # Zona de treino
        zone = self._get_workout_zone(segment)

        # Montar step
        step = {
            "duration": f"{duration_minutes}m",
            "zone": zone,
            "description": segment.description or segment.name
        }

        # Adicionar pace se disponível
        if segment.pace:
            step["pace"] = segment.pace

        # Adicionar distância se disponível
        if segment.distance_km and segment.distance_km > 0:
            # Converter km para metros
            distance_meters = int(segment.distance_km * 1000)
            step["distance"] = f"{distance_meters}m"

        return step

    def _convert_workout_to_event(self, workout: Workout, date: datetime) -> Dict[str, Any]:
        """
        Converte treino para formato de evento do Intervals.icu.

        Args:
            workout: Treino a converter
            date: Data do treino

        Returns:
            Dicionário com dados do evento
        """
        # Data no formato ISO
        start_date_local = date.strftime("%Y-%m-%dT00:00:00")

        # Nome e descrição
        name = f"{workout.type}"
        description = workout.description or ""

        # Tipo para Intervals.icu
        intervals_type = self._map_workout_type_to_intervals(workout.type)

        # Tempo total em segundos
        moving_time = int(workout.duration_minutes * 60) if workout.duration_minutes else 0

        # Converter segmentos para steps
        steps = []
        if workout.segments:
            for segment in workout.segments:
                step = self._convert_segment_to_step(segment)
                steps.append(step)

        # Montar evento
        event = {
            "start_date_local": start_date_local,
            "category": "WORKOUT",
            "name": name,
            "description": description,
            "type": intervals_type,
        }

        # Adicionar tempo se disponível
        if moving_time > 0:
            event["moving_time"] = moving_time

        # Adicionar steps se houver estrutura detalhada
        if steps:
            event["steps"] = steps

        return event

    def _convert_plan_to_events(self, plan: RunningPlan) -> List[Dict[str, Any]]:
        """
        Converte plano completo para lista de eventos.

        Args:
            plan: Plano de treino

        Returns:
            Lista de eventos no formato Intervals.icu
        """
        events = []

        if not plan.start_date:
            print("⚠️  Plano não tem data de início definida.")
            print("   Use: plan.set_start_date(datetime(2025, 1, 6))")
            return events

        # Iterar por semanas e treinos
        for week in plan.schedule:
            # Calcular data de início da semana
            week_start = plan.start_date + timedelta(weeks=week.week_number - 1)

            # Mapeamento de dias da semana para offset
            day_offset = {
                "Mon": 0, "Seg": 0,
                "Tue": 1, "Ter": 1,
                "Wed": 2, "Qua": 2,
                "Thu": 3, "Qui": 3,
                "Fri": 4, "Sex": 4,
                "Sat": 5, "Sáb": 5, "Sab": 5,
                "Sun": 6, "Dom": 6
            }

            for workout in week.workouts:
                # Calcular data específica do treino
                day_name = workout.day.strip()
                offset = day_offset.get(day_name, 0)
                workout_date = week_start + timedelta(days=offset)

                # Pular dias de descanso opcionalmente
                if workout.type == "Rest":
                    # Você pode escolher incluir ou não os dias de descanso
                    # Para incluir, comente a linha abaixo
                    continue

                # Converter e adicionar evento
                event = self._convert_workout_to_event(workout, workout_date)
                events.append(event)

        return events

    def upload_plan(self, plan: RunningPlan, include_rest_days: bool = False) -> bool:
        """
        Faz upload do plano para Intervals.icu.

        Args:
            plan: Plano de treino a enviar
            include_rest_days: Se True, inclui dias de descanso

        Returns:
            True se sucesso, False caso contrário
        """
        # Verificar configuração
        if not self.config.is_configured():
            print("❌ Configuração do Intervals.icu não encontrada ou incompleta.")
            return False

        print(f"\n🚀 Preparando upload do plano '{plan.name}' para Intervals.icu...")

        # Converter plano para eventos
        events = self._convert_plan_to_events(plan)

        if not events:
            print("❌ Nenhum evento para enviar.")
            return False

        print(f"📋 Total de treinos a enviar: {len(events)}")

        # Preparar requisição
        url = f"{self.BASE_URL}/{self.config.athlete_id}/events/bulk"
        headers = self._get_headers()

        try:
            # Fazer upload
            print(f"\n⏳ Enviando treinos...")
            response = requests.post(url, headers=headers, json=events, timeout=30)

            # Verificar resposta
            if response.status_code in [200, 201]:
                print(f"✅ Upload concluído com sucesso!")
                print(f"🎉 {len(events)} treinos adicionados ao seu calendário Intervals.icu")
                print(f"\n🔗 Acesse: https://intervals.icu/athletes/{self.config.athlete_id}/calendar")
                return True
            else:
                print(f"❌ Erro no upload: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print("❌ Timeout na requisição. Tente novamente.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Testa conexão com Intervals.icu.

        Returns:
            True se conseguiu conectar, False caso contrário
        """
        if not self.config.is_configured():
            print("❌ Configuração não encontrada.")
            return False

        print("🔍 Testando conexão com Intervals.icu...")

        try:
            # Tentar buscar dados do atleta
            url = f"{self.BASE_URL}/{self.config.athlete_id}"
            headers = self._get_headers()

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                athlete_name = data.get('name', 'Atleta')
                print(f"✅ Conexão OK! Bem-vindo, {athlete_name}!")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Verifique suas credenciais no arquivo '{self.config.config_file}'")
                return False

        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False


def create_config_file(api_key: str, athlete_id: str,
                       config_file: str = "intervals_config.json") -> None:
    """
    Cria arquivo de configuração com credenciais.

    Args:
        api_key: API Key completa do Intervals.icu
        athlete_id: ID do atleta
        config_file: Nome do arquivo de configuração

    Exemplo:
        create_config_file("athlete_12345:abc123xyz", "12345")
    """
    config = {
        "api_key": api_key,
        "athlete_id": athlete_id
    }

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Arquivo '{config_file}' criado com sucesso!")
    print(f"\n⚠️  IMPORTANTE: Mantenha este arquivo privado!")
    print(f"   Adicione '{config_file}' ao seu .gitignore")


if __name__ == "__main__":
    # Exemplo de uso
    print("🏃‍♂️ Intervals.icu Integration - Teste")
    print("=" * 60)

    # Testar configuração
    uploader = IntervalsUploader()

    if uploader.config.is_configured():
        uploader.test_connection()
    else:
        print("\n💡 Para começar, crie o arquivo de configuração:")
        print("   from intervals_integration import create_config_file")
        print('   create_config_file("athlete_12345:suachave", "12345")')
