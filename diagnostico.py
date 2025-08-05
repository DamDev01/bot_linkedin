#!/usr/bin/env python3
"""
Diagnóstico simples para verificar se o bot consegue acessar o LinkedIn
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

def diagnostico_simples():
    """Diagnóstico básico do navegador e acesso ao LinkedIn"""
    try:
        print("🔍 Iniciando diagnóstico...")
        
        # Configura o Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("🌐 Iniciando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("✅ Navegador iniciado com sucesso!")
        print(f"📄 URL atual: {driver.current_url}")
        
        # Testa acesso ao Google primeiro
        print("🔍 Testando acesso ao Google...")
        driver.get("https://www.google.com")
        time.sleep(3)
        print(f"✅ Google carregado: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Testa acesso ao LinkedIn
        print("🔍 Testando acesso ao LinkedIn...")
        driver.get("https://www.linkedin.com")
        time.sleep(5)
        print(f"✅ LinkedIn carregado: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Verifica se chegou na página de login
        if "login" in driver.current_url or "signup" in driver.current_url:
            print("✅ Página de login do LinkedIn carregada!")
            
            # Tenta encontrar elementos de login
            try:
                email_input = driver.find_element(By.ID, "username")
                print("✅ Campo de email encontrado!")
            except:
                print("❌ Campo de email não encontrado")
                
            try:
                senha_input = driver.find_element(By.ID, "password")
                print("✅ Campo de senha encontrado!")
            except:
                print("❌ Campo de senha não encontrado")
                
        else:
            print(f"⚠️ Página carregada não é de login: {driver.current_url}")
            
        # Testa acesso direto à página de login
        print("🔍 Testando acesso direto à página de login...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        print(f"✅ Página de login direta: {driver.current_url}")
        
        # Aguarda um pouco para você verificar
        print("\n⏳ Aguardando 10 segundos para você verificar...")
        time.sleep(10)
        
        # Fecha o navegador
        driver.quit()
        print("✅ Diagnóstico concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnostico_simples() 