"""
Módulo para exportação de planos de treino em PDF.
Suporta inclusão de zonas de treino, plano completo e gráficos.
"""

import os
import tempfile
from typing import Optional
from datetime import datetime

# Tentar importar bibliotecas de PDF
PDF_LIBS_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_LIBS_AVAILABLE = True
except ImportError:
    print("⚠️  reportlab não instalado. Instale com: pip install reportlab")

# Para gráficos
PLOT_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend sem display
    import matplotlib.pyplot as plt
    from plot_utils import plot_weekly_volume, plot_zone_distribution_stacked
    PLOT_AVAILABLE = True
except ImportError:
    print("⚠️  matplotlib não disponível para gráficos")


def export_plan_to_pdf(plan, filename: Optional[str] = None, include_graphs: bool = True):
    """
    Exporta um plano de treino completo para PDF.

    Args:
        plan: Objeto RunningPlan
        filename: Nome do arquivo PDF (se None, usa o nome do plano)
        include_graphs: Se True, inclui gráficos de volume e distribuição

    Returns:
        str: Caminho do arquivo PDF gerado
    """
    if not PDF_LIBS_AVAILABLE:
        print("❌ Não é possível gerar PDF sem reportlab instalado.")
        print("   Instale com: pip install reportlab")
        return None

    # Definir nome do arquivo
    if filename is None:
        # Sanitizar nome do plano para usar como nome de arquivo
        filename = plan.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"{filename}.pdf"

    if not filename.endswith('.pdf'):
        filename += '.pdf'

    # Criar documento
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)

    # Container para elementos do PDF
    elements = []

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Estilo para texto normal
    normal_style = styles['Normal']

    # ===================
    # CABEÇALHO DO PLANO
    # ===================
    elements.append(Paragraph(f"🏃 {plan.name}", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Informações do plano em tabela
    info_data = [
        ['Meta:', plan.goal],
        ['Nível:', plan.level.capitalize()],
        ['Duração:', f'{plan.weeks} semanas'],
        ['Dias de treino:', f'{plan.days_per_week} dias/semana'],
        ['Início:', plan.start_date.strftime('%d/%m/%Y') if plan.start_date else 'Não definido'],
        ['Prova:', plan.get_race_date().strftime('%d/%m/%Y') if plan.start_date else 'Não definido'],
    ]

    # Calcular volume total
    total_km = sum(w.total_distance_km for w in plan.schedule)
    info_data.append(['Volume total:', f'{total_km:.1f} km'])

    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))

    # ===================
    # ZONAS DE TREINO
    # ===================
    if hasattr(plan, 'training_zones') and plan.training_zones:
        elements.append(Paragraph("📊 Zonas de Treinamento", subtitle_style))

        zones = plan.training_zones
        if hasattr(zones, 'vdot') and zones.vdot:
            elements.append(Paragraph(f"<b>VDOT:</b> {zones.vdot:.1f}", normal_style))
            elements.append(Spacer(1, 0.1*inch))

        # Tabela de zonas
        zone_data = [['Zona', 'Pace/km', '% FCMax', 'Uso']]

        zone_info = {
            'easy': ('Easy/Recovery', '65-75%', 'Regeneração, base aeróbica'),
            'marathon': ('Marathon Pace', '75-84%', 'Resistência aeróbica'),
            'threshold': ('Threshold/Tempo', '84-88%', 'Limiar anaeróbico'),
            'interval': ('Interval/5K', '95-98%', 'VO2max'),
            'repetition': ('Repetition/Fast', '98-100%', 'Velocidade máxima')
        }

        for zone_name in ['easy', 'marathon', 'threshold', 'interval', 'repetition']:
            if zone_name in zones.zones:
                name, hr, uso = zone_info[zone_name]
                pace_range = zones.get_zone_pace_range_str(zone_name)
                zone_data.append([name, pace_range, hr, uso])

        zone_table = Table(zone_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 2.5*inch])
        zone_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            # Bordas e grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(zone_table)
        elements.append(Spacer(1, 0.3*inch))

    # ===================
    # GRÁFICOS
    # ===================
    if include_graphs and PLOT_AVAILABLE:
        elements.append(Paragraph("📈 Visualizações", subtitle_style))

        # Criar diretório temporário para gráficos
        temp_dir = tempfile.mkdtemp()

        try:
            # Gráfico de volume semanal
            vol_img_path = os.path.join(temp_dir, 'weekly_volume.png')
            fig, ax = plot_weekly_volume(plan, figsize=(7, 3.5))
            plt.savefig(vol_img_path, dpi=150, bbox_inches='tight')
            plt.close(fig)

            elements.append(Image(vol_img_path, width=6*inch, height=3*inch))
            elements.append(Spacer(1, 0.2*inch))

            # Gráfico de distribuição de zonas
            if hasattr(plan, 'training_zones') and plan.training_zones:
                dist_img_path = os.path.join(temp_dir, 'zone_distribution.png')
                fig, ax = plot_zone_distribution_stacked(plan, figsize=(7, 3.5))
                plt.savefig(dist_img_path, dpi=150, bbox_inches='tight')
                plt.close(fig)

                elements.append(Image(dist_img_path, width=6*inch, height=3*inch))
                elements.append(Spacer(1, 0.2*inch))

        except Exception as e:
            print(f"⚠️  Erro ao gerar gráficos: {e}")

        elements.append(PageBreak())

    # ===================
    # PLANO SEMANA A SEMANA
    # ===================
    elements.append(Paragraph("📅 Plano Detalhado Semana a Semana", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))

    for week in plan.schedule:
        # Título da semana
        week_title = f"Semana {week.week_number} - {week.total_distance_km:.1f} km"

        # Calcular data de início da semana se plano tem start_date
        if plan.start_date:
            from datetime import timedelta
            week_start = plan.start_date + timedelta(weeks=week.week_number - 1)
            week_title += f" ({week_start.strftime('%d/%m')})"

        elements.append(Paragraph(week_title, ParagraphStyle(
            'WeekTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#4a90e2'),
            spaceBefore=12,
            spaceAfter=6
        )))

        # Notas da semana
        if week.notes:
            elements.append(Paragraph(f"<i>{week.notes}</i>", normal_style))
            elements.append(Spacer(1, 0.1*inch))

        # Tabela de treinos
        workout_data = [['Dia', 'Treino', 'Distância', 'Detalhes']]

        for workout in week.workouts:
            dia = workout.day
            tipo = workout.type
            distancia = f"{workout.distance_km:.1f} km" if workout.distance_km else "-"

            # Detalhes
            detalhes = []
            if workout.target_pace:
                detalhes.append(f"Pace: {workout.target_pace}")
            if workout.total_time_estimated:
                detalhes.append(f"Tempo: {workout.total_time_estimated}")
            if workout.description:
                detalhes.append(workout.description)

            detalhes_str = ", ".join(detalhes) if detalhes else "-"

            workout_data.append([dia, tipo, distancia, detalhes_str])

        workout_table = Table(workout_data, colWidths=[0.9*inch, 1.5*inch, 0.9*inch, 3*inch])
        workout_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f4f8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(workout_table)
        elements.append(Spacer(1, 0.15*inch))

        # Page break a cada 3 semanas para melhor layout
        if week.week_number % 3 == 0 and week.week_number < plan.weeks:
            elements.append(PageBreak())

    # ===================
    # RODAPÉ
    # ===================
    elements.append(PageBreak())
    elements.append(Paragraph("💡 Dicas Importantes", subtitle_style))

    tips = [
        "Consistência é a chave: É melhor treinar regularmente do que fazer treinos intensos esporadicamente",
        "Escute seu corpo: Descanse se sentir dor ou fadiga excessiva",
        "Hidratação: Beba água antes, durante e depois dos treinos",
        "Nutrição: Alimente-se adequadamente para suportar o treino",
        "Recuperação: Os dias de descanso são quando seu corpo fica mais forte",
        "Aquecimento: Sempre faça aquecimento antes de treinos intensos",
        "Alongamento: Alongue após os treinos para prevenir lesões",
        "Confie no plano: Especialmente durante o taper - resista à tentação de fazer mais"
    ]

    for tip in tips:
        elements.append(Paragraph(f"• {tip}", normal_style))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        f"<i>Plano gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>",
        ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    # Construir PDF
    try:
        doc.build(elements)
        print(f"✅ PDF gerado com sucesso: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_plan_simple_pdf(plan, filename: Optional[str] = None):
    """
    Exporta versão simplificada do plano (sem gráficos).

    Args:
        plan: Objeto RunningPlan
        filename: Nome do arquivo PDF

    Returns:
        str: Caminho do arquivo gerado
    """
    return export_plan_to_pdf(plan, filename, include_graphs=False)


# Função auxiliar para notebooks
def save_plan_as_pdf(plan, filename: Optional[str] = None, include_graphs: bool = True):
    """
    Função amigável para notebooks Jupyter.
    Salva o plano como PDF e mostra mensagem de sucesso.

    Args:
        plan: Objeto RunningPlan
        filename: Nome do arquivo (opcional)
        include_graphs: Se True, inclui gráficos

    Returns:
        str: Caminho do arquivo gerado ou None se falhar
    """
    print("📄 Gerando PDF...")
    print("=" * 60)

    result = export_plan_to_pdf(plan, filename, include_graphs)

    if result:
        print("=" * 60)
        print(f"✅ PDF salvo com sucesso!")
        print(f"📁 Arquivo: {result}")
        print(f"📊 O PDF inclui:")
        print("   • Informações do plano")
        if hasattr(plan, 'training_zones') and plan.training_zones:
            print("   • Tabela de zonas de treino")
        if include_graphs and PLOT_AVAILABLE:
            print("   • Gráficos de volume e distribuição")
        print("   • Plano detalhado semana a semana")
        print("   • Dicas de treino")
        print("\n💡 Você pode fazer download deste arquivo e imprimir!")

    return result
