from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    Table, TableStyle, PageBreak, PageTemplate, Frame, NextPageTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
import io
from typing import List, Tuple
from pathlib import Path

from src.api.endpoints import POSTS_ENDPOINT, USERS_ENDPOINT
from src.processors.data_processor import DataProcessor
from src.utils.helpers import sort_users_by_post_count
from ..models.user import User
from ..utils.logger import setup_logging
import pandas as pd
import numpy as np
from ..api.client import APIClient

logger = logging.getLogger(__name__)

class UserAnalytics:
    def __init__(self, api_base_url: str, output_dir: str):
        """Inicializa o analisador de dados de usuários
        Args:
            api_base_url: URL base da API para consumo
            output_dir: Diretório de saída para relatórios
        """
        self.api_client = APIClient(api_base_url)
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator(output_dir)
        
        def run_analysis(self) -> Tuple[str, str]:
            """
            Executa a análise completa dos dados de usuários.
            
            Returns:
                Tuple[str, str]: Caminhos dos arquivos PDF e Excel gerados
                
            Raises:
                Exception: Se houver falha durante o processo de análise
            """
            try:
                # Busca dados paginados da API
                logger.info("Iniciando coleta de dados da API")
                users_data = self.api_client.get_paginated(USERS_ENDPOINT)
                posts_data = self.api_client.get_paginated(POSTS_ENDPOINT)
                
                # Processa os dados coletados
                logger.info("Processando dados de usuários e posts")
                self.users = self.data_processor.process_users(users_data)
                posts = self.data_processor.process_posts(posts_data)
                
                # Calcula métricas para cada usuário
                logger.info("Calculando métricas individuais dos usuários")
                for user in self.users:
                    self.data_processor.calculate_metrics(user, posts)
                
                # Ordena usuários por contagem de posts
                logger.info("Ordenando usuários por quantidade de posts")
                sorted_users = sort_users_by_post_count(self.users)
                
                # Gera relatórios PDF e Excel
                logger.info("Gerando relatórios PDF e Excel")
                pdf_path = self.report_generator.generate_pdf_report(
                    sorted_users, 
                    "user_analytics_report"
                )
                excel_path = self.report_generator.generate_excel_report(
                    sorted_users, 
                    "user_analytics_report"
                )
                
                return pdf_path, excel_path
                
            except Exception as e:
                logger.error(f"Falha durante a análise: {str(e)}")
                raise

class NumberedCanvas(canvas.Canvas):
    """
    Classe que estende o Canvas do ReportLab para adicionar numeração automática às páginas.
    Permite personalizar a apresentação e o formato dos números de página.
    """
    def __init__(self, *args, **kwargs):
        """
        Inicializa o canvas numerado
        Args:
            *args: Argumentos posicionais para o canvas pai
            **kwargs: Argumentos nomeados para o canvas pai
        """
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []  # Armazena estados das páginas para numeração posterior

    def showPage(self):
        """
        Sobrescreve o método showPage para salvar o estado da página atual
        antes de iniciar uma nova página
        """
        # Salva o estado atual da página para processamento posterior
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Sobrescreve o método save para adicionar números de página antes de
        salvar definitivamente o documento
        """
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            # Adiciona numeração a todas as páginas, exceto a capa (página 1)
            if self._pageNumber > 1:
                self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """
        Desenha o número da página no rodapé
        Args:
            page_count: Número total de páginas no documento
        """
        self.setFont("Helvetica", 9)
        self.drawRightString(
            self._pagesize[0] - 0.5 * inch,
            0.5 * inch,
            f"Página {self._pageNumber} de {page_count}"
        )

class ReportGenerator:
    """
    Classe responsável pela geração de relatórios em diferentes formatos (PDF e Excel).
    Implementa funcionalidades para criar relatórios profissionais com elementos visuais,
    gráficos e formatação personalizada.
    """
    def __init__(self, output_dir: str):
        """
        Configura o gerador de relatórios
        Args:
            output_dir: Diretório para armazenar os arquivos gerados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.brand_green = HexColor('#16a34a')  # Verde corporativo padrão
        self.brand_blue = HexColor('#1f213b')   # Azul corporativo padrão
        
        # Inicialização dos estilos base
        self.styles = getSampleStyleSheet()
        self._define_custom_styles()
        
    def _define_custom_styles(self):
        """
        Define estilos tipográficos personalizados para o relatório PDF.
        Configura fontes, cores e espaçamentos para diferentes elementos do documento.
        """
        # Estilo para o título principal do documento
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.white,
            spaceAfter=20,
            alignment=1  # Centralizado
        )
        
        # Estilo para títulos de seções do relatório
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.brand_blue,
            spaceBefore=30,  # Espaço antes do título
            spaceAfter=15,   # Espaço após o título
            alignment=0      # Alinhado à esquerda
        )

        # Estilo para o sumário (tabela de conteúdo)
        self.toc_style = TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (0,-1), 30),  # Recuo para hierarquia
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])

    def _draw_cover_page(self, canvas_obj, doc):
        """
        Cria a página de capa do relatório com elementos visuais corporativos
        Args:
            canvas_obj: Objeto canvas do ReportLab para desenho
            doc: Documento PDF atual
        """
        width, height = A4
        
        # Aplica cor de fundo corporativa
        canvas_obj.setFillColor(self.brand_green)
        canvas_obj.rect(0, 0, width, height, fill=1)
        
        # Insere e centraliza o logotipo
        logo_path = Path("assets/logo_caplink.png")
        if logo_path.exists():
            canvas_obj.drawImage(
                str(logo_path),
                x=(width - 368)/2,  # Centralização horizontal
                y=height - 6*inch,   # Posicionamento vertical fixo
                width=368,
                height=368,
                preserveAspectRatio=True
            )
        
        # Adiciona título do relatório
        title_y = height/2 - 1.8*inch  # Ajuste vertical do título
        canvas_obj.setFillColor("#1f213b")
        canvas_obj.setFont("Helvetica-Bold", 18)
        canvas_obj.drawCentredString(width/2, title_y, "Relatório de Automação Robótica de Processos")

    def _create_data_table(self, users: List[User]) -> Table:
        """
        Gera uma tabela formatada com os dados dos usuários
        Args:
            users: Lista de objetos User para exibição no relatório
        Returns:
            Table: Objeto Table do ReportLab pronto para inserção no PDF
        """
        # Define cabeçalhos e prepara dados da tabela
        headers = ['ID', 'Nome', 'Posts', 'Média Caracteres']
        data = [headers]
        
        # Preenche as linhas com dados dos usuários
        for user in users:
            data.append([
                str(user.id),
                user.name,
                str(user.post_count),
                f"{user.avg_chars:.2f}" if user.avg_chars else '0.00'
            ])
        
        # Aplica estilização à tabela
        return Table(data, style=[
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),  # Fundo cinza no cabeçalho
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),       # Texto preto
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),                # Alinhamento à esquerda
            ('GRID', (0,0), (-1,-1), 1, colors.black)         # Grade preta
        ])

    def _create_charts_section(self, users: List[User]):
        """
        Gera visualizações gráficas dos dados dos usuários
        Args:
            users: Lista de usuários para geração dos gráficos
        Returns:
            List: Lista de elementos Image do ReportLab contendo os gráficos gerados
        """
        charts = []
        
        # Gráfico 1: Gráfico de barras mostrando total de posts por usuário
        plt.figure(figsize=(10, 5))
        user_names = [user.name for user in users]
        post_counts = [user.post_count for user in users]
        
        # Personaliza as barras do gráfico
        bars = plt.bar(user_names, post_counts)
        plt.xticks(rotation=30, ha='right')
        plt.title('Total de Posts por Usuário')
        
        # Aplica cor corporativa às barras
        for bar in bars:
            bar.set_color(f"#{self.brand_green.hexval()[2:]}")
        
        # Converte gráfico para imagem PNG
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=450, bbox_inches='tight')
        plt.close()
        
        # Adiciona primeiro gráfico ao relatório
        charts.append(Image(img_buffer, width=450, height=220))
        charts.append(Spacer(1, 0.2*inch))  # Espaçamento entre gráficos

        # Gráfico 2: Média de caracteres por post para cada usuário
        plt.figure(figsize=(10, 5))
        avg_chars = [user.avg_chars for user in users]
        plt.bar(user_names, avg_chars, color=f"#{self.brand_blue.hexval()[2:]}")
        plt.xticks(rotation=30, ha='right')
        plt.title('Média de Caracteres por Usuário')
        
        # Gera segunda imagem
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=450, bbox_inches='tight')
        plt.close()
        
        # Adiciona segundo gráfico ao relatório
        charts.append(Image(img_buffer, width=450, height=220))
        return charts

    def generate_excel_report(self, users: List[User], filename: str) -> str:
        """
        Gera relatório detalhado em formato Excel
        Args:
            users: Lista de usuários processados
            filename: Nome base do arquivo (sem extensão)
        Returns:
            str: Caminho completo do arquivo Excel gerado
        """
        try:
            output_path = self.output_dir / f"{filename}.xlsx"
            
            # Prepara dados para formato tabular
            data = [{
                'ID': user.id,
                'Nome': user.name,
                'Posts': user.post_count,
                'Média Caracteres': f"{user.avg_chars:.2f}" if user.avg_chars else '0.00'
            } for user in users]
            
            # Cria DataFrame e configura layout
            df = pd.DataFrame(data)
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados Detalhados')
                
                # Ajusta largura das colunas automaticamente
                worksheet = writer.sheets['Dados Detalhados']
                for column in worksheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            logger.info(f"Relatório Excel gerado com sucesso: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Falha ao gerar relatório Excel: {str(e)}")
            raise
    
    def generate_reports(self, users: List[User], filename: str) -> Tuple[str, str]:
        """
        Coordena a geração dos relatórios em PDF e Excel
        Args:
            users: Lista de usuários processados
            filename: Nome base para os arquivos de saída
        Returns:
            Tuple[str, str]: Caminhos dos relatórios PDF e Excel gerados
        """
        try:
            # Gera os relatórios sequencialmente
            pdf_path = self.generate_pdf_report(users, filename)
            excel_path = self.generate_excel_report(users, filename)
            
            logger.info(f"Relatórios gerados com sucesso: PDF={pdf_path}, Excel={excel_path}")
            return pdf_path, excel_path
            
        except Exception as e:
            logger.error(f"Falha na geração dos relatórios: {str(e)}")
            raise
    def generate_pdf_report(self, users: List[User], filename: str) -> str:
        """
        Gera relatório PDF completo com elementos visuais e formatação profissional
        Args:
            users: Lista de usuários para incluir no relatório
            filename: Nome base do arquivo (sem extensão)
        Returns:
            str: Caminho completo do arquivo PDF gerado
        Raises:
            ValueError: Se a lista de usuários estiver vazia
        """
        # Validação inicial dos dados
        if not users:
            logger.error("Lista de usuários vazia - não há dados para gerar relatório")
            raise ValueError("Dados insuficientes para geração do relatório")
        
        # Garante que o diretório de saída existe
        if not self.output_dir.exists():
            logger.info(f"Criando diretório de saída: {self.output_dir}")
            self.output_dir.mkdir(parents=True)
        
        try:
            pdf_path = self.output_dir / f"{filename}.pdf"
            
            # Configura documento base
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            elements = []  # Lista para armazenar elementos do PDF
            
            # Define template da capa
            cover_template = PageTemplate(
                id='cover',
                frames=[Frame(
                    doc.leftMargin,
                    doc.bottomMargin,
                    doc.width,
                    doc.height,
                    id='normal'
                )],
                onPage=self._draw_cover_page
            )
            
            # Define template para páginas de conteúdo
            content_template = PageTemplate(
                id='content',
                frames=[Frame(
                    doc.leftMargin,
                    doc.bottomMargin,
                    doc.width,
                    doc.height,
                    id='normal'
                )],
            )
            
            # Adiciona templates ao documento
            doc.addPageTemplates([cover_template, content_template])
            
            # Configura transição para páginas de conteúdo
            elements.append(NextPageTemplate('content'))
            elements.append(PageBreak())
            
            # Define estilo do título principal
            # Define estilo personalizado para o título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Centralizado
            )
            elements.append(Paragraph('Relatório de Atividades', title_style))
            
            # Adiciona data de geração do relatório
            date_style = ParagraphStyle(
                'CustomDate',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=colors.gray,
                alignment=1,
                spaceAfter=30
            )
            elements.append(Paragraph(f'Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', date_style))
            
            # Seção 1: Visão Geral
            elements.append(Paragraph('1. Visão Geral', self.section_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Texto explicativo do relatório
            overview_text = """
            Este relatório documenta a execução do Test Case: Automação Robótica de Processos. 
            O objetivo é avaliar a capacidade de consumir APIs, manipular e processar dados, 
            resolver problemas e documentar o fluxo de trabalho. Utilizando a API fictícia 
            JSONPlaceholder, foram realizadas requisições para obter usuários e seus posts, 
            calculando a média de caracteres dos textos.
            """
            
            # Estilo para texto justificado
            justified_style = ParagraphStyle(
                'Justified',
                parent=self.styles['Normal'],
                alignment=4  # Justificado
            )
            
            elements.append(Paragraph(overview_text, justified_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Seção 2: Tabela de Dados dos Usuários
            elements.append(Paragraph('2. Dados dos Usuários', self.section_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Prepara dados para a tabela
            headers = ['ID', 'Nome', 'Posts', 'Média Caracteres']
            data = [headers]
            
            for user in users:
                data.append([
                    str(user.id),
                    user.name,
                    str(user.post_count),
                    f"{user.avg_chars:.2f}" if user.avg_chars else '0.00'
                ])
            
            # Cria e estiliza a tabela
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f213b')),  # Cabeçalho azul corporativo
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),                 # Texto branco no cabeçalho
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),                         # Alinhamento à esquerda
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),             # Fonte negrito no cabeçalho
                ('FONTSIZE', (0,0), (-1,0), 10),                          # Tamanho da fonte do cabeçalho
                ('BOTTOMPADDING', (0,0), (-1,0), 12),                     # Espaçamento inferior
                ('BACKGROUND', (0,1), (-1,-1), colors.white),             # Fundo branco para dados
                ('GRID', (0,0), (-1,-1), 1, colors.black),               # Grade preta
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),               # Fonte normal para dados
                ('FONTSIZE', (0,1), (-1,-1), 10),                        # Tamanho da fonte dos dados
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Seção 3: Gráficos e Análise Visual
            elements.append(Paragraph('3. Análise Visual', self.section_style))
            elements.append(Spacer(1, 0.2*inch))
            elements.extend(self._create_charts_section(users))
            
            # Gera o documento final com numeração de páginas
            doc.build(elements, canvasmaker=NumberedCanvas)
            
            logger.info(f"Relatório PDF gerado com sucesso: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Erro crítico na geração do PDF: {str(e)}")
            raise
