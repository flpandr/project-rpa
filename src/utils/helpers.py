from typing import List, Dict
from ..models.user import User
from ..models.post import Post

def sort_users_by_post_count(users: List[User]) -> List[User]:
    """
    Ordena usuários pelo número de posts em ordem decrescente
    
    Args:
        users: Lista de objetos User para ordenação
        
    Returns:
        List[User]: Lista ordenada de usuários
    """
    return sorted(users, key=lambda x: x.post_count or 0, reverse=True)

def filter_active_users(users: List[User], min_posts: int = 1) -> List[User]:
    """
    Filtra usuários com número mínimo de posts
    
    Args:
        users: Lista de usuários para filtrar
        min_posts: Número mínimo de posts para considerar usuário ativo
        
    Returns:
        List[User]: Lista de usuários ativos
    """
    return [user for user in users if user.post_count and user.post_count >= min_posts]

def get_average_post_length(posts: List[Post]) -> float:
    """
    Calcula o comprimento médio dos posts
    
    Args:
        posts: Lista de posts para análise
        
    Returns:
        float: Média de caracteres por post ou 0.0 se lista vazia
    """
    if not posts:
        return 0.0
    return sum(len(post.body) for post in posts) / len(posts)
