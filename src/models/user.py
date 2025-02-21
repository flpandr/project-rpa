from typing import List
from dataclasses import dataclass, field
from .post import Post
from pydantic import BaseModel

class User(BaseModel):
    """
    Modelo de dados para usuário com métricas de posts
    
    Attributes:
        id (int): Identificador único do usuário
        name (str): Nome completo do usuário
        username (str): Nome de usuário
        email (str): Endereço de email
        posts (List[Post]): Lista de posts do usuário
        post_count (int): Quantidade total de posts
        avg_chars (float): Média de caracteres por post
    """
    id: int
    name: str
    username: str
    email: str
    posts: List['Post'] = []
    post_count: int = 0
    avg_chars: float = 0.0