# cache.py
import json
import redis
from functools import wraps
from typing import Any, Optional, Callable
from datetime import timedelta
import hashlib
from pathlib import Path
import time

from src.utils.logger import setup_logging
from ..config import settings

class RedisCache:
    """
    Classe para gerenciamento de cache utilizando Redis.
    Fornece interface simplificada para operações de cache com serialização JSON.
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 default_ttl: int = 3600):
        """
        Inicializa o cliente Redis com configurações padrão
        
        Args:
            host: Endereço do servidor Redis
            port: Porta de conexão do Redis
            db: Número do banco de dados Redis a ser utilizado
            default_ttl: Tempo padrão de expiração em segundos (1 hora por padrão)
        """
        self.client = redis.Redis(host=host, port=port, db=db, 
                                decode_responses=True)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache
        
        Args:
            key: Chave para busca no cache
            
        Returns:
            Optional[Any]: Valor armazenado ou None se não encontrado/erro
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            setup_logging.warning(f"Erro ao recuperar dados do cache: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazena um valor no cache
        
        Args:
            key: Chave para armazenamento
            value: Valor a ser armazenado (será serializado em JSON)
            ttl: Tempo de expiração em segundos (usa default_ttl se não informado)
            
        Returns:
            bool: True se armazenado com sucesso, False caso contrário
        """
        try:
            ttl = ttl or self.default_ttl
            return self.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
        except Exception as e:
            setup_logging.warning(f"Erro ao armazenar dados no cache: {str(e)}")
            return False

# exceptions.py
class APIError(Exception):
    """Exceção base para erros relacionados à API"""
    def __init__(self, message: str):
        super().__init__(message)

class ProcessingError(Exception):
    """Exceção lançada quando ocorre erro no processamento de dados de usuário"""
    pass

class ReportError(Exception):
    """Exceção lançada quando falha a geração de relatórios"""
    pass

class DataValidationError(ProcessingError):
    """
    Exceção lançada quando falha a validação de dados.
    Armazena os dados inválidos para análise posterior.
    """
    def __init__(self, message: str, invalid_data: dict):
        super().__init__(message)
        self.invalid_data = invalid_data