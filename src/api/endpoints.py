# Constantes dos endpoints base da API
USERS_ENDPOINT = "users"        # Endpoint base para usuários
POSTS_ENDPOINT = "posts"        # Endpoint base para posts
COMMENTS_ENDPOINT = "comments"  # Endpoint base para comentários


class APIEndpoints:
    """
    Classe utilitária para construção de URLs de endpoints da API.
    Fornece métodos estáticos para gerar URLs formatadas para diferentes recursos.
    """
    
    @staticmethod
    def get_user(user_id: int) -> str:
        """
        Gera a URL para obter dados de um usuário específico
        
        Args:
            user_id (int): Identificador único do usuário
            
        Returns:
            str: URL formatada para o endpoint do usuário (ex: 'users/123')
        """
        return f"{USERS_ENDPOINT}/{user_id}"
    
    @staticmethod
    def get_user_posts(user_id: int) -> str:
        """
        Gera a URL para obter todos os posts de um usuário específico
        
        Args:
            user_id (int): Identificador único do usuário
            
        Returns:
            str: URL formatada para o endpoint de posts do usuário (ex: 'users/123/posts')
        """
        return f"{USERS_ENDPOINT}/{user_id}/posts"