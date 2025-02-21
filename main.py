import logging
from pathlib import Path
from src.api.client import APIClient
from src.processors.data_processor import DataProcessor
from src.reports.report_generator import ReportGenerator
from src.utils.logger import setup_logging
from src.utils.helpers import sort_users_by_post_count
from src.api.endpoints import USERS_ENDPOINT, POSTS_ENDPOINT
from src.config import settings
from typing import Tuple

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

class UserAnalytics:
    """
    Classe responsável pela análise de dados de usuários.
    Processa dados de usuários e posts, calcula métricas e gera relatórios.
    
    Atributos:
        api_client: Cliente para fazer requisições à API
        data_processor: Processador de dados brutos
        report_generator: Gerador de relatórios em PDF
        users: Lista para armazenar usuários processados
    """
    def __init__(self, api_base_url: str, output_dir: str):
        """
        Inicializa a classe com as configurações necessárias.
        
        Args:
            api_base_url: URL base da API
            output_dir: Diretório para salvar os relatórios gerados
        """
        self.api_client = APIClient(api_base_url)
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator(output_dir)
        self.users = []  # Armazena os usuários após processamento
        
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

def main():
    """
    Configura logs, processa dados e envia relatório por email se configurado.
    """
    setup_logging()
    logger.info("Iniciando aplicação...")
    
    try:
        # Inicializa e executa análise
        analytics = UserAnalytics(
            settings.API_BASE_URL,
            settings.OUTPUT_DIR
        )
        result = analytics.run_analysis()  # Recebe a tupla completa
        pdf_path = result[0]
        excel_path = result[1]
        
        # Extrai nome do relatório do caminho do arquivo
        report_name = Path(pdf_path).stem
        
        # Calcula estatísticas finais
        sorted_users = sort_users_by_post_count(analytics.users)
        user_count = len(sorted_users)
        avg_chars = sum(u.avg_chars for u in sorted_users) / user_count if user_count else 0
        
        logger.info(f"Relatórios gerados com sucesso: PDF={pdf_path}, Excel={excel_path}")
        
        # Envia email se configurado
        if settings.EMAIL_ENABLED:
            logger.info("Tentando enviar relatório por email")
            email_sent = analytics.api_client.send_report_email(
                settings.EMAIL_RECIPIENT,
                pdf_path,
                report_name=report_name,
                user_count=user_count,
                avg_chars=avg_chars
            )
            if email_sent:
                logger.info("Relatório enviado por email com sucesso")
            else:
                logger.warning("Falha no envio do relatório por email")
            
    except Exception as e:
        logger.error(f"Falha crítica na aplicação: {str(e)}")
        raise

if __name__ == "__main__":
    main()