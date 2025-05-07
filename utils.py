import re

def validar_senha(senha):
    """
    Valida se a senha atende aos critérios de segurança:
    - Mínimo de 8 caracteres
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um símbolo especial (@$!%*?&)
    
    Retorna uma tupla (bool, str) onde:
    - bool: True se a senha é válida, False caso contrário
    - str: Mensagem de erro se a senha for inválida, ou None se for válida
    """
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'\d', senha):
        return False, "A senha deve conter pelo menos um número"
    
    if not re.search(r'[@$!%*?&]', senha):
        return False, "A senha deve conter pelo menos um símbolo especial (@$!%*?&)"
    
    return True, None
