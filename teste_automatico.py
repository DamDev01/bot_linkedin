#!/usr/bin/env python3
"""
Teste automático com credenciais já incluídas
"""

import logging
import time
from modules.linkedin_bot import LinkedInBot

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def teste_automatico():
    """Teste automático com credenciais"""
    try:
        print("🔐 Iniciando teste automático...")
        
        # Credenciais
        email = "damdev0101@gmail.com"
        senha = "bbnn182706"
        
        print(f"📧 Email: {email}")
        print(f"🔒 Senha: {senha}")
        
        # Inicializa o bot
        bot = LinkedInBot()
        print("✅ Bot inicializado")
        
        # Verifica se o driver foi criado
        if not bot.driver:
            print("❌ Driver não foi criado")
            return
        
        print(f"🌐 URL inicial: {bot.driver.current_url}")
        
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
        
        # Se o login funcionou, testa busca
        if resultado and bot.is_logged_in:
            print("\n🔍 Testando busca de perfis...")
            resultados = bot.buscar_perfis("python", limite=3)
            
            if resultados:
                print(f"✅ Busca bem-sucedida! Encontrados {len(resultados)} perfis:")
                for i, perfil in enumerate(resultados, 1):
                    print(f"   {i}. {perfil['nome']} - {perfil['cargo']} - {perfil['acao_disponivel']}")
            else:
                print("❌ Nenhum perfil encontrado na busca")
        
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
    teste_automatico() 