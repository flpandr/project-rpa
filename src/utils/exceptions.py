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