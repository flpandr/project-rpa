from dataclasses import dataclass

@dataclass
class Post:
    """
    Modelo de dados para representar um post de usuário
    
    Attributes:
        id (int): Identificador único do post
        user_id (int): Identificador do usuário que criou o post
        title (str): Título do post
        body (str): Conteúdo do post
    """
    id: int
    user_id: int
    title: str
    body: str