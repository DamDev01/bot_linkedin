#!/usr/bin/env python3
"""
Teste específico para verificar a função de login
"""

import logging
import time
from modules.linkedin_bot import LinkedInBot

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def teste_login():
    """Teste específico da função de login"""
    try:
        print("🔐 Iniciando teste de login...")
        
        # Inicializa o bot
        bot = LinkedInBot()
        print("✅ Bot inicializado")
        
        # Verifica se o driver foi criado
        if not bot.driver:
            print("❌ Driver não foi criado")
            return
        
        print(f"🌐 URL atual: {bot.driver.current_url}")
        
        # Solicita credenciais
        email = input("📧 Email: ")
        senha = input("🔒 Senha: ")
        
        # Testa login
        print("🔐 Fazendo login...")
        sucesso = bot.fazer_login(email, senha)
        
        if sucesso:
            print("✅ Login realizado com sucesso!")
            print(f"🌐 URL após login: {bot.driver.current_url}")
            print(f"📄 Título da página: {bot.driver.title}")
            
            # Verifica status do login
            if bot.is_logged_in:
                print("✅ Status: Logado")
            else:
                print("⚠️ Status: Não logado (mas login retornou True)")
                
            # Testa verificação de login
            print("🔍 Verificando login...")
            if bot._verificar_login():
                print("✅ Verificação de login: OK")
            else:
                print("❌ Verificação de login: Falhou")
                
        else:
            print("❌ Falha no login")
            print(f"🌐 URL atual: {bot.driver.current_url}")
            print(f"📄 Título da página: {bot.driver.title}")
        
        # Aguarda um pouco para verificar
        print("\n⏳ Aguardando 5 segundos...")
        time.sleep(5)
        
        # Fecha o navegador
        bot.fechar()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_login() 