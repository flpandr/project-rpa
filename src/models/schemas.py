from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class PostSchema(BaseModel):
    """
    Schema de validação para posts
    
    Attributes:
        id (int): Identificador único do post
        userId (int): Identificador do usuário (mantido como userId para compatibilidade com API)
        title (str): Título do post
        body (str): Conteúdo do post
    """
    id: int
    userId: int = Field(..., alias='userId')
    title: str
    body: str

    class Config:
        """Configurações do modelo Pydantic"""
        allow_population_by_field_name = True

class UserSchema(BaseModel):
    """
    Schema de validação para usuários
    
    Attributes:
        id (int): Identificador único do usuário
        name (str): Nome completo do usuário
        username (str): Nome de usuário
        email (str): Endereço de email (deve conter @)
        phone (Optional[str]): Número de telefone (opcional)
        website (Optional[str]): Website do usuário (opcional)
    """
    id: int
    name: str
    username: str
    email: str
    phone: Optional[str]
    website: Optional[str]

    @field_validator('email')
    def email_must_contain_at(cls, v: str) -> str:
        """
        Validador para garantir que o email contém @
        
        Args:
            v (str): Valor do campo email
            
        Returns:
            str: Email validado
            
        Raises:
            ValueError: Se o email não contiver @
        """
        if '@' not in v:
            raise ValueError('Formato de email inválido')
        return v