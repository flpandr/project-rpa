import logging
from typing import List, Dict
from ..models.user import User
from ..models.post import Post
from ..utils.logger import setup_logging
from ..utils.exceptions import ProcessingError
from src.models.user import User as UserModel
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Classe responsável pelo processamento e validação de dados de usuários e posts.
    Realiza cálculos de métricas e garante a integridade dos dados.
    """
    
    @staticmethod
    def process_users(users_data: List[Dict]) -> List[User]:
        """
        Processa e valida uma lista de dados de usuários
        
        Args:
            users_data (List[Dict]): Lista de dicionários contendo dados dos usuários
            
        Returns:
            List[User]: Lista de objetos User validados
            
        Observações:
            - Usuários com dados incompletos são ignorados
            - Erros de validação são registrados no log
        """
        validated_users = []
        logger.info(f"Iniciando processamento de {len(users_data)} usuários")
        
        for user in users_data:
            # Verifica campos obrigatórios
            if not all(key in user for key in ['id', 'name']):
                logger.warning(
                    "Dados de usuário ignorados por estarem incompletos: %s",
                    user
                )
                continue
                
            try:
                # Tenta criar e validar o objeto de usuário
                validated_user = UserModel(**user)
                validated_users.append(validated_user)
                logger.debug(f"Usuário {validated_user.id} processado com sucesso")
                
            except ValidationError as e:
                logger.error(
                    "Falha na validação dos dados do usuário: %s. Detalhes: %s",
                    user.get('id', 'ID desconhecido'),
                    e.json()
                )
        
        logger.info(f"Processamento finalizado. {len(validated_users)} usuários válidos encontrados")
        return validated_users
    
    @staticmethod
    def process_posts(posts_data: List[Dict]) -> List[Post]:
        """
        Processa e converte dados de posts em objetos Post
        
        Args:
            posts_data (List[Dict]): Lista de dicionários contendo dados dos posts
            
        Returns:
            List[Post]: Lista de objetos Post criados
            
        Raises:
            KeyError: Se algum campo obrigatório estiver faltando
        """
        logger.info(f"Iniciando processamento de {len(posts_data)} posts")
        processed_posts = []
        
        for post in posts_data:
            try:
                processed_post = Post(
                    id=post['id'],
                    user_id=post['userId'],
                    title=post['title'],
                    body=post['body']
                )
                processed_posts.append(processed_post)
                logger.debug(f"Post {processed_post.id} processado com sucesso")
                
            except KeyError as e:
                logger.error(
                    "Campo obrigatório ausente no post: %s. Dados: %s",
                    str(e),
                    post
                )
        
        logger.info(f"Processamento finalizado. {len(processed_posts)} posts processados")
        return processed_posts
    
    @staticmethod
    def calculate_metrics(user: User, posts: List[Post]) -> User:
        """
        Calcula métricas de posts para um usuário específico
        
        Args:
            user (User): Objeto usuário para calcular métricas
            posts (List[Post]): Lista de todos os posts disponíveis
            
        Returns:
            User: Objeto usuário atualizado com métricas calculadas
            
        Raises:
            ProcessingError: Se ocorrer erro durante o cálculo das métricas
            
        Métricas calculadas:
            - Quantidade total de posts
            - Média de caracteres por post
        """
        logger.info(f"Iniciando cálculo de métricas para usuário {user.id}")
        
        try:
            # Filtra posts do usuário
            user_posts = [post for post in posts if post.user_id == user.id]
            user.posts = user_posts
            user.post_count = len(user_posts)
            
            # Calcula média de caracteres se houver posts
            if user_posts:
                total_chars = sum(len(post.body.strip()) for post in user_posts)
                user.avg_chars = total_chars / len(user_posts)
                logger.debug(
                    "Métricas calculadas para usuário %d: %d posts, média de %.2f caracteres",
                    user.id,
                    user.post_count,
                    user.avg_chars
                )
            else:
                user.avg_chars = 0
                logger.warning(f"Usuário {user.id} não possui posts")
                
            return user
            
        except Exception as e:
            error_msg = f"Erro ao calcular métricas para usuário {user.id}"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ProcessingError(error_msg) from e

    @staticmethod
    def validate_users(users: List[User]):
        """Valida lista de usuários antes de gerar relatórios"""
        if not users:
            logger.error("Dados inválidos para relatório - lista de usuários vazia")
            raise ValueError("Nenhum dado disponível para exportação")
        
        if any(not user.post_count for user in users):
            logger.warning("Usuários com contagem de posts zerada detectados")