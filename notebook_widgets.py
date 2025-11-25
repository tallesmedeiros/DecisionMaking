"""
Widgets interativos para notebooks Jupyter.
Fornece interface visual amigável para entrada de dados do usuário.
"""

try:
    import ipywidgets as widgets
    from IPython.display import display, clear_output, HTML
    WIDGETS_AVAILABLE = True
except ImportError:
    WIDGETS_AVAILABLE = False
    print("⚠️ ipywidgets não está instalado. Execute: pip install ipywidgets")

from datetime import datetime, date, timedelta
from user_profile import UserProfile, RaceGoal
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator


class PlanCreatorWidgets:
    """Classe para gerenciar widgets de criação de plano de treino."""

    def __init__(self):
        """Inicializa os widgets."""
        if not WIDGETS_AVAILABLE:
            raise ImportError("ipywidgets não está disponível")

        self.profile = UserProfile(name="", age=30, weight_kg=70, height_cm=175)
        self.plan = None

        # Widgets para informações pessoais
        self.nome_widget = widgets.Text(
            value='João Silva',
            description='Nome:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.idade_widget = widgets.IntSlider(
            value=30,
            min=15,
            max=80,
            step=1,
            description='Idade:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.peso_widget = widgets.FloatSlider(
            value=70.0,
            min=40.0,
            max=150.0,
            step=0.5,
            description='Peso (kg):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.altura_widget = widgets.IntSlider(
            value=175,
            min=140,
            max=220,
            step=1,
            description='Altura (cm):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.sexo_widget = widgets.Dropdown(
            options=[('Masculino', 'M'), ('Feminino', 'F'), ('Não especificar', '')],
            value='M',
            description='Sexo:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.fc_repouso_widget = widgets.BoundedIntText(
            value=0,
            min=0,
            max=120,
            description='FC repouso:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px'),
            placeholder='Opcional'
        )

        self.fc_max_widget = widgets.BoundedIntText(
            value=0,
            min=0,
            max=240,
            description='FC máxima:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px'),
            placeholder='Opcional'
        )

        # Widgets para experiência
        self.anos_correndo_widget = widgets.FloatSlider(
            value=2.0,
            min=0.0,
            max=30.0,
            step=0.5,
            description='Anos correndo:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.km_semanal_widget = widgets.FloatSlider(
            value=30.0,
            min=0.0,
            max=150.0,
            step=5.0,
            description='Km semanal atual:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.volume_medio_widget = widgets.FloatSlider(
            value=30.0,
            min=0.0,
            max=200.0,
            step=5.0,
            description='Volume médio (km):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.pico_recente_widget = widgets.FloatSlider(
            value=40.0,
            min=0.0,
            max=250.0,
            step=5.0,
            description='Pico recente (km):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.dias_mantidos_widget = widgets.IntSlider(
            value=4,
            min=1,
            max=7,
            step=1,
            description='Dias mantidos/sem:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.nivel_widget = widgets.Dropdown(
            options=[('Iniciante', 'beginner'), ('Intermediário', 'intermediate'), ('Avançado', 'advanced')],
            value='intermediate',
            description='Nível:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.treinos_tolerados_widget = widgets.SelectMultiple(
            options=UserProfile.TOLERATED_WORKOUT_OPTIONS,
            value=['Corridas fáceis/rodagens', 'Longões progressivos'],
            description='Treinos tolerados:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px', height='120px')
        )

        self.aderencia_widget = widgets.IntSlider(
            value=80,
            min=0,
            max=100,
            step=5,
            description='Aderência (%):',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        # Widgets para objetivo
        self.distancia_widget = widgets.Dropdown(
            options=['5K', '10K', 'Half Marathon', 'Marathon'],
            value='10K',
            description='Distância:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        # Data da prova (60 dias a partir de hoje por padrão)
        data_padrao = (date.today() + timedelta(days=60)).strftime('%Y-%m-%d')
        self.data_prova_widget = widgets.DatePicker(
            value=datetime.strptime(data_padrao, '%Y-%m-%d').date(),
            description='Data da prova:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.nome_prova_widget = widgets.Text(
            value='Corrida da Cidade',
            description='Nome da prova:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.local_prova_widget = widgets.Text(
            value='São Paulo',
            description='Local:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.tempo_meta_widget = widgets.Text(
            value='',
            placeholder='Ex: 45:00 ou 1:45:30',
            description='Tempo meta:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        # Widgets para disponibilidade
        self.dias_semana_widget = widgets.IntSlider(
            value=4,
            min=3,
            max=6,
            step=1,
            description='Dias/semana:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.horas_dia_widget = widgets.FloatSlider(
            value=1.0,
            min=0.5,
            max=3.0,
            step=0.25,
            description='Horas/dia:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.horario_widget = widgets.Dropdown(
            options=[('Manhã', 'morning'), ('Tarde', 'afternoon'), ('Noite', 'evening')],
            value='morning',
            description='Horário preferido:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        # Widgets para zonas de treino
        self.tempo_5k_widget = widgets.Text(
            value='',
            placeholder='Ex: 22:30',
            description='Tempo 5K:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.tempo_10k_widget = widgets.Text(
            value='',
            placeholder='Ex: 47:15',
            description='Tempo 10K:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.tempo_21k_widget = widgets.Text(
            value='',
            placeholder='Ex: 1:45:30',
            description='Tempo Meia:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.tempo_42k_widget = widgets.Text(
            value='',
            placeholder='Ex: 3:45:00',
            description='Tempo Maratona:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.prova_recente_dist_widget = widgets.Dropdown(
            options=[('5K', '5K'), ('10K', '10K'), ('15K', '15K'), ('Meia (21K)', '21K'), ('Maratona (42K)', '42K')],
            value='10K',
            description='Prova recente:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.prova_recente_tempo_widget = widgets.Text(
            value='',
            placeholder='MM:SS ou HH:MM:SS',
            description='Tempo recente:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        self.vdot_info_widget = widgets.HTML(
            value="<i>Preencha distância e tempo recente para estimar VDOT (Jack Daniels).</i>"
        )

        self.metodo_zonas_widget = widgets.Dropdown(
            options=[('Jack Daniels (recomendado)', 'jack_daniels'), ('Velocidade Crítica', 'critical_velocity')],
            value='jack_daniels',
            description='Método de cálculo:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )

        # Widget para lesões
        self.lesoes_atuais_widget = widgets.SelectMultiple(
            options=UserProfile.COMMON_INJURIES,
            value=[],
            description='Lesões atuais:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px', height='120px')
        )

        self.lesoes_previas_widget = widgets.SelectMultiple(
            options=UserProfile.COMMON_INJURIES,
            value=[],
            description='Lesões prévias:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px', height='120px')
        )

        # Output widget para mostrar resultados
        self.output = widgets.Output()

    def show_personal_info(self):
        """Mostra widgets para informações pessoais."""
        display(HTML("<h3>👤 Informações Pessoais</h3>"))
        display(self.nome_widget)
        display(self.idade_widget)
        display(self.peso_widget)
        display(self.altura_widget)
        display(self.sexo_widget)
        display(HTML("<p><i>Use FC de repouso/máxima para validar fadiga (opcional).</i></p>"))
        display(self.fc_repouso_widget)
        display(self.fc_max_widget)

    def show_experience(self):
        """Mostra widgets para experiência em corrida."""
        display(HTML("<h3>🏃 Experiência em Corrida</h3>"))
        display(self.anos_correndo_widget)
        display(self.km_semanal_widget)
        display(self.volume_medio_widget)
        display(self.pico_recente_widget)
        display(self.dias_mantidos_widget)
        display(self.nivel_widget)
        display(self.treinos_tolerados_widget)
        display(self.aderencia_widget)

    def show_goal(self):
        """Mostra widgets para objetivo de prova."""
        display(HTML("<h3>🎯 Objetivo da Prova</h3>"))
        display(self.distancia_widget)
        display(self.data_prova_widget)
        display(self.nome_prova_widget)
        display(self.local_prova_widget)
        display(self.tempo_meta_widget)

    def show_availability(self):
        """Mostra widgets para disponibilidade de tempo."""
        display(HTML("<h3>📅 Disponibilidade</h3>"))
        display(self.dias_semana_widget)
        display(self.horas_dia_widget)
        display(self.horario_widget)

    def show_training_zones(self):
        """Mostra widgets para zonas de treino."""
        display(HTML("<h3>📊 Tempos Recentes de Prova</h3>"))
        display(HTML("<p><i>Preencha os tempos que você tiver. Deixe em branco os que não tiver.</i></p>"))
        display(self.tempo_5k_widget)
        display(self.tempo_10k_widget)
        display(self.tempo_21k_widget)
        display(self.tempo_42k_widget)
        display(HTML("<p><b>Prova mais recente (para estimar VDOT):</b></p>"))
        display(self.prova_recente_dist_widget)
        display(self.prova_recente_tempo_widget)
        display(self.vdot_info_widget)
        display(self.metodo_zonas_widget)

    def show_injuries(self):
        """Mostra widgets para histórico de lesões."""
        display(HTML("<h3>🩹 Histórico de Lesões</h3>"))
        display(HTML("<p><i>Segure Ctrl (ou Cmd no Mac) para selecionar múltiplas opções</i></p>"))
        display(self.lesoes_atuais_widget)
        display(self.lesoes_previas_widget)

    def create_profile(self):
        """Cria o perfil do usuário baseado nos widgets."""
        # Informações pessoais
        self.profile = UserProfile(
            name=self.nome_widget.value,
            age=self.idade_widget.value,
            weight_kg=self.peso_widget.value,
            height_cm=self.altura_widget.value,
            gender=self.sexo_widget.value
        )

        # Frequência cardíaca (opcional)
        self.profile.hr_resting = self.fc_repouso_widget.value or None
        self.profile.hr_max = self.fc_max_widget.value or None

        # Experiência
        self.profile.years_running = self.anos_correndo_widget.value
        self.profile.current_weekly_km = self.km_semanal_widget.value
        self.profile.average_weekly_km = self.volume_medio_widget.value
        self.profile.recent_peak_weekly_km = self.pico_recente_widget.value
        self.profile.consistent_days_per_week = self.dias_mantidos_widget.value
        self.profile.tolerated_workouts = list(self.treinos_tolerados_widget.value)
        self.profile.adherence_score = float(self.aderencia_widget.value)
        self.profile.experience_level = self.nivel_widget.value

        # Objetivo
        self.profile.main_race = RaceGoal(
            distance=self.distancia_widget.value,
            date=self.data_prova_widget.value,
            name=self.nome_prova_widget.value,
            location=self.local_prova_widget.value,
            is_main_goal=True,
            target_time=self.tempo_meta_widget.value if self.tempo_meta_widget.value else None
        )

        # Disponibilidade
        self.profile.days_per_week = self.dias_semana_widget.value
        self.profile.hours_per_day = self.horas_dia_widget.value
        self.profile.preferred_time = self.horario_widget.value

        # Tempos de prova
        if self.tempo_5k_widget.value:
            self.profile.recent_race_times["5K"] = self.tempo_5k_widget.value
        if self.tempo_10k_widget.value:
            self.profile.recent_race_times["10K"] = self.tempo_10k_widget.value
        if self.tempo_21k_widget.value:
            self.profile.recent_race_times["21K"] = self.tempo_21k_widget.value
        if self.tempo_42k_widget.value:
            self.profile.recent_race_times["42K"] = self.tempo_42k_widget.value

        # Prova recente para estimativa de VDOT
        self._estimate_vdot_from_recent_race()

        self.profile.zones_calculation_method = self.metodo_zonas_widget.value

        # Lesões
        self.profile.current_injuries = list(self.lesoes_atuais_widget.value)
        self.profile.previous_injuries = list(self.lesoes_previas_widget.value)

        # Atualizar timestamp
        self.profile.last_updated = datetime.now()

        return self.profile

    def _estimate_vdot_from_recent_race(self):
        """Calcula VDOT a partir da prova recente informada."""
        recent_time = self.prova_recente_tempo_widget.value.strip()
        if not recent_time:
            self.profile.vdot_estimate = None
            self.vdot_info_widget.value = "<i>Preencha distância e tempo recente para estimar VDOT (Jack Daniels).</i>"
            return

        distance_map = {
            "5K": 5.0,
            "10K": 10.0,
            "15K": 15.0,
            "21K": 21.0975,
            "42K": 42.195,
        }

        distance_label = self.prova_recente_dist_widget.value
        distance_km = distance_map.get(distance_label)

        if not distance_km:
            self.profile.vdot_estimate = None
            self.vdot_info_widget.value = "<b style='color:red'>Distância inválida para cálculo de VDOT.</b>"
            return

        try:
            race_time = RaceTime.from_time_string(distance_km, recent_time)
        except ValueError:
            self.profile.vdot_estimate = None
            self.vdot_info_widget.value = "<b style='color:red'>Formato de tempo inválido. Use MM:SS ou HH:MM:SS.</b>"
            return

        zones = TrainingZones(method='jack_daniels')
        zones.add_race_time("Prova Recente", race_time)
        zones.calculate_zones()

        self.profile.vdot_estimate = zones.vdot
        self.profile.recent_race_times[distance_label] = recent_time
        self.vdot_info_widget.value = f"<b>VDOT estimado:</b> {zones.vdot:.1f} (Jack Daniels)"

    def generate_plan(self):
        """Gera o plano de treino baseado no perfil."""
        # Criar perfil
        profile = self.create_profile()

        # Gerar plano
        self.plan = PlanGenerator.generate_plan(
            name=f"Plano {profile.main_race.distance} - {profile.name}",
            goal=profile.main_race.distance,
            level=profile.experience_level,
            weeks=None,  # Calculado automaticamente
            days_per_week=profile.days_per_week,
            training_zones=None,  # Calculado do perfil
            user_profile=profile
        )

        # Definir data de início (próxima segunda-feira)
        hoje = date.today()
        dias_ate_segunda = (7 - hoje.weekday()) % 7
        if dias_ate_segunda == 0:
            dias_ate_segunda = 7
        proxima_segunda = hoje + timedelta(days=dias_ate_segunda)
        self.plan.set_start_date(datetime.combine(proxima_segunda, datetime.min.time()))

        return self.plan

    def show_all_simple(self):
        """Mostra todos os widgets em modo simples (para criação rápida de plano básico)."""
        display(HTML("<h2>🏃‍♂️ Criador de Plano de Treino - Modo Simples</h2>"))
        display(HTML("<hr>"))

        self.show_personal_info()
        display(HTML("<hr>"))

        self.show_goal()
        display(HTML("<hr>"))

        self.show_availability()
        display(HTML("<hr>"))

        # Botão para gerar plano
        botao_gerar = widgets.Button(
            description='🚀 Gerar Plano de Treino',
            button_style='success',
            layout=widgets.Layout(width='400px', height='50px')
        )

        def on_gerar_click(b):
            with self.output:
                clear_output()
                print("⏳ Gerando plano...")
                try:
                    plan = self.generate_plan()
                    print("\n✅ Plano gerado com sucesso!\n")
                    plan.print_visual()
                except Exception as e:
                    print(f"❌ Erro ao gerar plano: {e}")

        botao_gerar.on_click(on_gerar_click)

        display(botao_gerar)
        display(self.output)

    def show_all_complete(self):
        """Mostra todos os widgets em modo completo (personalização total)."""
        display(HTML("<h2>🏃‍♂️ Criador de Plano de Treino - Modo Completo</h2>"))
        display(HTML("<p><i>Preencha todas as seções para criar um plano totalmente personalizado</i></p>"))
        display(HTML("<hr>"))

        self.show_personal_info()
        display(HTML("<hr>"))

        self.show_experience()
        display(HTML("<hr>"))

        self.show_goal()
        display(HTML("<hr>"))

        self.show_availability()
        display(HTML("<hr>"))

        self.show_training_zones()
        display(HTML("<hr>"))

        self.show_injuries()
        display(HTML("<hr>"))

        # Botão para gerar plano
        botao_gerar = widgets.Button(
            description='🚀 Gerar Plano Personalizado',
            button_style='success',
            layout=widgets.Layout(width='400px', height='50px')
        )

        def on_gerar_click(b):
            with self.output:
                clear_output()
                print("⏳ Gerando plano personalizado...")
                try:
                    plan = self.generate_plan()
                    print("\n✅ Plano gerado com sucesso!\n")
                    print(f"📋 Nome: {plan.name}")
                    print(f"🎯 Meta: {plan.goal}")
                    print(f"📅 Início: {plan.start_date.strftime('%d/%m/%Y')}")
                    print(f"🏁 Prova: {plan.get_race_date().strftime('%d/%m/%Y')}")
                    print(f"⏱️  Duração: {plan.weeks} semanas")
                    print(f"📊 Dias/semana: {plan.days_per_week}")
                    print("\n" + "="*70 + "\n")
                    plan.print_visual()
                except Exception as e:
                    print(f"❌ Erro ao gerar plano: {e}")
                    import traceback
                    traceback.print_exc()

        botao_gerar.on_click(on_gerar_click)

        display(botao_gerar)
        display(self.output)


def create_simple_plan_widgets():
    """Cria widgets simples para criação rápida de plano."""
    if not WIDGETS_AVAILABLE:
        print("❌ ipywidgets não está disponível. Instale com: pip install ipywidgets")
        return None

    widgets_obj = PlanCreatorWidgets()
    widgets_obj.show_all_simple()
    return widgets_obj


def create_complete_plan_widgets():
    """Cria widgets completos para personalização total."""
    if not WIDGETS_AVAILABLE:
        print("❌ ipywidgets não está disponível. Instale com: pip install ipywidgets")
        return None

    widgets_obj = PlanCreatorWidgets()
    widgets_obj.show_all_complete()
    return widgets_obj
