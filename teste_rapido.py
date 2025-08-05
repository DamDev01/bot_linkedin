#!/usr/bin/env python3
"""
Teste rápido para verificar se a captura de perfis está funcionando
"""

import logging
import time
from modules.linkedin_bot import LinkedInBot

# Configura logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def teste_rapido():
    """Teste rápido da captura de perfis"""
    try:
        print("🚀 Iniciando teste rápido de captura...")
        
        # Inicializa o bot
        bot = LinkedInBot()
        print("✅ Bot inicializado")
        
        # Solicita credenciais
        email = input("📧 Email: ")
        senha = input("🔒 Senha: ")
        
        # Login
        print("🔐 Fazendo login...")
        if bot.fazer_login(email, senha):
            print("✅ Login realizado!")
            
            # Testa busca
            termo = "python"
            print(f"🔍 Testando busca por: '{termo}'")
            
            resultados = bot.buscar_perfis(termo, limite=3)
            
            if resultados:
                print(f"✅ Sucesso! Encontrados {len(resultados)} perfis:")
                for i, perfil in enumerate(resultados, 1):
                    print(f"   {i}. {perfil['nome']}")
                    print(f"      Cargo: {perfil['cargo']}")
                    print(f"      Localização: {perfil['localizacao']}")
                    print(f"      Ação: {perfil['acao_disponivel']}")
                    print(f"      Link: {perfil['link']}")
                    if perfil['resumo']:
                        print(f"      Resumo: {perfil['resumo'][:100]}...")
                    if perfil['conexoes_comum']:
                        print(f"      Conexões: {perfil['conexoes_comum']}")
                    print()
            else:
                print("❌ Nenhum perfil encontrado")
        else:
            print("❌ Falha no login")
        
        # Fecha o navegador
        bot.fechar()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_rapido() 