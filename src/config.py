from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    """
    Configurações globais do sistema usando Pydantic BaseSettings.
    Permite carregar configurações de variáveis de ambiente e/ou arquivo .env
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    # Configurações da API
    API_BASE_URL: str = Field(
        "https://jsonplaceholder.typicode.com",
        description="URL base para requisições à API"
    )
    API_TIMEOUT: int = Field(
        30,
        description="Tempo limite para requisições à API em segundos"
    )
    API_MAX_RETRIES: int = Field(
        3,
        description="Número máximo de tentativas de requisição à API"
    )
    
    # Configurações de Diretórios
    OUTPUT_DIR: str = Field(
        'output',
        description="Diretório para armazenamento dos arquivos gerados"
    )
    
    # Configurações de Email
    EMAIL_ENABLED: bool = Field(
        True,
        description="Habilita/desabilita o envio de notificações por email"
    )
    EMAIL_RECIPIENT: str = Field(
        'relatorios@empresa.com',
        description="Endereço de email padrão para envio dos relatórios"
    )
    
    # Configurações de Logs
    LOG_LEVEL: str = Field(
        'INFO',
        description="Nível de detalhamento dos logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FILE: Optional[str] = Field(
        None,
        description="Caminho do arquivo de log. Se None, logs serão enviados para stdout"
    )
    LOG_ROTATION: str = Field(
        '10 MB',
        description="Tamanho máximo do arquivo de log antes de rotacionar"
    )
    LOG_RETENTION: str = Field(
        '30 days',
        description="Período de retenção dos arquivos de log"
    )

    # Configurações de Cache
    CACHE_ENABLED: bool = Field(
        True,
        description="Habilita/desabilita o cache de respostas da API"
    )
    CACHE_TTL: int = Field(
        3600,
        description="Tempo de vida do cache em segundos (padrão: 1 hora)"
    )

    # Novo campo DEBUG
    DEBUG: bool = Field(
        False,
        description="Habilita/desabilita o modo de depuração"
    )

    def __init__(self, **kwargs):
        """
        Inicializa as configurações e garante que a estrutura de diretórios existe
        
        Args:
            **kwargs: Argumentos nomeados para sobrescrever valores padrão
        """
        super().__init__(**kwargs)
        # Garante que o diretório de saída existe
        Path(self.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Instância global das configurações
settings = Settings()

# Exemplo de uso:
"""
Para usar estas configurações em outros módulos:

from config import settings

# Acessando configurações
api_url = settings.API_BASE_URL
timeout = settings.API_TIMEOUT

# As configurações podem ser sobrescritas por variáveis de ambiente:
# export API_BASE_URL="https://api.outroservico.com"
# export API_TIMEOUT="60"
"""