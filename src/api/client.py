import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List
from ..utils.exceptions import APIError
from ..api.endpoints import USERS_ENDPOINT, POSTS_ENDPOINT
import time
import json
from datetime import datetime
from src.models.schemas import UserSchema, PostSchema
from pydantic import ValidationError
from ..config import settings

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        """
        Inicializa o cliente API com configurações básicas
        
        Args:
            base_url (str): URL base para todas as requisições da API
        """
        self.base_url = base_url
        self.page_size = 100  # Tamanho padrão da página para paginação
        self.max_pages = 10   # Número máximo de páginas a serem buscadas
        self.timeout = settings.API_TIMEOUT  # Tempo limite para requisições
        self.max_retries = settings.API_MAX_RETRIES  # Número máximo de tentativas
        self.session = requests.Session()
        
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Executa uma requisição GET com retry automático
        
        Args:
            endpoint (str): Endpoint da API
            params (Dict): Parâmetros opcionais da requisição
            
        Returns:
            Dict: Dados da resposta em formato JSON
            
        Raises:
            APIError: Quando todas as tentativas de requisição falham
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                duration = time.time() - start_time
                
                response.raise_for_status()
                self._log_performance_metrics(endpoint, duration)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Falha ao acessar {endpoint}: {str(e)}")
                    raise APIError(f"Falha ao obter dados de {endpoint}: {str(e)}")
                logger.warning(f"Tentando novamente a requisição para {endpoint} (tentativa {attempt + 1})")
                time.sleep(2 ** attempt)  # Backoff exponencial

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict:
        """
        Executa uma requisição POST
        
        Args:
            endpoint (str): Endpoint da API
            data (Dict): Dados a serem enviados no corpo da requisição
            
        Returns:
            Dict: Resposta da API em formato JSON
            
        Raises:
            APIError: Quando a requisição falha
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            logger.info(f"Iniciando requisição POST para {url}")
            
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Falha na requisição da API: {str(e)}")
            raise APIError(f"Falha ao enviar dados para {endpoint}: {str(e)}")

    def send_report_email(self, recipient: str, report_path: str, report_name: str, user_count: int, avg_chars: float) -> bool:
        """
        Simula o envio de email com relatório de análise
        
        Args:
            recipient (str): Email do destinatário
            report_path (str): Caminho do arquivo do relatório
            report_name (str): Nome do relatório
            user_count (int): Total de usuários analisados
            avg_chars (float): Média de caracteres por post
            
        Returns:
            bool: True se o envio foi simulado com sucesso, False caso contrário
        """
        try:
            endpoint = "send-email"
            payload = {
                "to": recipient,
                "subject": f"Relatório de Análise de Posts - {report_name}",
                "body": (
                    f"Relatório gerado em: {report_path}\n"
                    f"Total de usuários analisados: {user_count}\n"
                    f"Média geral de caracteres por post: {avg_chars:.2f}"
                )
            }
            
            logger.info(f"Iniciando envio simulado de email para: {recipient}")
            logger.debug(f"Detalhes do email simulado: {payload}")
            
            # Simulação de delay no envio
            logger.debug("Simulando processamento do envio...")
            time.sleep(0.5)
            
            # Simula resposta bem sucedida
            response = {"status": "success", "message": "Email enviado com sucesso"}
            
            logger.info(f"Email simulado enviado para: {recipient}")
            logger.debug(f"Resposta simulada: {response}")
            logger.info(f"Relatório anexado: {report_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Falha na simulação de envio de email: {str(e)}")
            logger.exception("Detalhes da exceção:")
            return False

    def _log_performance_metrics(self, endpoint: str, duration: float):
        """
        Registra métricas de performance das requisições
        
        Args:
            endpoint (str): Endpoint acessado
            duration (float): Duração da requisição em segundos
        """
        metrics = {
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        with open('api_performance.log', 'a') as f:
            f.write(f"{json.dumps(metrics)}\n")

    def _validate_response(self, endpoint: str, data: list):
        """
        Valida os dados recebidos da API usando schemas
        
        Args:
            endpoint (str): Endpoint que retornou os dados
            data (list): Lista de dados a serem validados
            
        Raises:
            ValidationError: Quando os dados não correspondem ao schema esperado
        """
        try:
            if endpoint == USERS_ENDPOINT:
                [UserSchema(**item) for item in data]
            elif endpoint == POSTS_ENDPOINT:
                [PostSchema(**item) for item in data]
        except ValidationError as e:
            logger.error(f"Falha na validação do schema para {endpoint}: {str(e)}")
            raise ValidationError(f"Formato de dados inválido de {endpoint}") from e

    def get_paginated(self, endpoint: str, params: dict = None) -> List[dict]:
        """
        Obtém todos os resultados paginados automaticamente
        
        Args:
            endpoint (str): Endpoint da API
            params (dict): Parâmetros adicionais da requisição
            
        Returns:
            List[dict]: Lista completa de resultados de todas as páginas
        """
        results = []
        page = 1
        
        while page <= self.max_pages:
            params = params or {}
            params.update({
                '_page': page,
                '_limit': self.page_size
            })
            
            try:
                response = self.get(endpoint, params=params)
                if not response:
                    break
                    
                results.extend(response)
                
                # Verifica se chegou na última página
                if len(response) < self.page_size:
                    break
                    
                page += 1
                
            except APIError as e:
                logger.error(f"Paginação interrompida na página {page}: {str(e)}")
                break
                
        return results

    def get_users(self) -> List[Dict]:
        """
        Obtém lista completa de usuários
        
        Returns:
            List[Dict]: Lista de usuários
        """
        return self._make_request('GET', USERS_ENDPOINT)
    
    def get_user_posts(self, user_id: int) -> List[Dict]:
        """
        Obtém todos os posts de um usuário específico
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            List[Dict]: Lista de posts do usuário
        """
        return self._make_request('GET', f'users/{user_id}/posts')
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Realiza requisição HTTP com retry automático e métricas
        
        Args:
            method (str): Método HTTP (GET, POST, etc)
            endpoint (str): Endpoint da API
            **kwargs: Argumentos adicionais para a requisição
            
        Returns:
            Any: Resposta da API em formato JSON
            
        Raises:
            APIError: Quando todas as tentativas falham
        """
        retries = 0
        while retries < self.max_retries:
            try:
                response = self.session.request(
                    method,
                    f"{self.base_url}/{endpoint}",
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                retries += 1
                logger.warning(f"Tentativa {retries}/{self.max_retries} falhou")
        raise APIError(f"Falha após {self.max_retries} tentativas")