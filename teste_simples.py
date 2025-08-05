#!/usr/bin/env python3
"""
Teste muito simples para identificar o problema
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def teste_simples():
    """Teste muito simples do login"""
    try:
        print("🚀 Iniciando teste simples...")
        
        # Configura o Chrome (igual ao bot)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("🌐 Iniciando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Navegador iniciado!")
        print(f"📄 URL inicial: {driver.current_url}")
        
        # Vai para a página de login
        print("🔍 Indo para página de login...")
        driver.get("https://www.linkedin.com/login")
        
        # Aguarda a página carregar
        print("⏳ Aguardando página carregar...")
        time.sleep(5)
        
        print(f"📄 URL atual: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Verifica se os campos de login existem
        try:
            email_input = driver.find_element(By.ID, "username")
            print("✅ Campo de email encontrado!")
        except Exception as e:
            print(f"❌ Campo de email não encontrado: {e}")
            
        try:
            senha_input = driver.find_element(By.ID, "password")
            print("✅ Campo de senha encontrado!")
        except Exception as e:
            print(f"❌ Campo de senha não encontrado: {e}")
            
        try:
            entrar_btn = driver.find_element(By.CSS_SELECTOR, ".btn__primary--large")
            print("✅ Botão de entrar encontrado!")
        except Exception as e:
            print(f"❌ Botão de entrar não encontrado: {e}")
        
        # Solicita credenciais
        email = input("📧 Digite seu email: ")
        senha = input("🔒 Digite sua senha: ")
        
        # Tenta fazer login manualmente
        print("🔐 Tentando fazer login...")
        
        try:
            # Limpa os campos
            email_input.clear()
            senha_input.clear()
            time.sleep(1)
            
            # Preenche os campos
            email_input.send_keys(email)
            time.sleep(1)
            senha_input.send_keys(senha)
            time.sleep(1)
            
            print("✅ Campos preenchidos!")
            
            # Clica no botão
            entrar_btn.click()
            print("✅ Botão clicado!")
            
            # Aguarda redirecionamento
            print("⏳ Aguardando redirecionamento...")
            time.sleep(10)
            
            print(f"📄 URL após login: {driver.current_url}")
            print(f"📄 Título após login: {driver.title}")
            
            # Verifica se logou
            if "feed" in driver.current_url or "checkpoint" in driver.current_url:
                print("✅ Login parece ter funcionado!")
            else:
                print("⚠️ Login pode ter falhado")
                
        except Exception as e:
            print(f"❌ Erro durante login: {e}")
        
        # Aguarda um pouco
        print("\n⏳ Aguardando 10 segundos...")
        time.sleep(10)
        
        # Fecha o navegador
        driver.quit()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_simples() 