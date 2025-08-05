#!/usr/bin/env python3
"""
Teste específico da função fazer_login do bot
"""

import logging
import time
from modules.linkedin_bot import LinkedInBot

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def teste_bot_login():
    """Teste específico da função fazer_login"""
    try:
        print("🔐 Testando função fazer_login do bot...")
        
        # Inicializa o bot
        bot = LinkedInBot()
        print("✅ Bot inicializado")
        
        # Verifica se o driver foi criado
        if not bot.driver:
            print("❌ Driver não foi criado")
            return
        
        print(f"🌐 URL inicial: {bot.driver.current_url}")
        
        # Solicita credenciais
        email = input("📧 Email: ")
        senha = input("🔒 Senha: ")
        
        # Testa a função fazer_login
        print("🔐 Chamando bot.fazer_login()...")
        resultado = bot.fazer_login(email, senha)
        
        print(f"📊 Resultado da função: {resultado}")
        print(f"🌐 URL após login: {bot.driver.current_url}")
        print(f"📄 Título após login: {bot.driver.title}")
        print(f"🔍 Status is_logged_in: {bot.is_logged_in}")
        
        # Testa verificação de login
        print("🔍 Testando _verificar_login()...")
        verificado = bot._verificar_login()
        print(f"📊 Resultado da verificação: {verificado}")
        
        # Aguarda um pouco
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
    teste_bot_login() 