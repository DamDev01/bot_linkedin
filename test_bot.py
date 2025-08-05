#!/usr/bin/env python3
"""
Script de teste para verificar se o bot do LinkedIn está funcionando corretamente
"""

import logging
import time
from modules.linkedin_bot import LinkedInBot

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_bot():
    """Testa o bot do LinkedIn"""
    try:
        print("🤖 Iniciando teste do bot do LinkedIn...")
        
        # Inicializa o bot
        bot = LinkedInBot()
        print("✅ Bot inicializado com sucesso")
        
        # Solicita credenciais
        email = input("📧 Digite seu email do LinkedIn: ")
        senha = input("🔒 Digite sua senha do LinkedIn: ")
        
        # Faz login
        print("🔐 Fazendo login...")
        if bot.fazer_login(email, senha):
            print("✅ Login realizado com sucesso!")
            
            # Testa busca simples
            termo_teste = input("🔍 Digite um termo para testar a busca (ex: 'python'): ")
            if not termo_teste:
                termo_teste = "python"
            
            print(f"🔍 Testando busca por: '{termo_teste}'")
            resultados = bot.buscar_perfis(termo_teste, limite=5)
            
            if resultados:
                print(f"✅ Busca bem-sucedida! Encontrados {len(resultados)} perfis:")
                for i, perfil in enumerate(resultados, 1):
                    print(f"   {i}. {perfil['nome']} - {perfil['cargo']} - {perfil['acao_disponivel']}")
            else:
                print("❌ Nenhum perfil encontrado. Verifique se:")
                print("   - O termo de busca é válido")
                print("   - Você está logado corretamente")
                print("   - O LinkedIn não bloqueou o acesso")
        else:
            print("❌ Falha no login. Verifique suas credenciais.")
        
        # Fecha o navegador
        bot.fechar()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot() 