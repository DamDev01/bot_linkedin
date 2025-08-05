import os
import re
import time
import random
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from modules.linkedin_selectors import (
    SELETOR_BOTAO_SEGUIR_LINKEDIN,
    SELETOR_BOTAO_SEGUINDO_EMPRESA_LINKEDIN,
    SELETOR_SPAN_PRIMEIRO_CONTATO_LINKEDIN,
    SELETOR_BOTAO_CONECTAR_LINKEDIN,
    SELETOR_BOTAO_PENDENTE_LINKEDIN,
    SELETOR_BOTAO_MAIS_LINKEDIN,
    SELETOR_BOTAO_MAIS_CONECTAR_LINKEDIN,
    SELETOR_BOTAO_ADICIONAR_NOTA_LINKEDIN,
    SELETOR_TEXT_AREA_LINKEDIN,
    SELETOR_BOTAO_ENVIAR_MENSAGEM_LINKEDIN,
    SELETOR_BOTAO_FECHAR_MENSAGEM_LINKEDIN,
    SELETOR_ELEMENTO_EMPRESA_ATUAL_LINKEDIN
)

class LinkedInBot:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.setup_driver()

    def setup_driver(self):
        """Configura o driver do Chrome com opções otimizadas"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import logging
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
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            logging.info("Driver configurado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao configurar driver: {e}")
            raise

    def fazer_login(self, email, senha):
        """Realiza login no LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.driver.implicitly_wait(10)

            email_input = self.driver.find_element(By.ID, "username")
            senha_input = self.driver.find_element(By.ID, "password")
            entrar_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn__primary--large")

            email_input.clear()
            senha_input.clear()
            time.sleep(random.uniform(0.5, 1.5))

            email_input.send_keys(email)
            time.sleep(random.uniform(0.5, 1.5))
            senha_input.send_keys(senha)
            time.sleep(random.uniform(0.5, 1.5))
            entrar_btn.click()

            WebDriverWait(self.driver, 10).until(
                lambda x: "feed" in x.current_url or "checkpoint" in x.current_url or "challenge" in x.current_url
            )

            if self._verificar_login():
                self.is_logged_in = True
                self._ultimo_email = email
                self._ultima_senha = senha
                logging.info("✅ Login realizado com sucesso!")
                return True
            else:
                logging.error("❌ Falha no login. Verifique suas credenciais.")
                return False

        except TimeoutException:
            logging.error("Timeout durante login. Página demorou para carregar.")
            return False
        except NoSuchElementException:
            logging.error("Elemento não encontrado durante login.")
            return False
        except Exception as e:
            logging.error(f"Erro durante login: {e}")
            return False

    def _verificar_login(self):
        """Verifica se o login foi bem sucedido com verificações mais robustas"""
        try:
            wait = WebDriverWait(self.driver, 5)
            
            # Múltiplos indicadores de que o usuário está logado
            indicadores_login = [
                (By.ID, "global-nav"),
                (By.CLASS_NAME, "scaffold-layout__main"),
                (By.CSS_SELECTOR, "div.feed-identity-module"),
                (By.CSS_SELECTOR, "nav.global-nav"),
                (By.CSS_SELECTOR, "div.feed-identity-module__member-info"),
                (By.CSS_SELECTOR, "div.identity-module"),
                (By.CSS_SELECTOR, "div.feed-identity-module__member-info")
            ]
            
            for indicador in indicadores_login:
                try:
                    wait.until(EC.presence_of_element_located(indicador))
                    logging.debug(f"✅ Login verificado com sucesso usando: {indicador}")
                    return True
                except TimeoutException:
                    continue
            
            # Verifica se há desafio de segurança
            current_url = self.driver.current_url
            if "checkpoint" in current_url or "challenge" in current_url:
                logging.warning("⚠️ LinkedIn solicitou verificação de segurança (captcha, etc.).")
                logging.warning("Por favor, resolva manualmente no navegador do bot.")
                # Aguarda o usuário resolver
                try:
                    WebDriverWait(self.driver, 120).until(lambda d: "feed" in d.current_url)
                    logging.info("✅ Verificação de segurança resolvida.")
                    return True
                except TimeoutException:
                    logging.error("❌ Verificação de segurança não foi resolvida a tempo.")
                    return False
            
            # Verifica se está na página de login
            if "login" in current_url:
                logging.warning("⚠️ Ainda na página de login. Login não foi realizado.")
                return False
            
            # Verifica se há elementos de erro de login
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-error, .error, .login-error")
                if error_elements:
                    logging.error("❌ Elementos de erro de login encontrados.")
                    return False
            except:
                pass
            
            logging.warning("⚠️ Não foi possível confirmar o status do login.")
            logging.debug(f"URL atual: {current_url}")
            return False
            
        except Exception as e:
            logging.warning(f"Erro ao verificar login: {e}")
            return False

    def fechar(self):
        """Fecha o navegador e limpa recursos"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                logging.info("Navegador fechado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao fechar navegador: {e}")

    def buscar_perfis(self, termo, tipo="pessoa", nicho="", regiao="", limite=10):
        """
        Busca perfis com melhor tratamento de erros e seletores mais robustos
        """
        try:
            if not termo:
                logging.error("❌ O termo de busca não pode ser vazio.")
                return []

            # Verifica se está logado
            if not self.is_logged_in or not self._verificar_login():
                logging.error("❌ Não está logado no LinkedIn. Faça login primeiro.")
                return []

            termo_busca_completo = f"{termo} {nicho} {regiao}".strip()
            from urllib.parse import quote_plus
            keywords = quote_plus(termo_busca_completo)
            url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER"
            
            logging.info(f"🚀 Iniciando busca por: '{termo_busca_completo}'")
            logging.info(f"📄 Acessando URL: {url}")
            
            self.driver.get(url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(self.driver, 20)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-results-container")))
                logging.info("✅ Página de resultados carregada com sucesso")
            except TimeoutException:
                logging.warning("⚠️ Timeout aguardando container de resultados, tentando continuar...")
            
            # Aguarda um pouco para garantir que os resultados carregaram
            time.sleep(3)
            
            # Executa debug da página atual
            self._debug_pagina_atual()
            
            perfis_encontrados = []
            resultados_unicos = set()
            
            # Múltiplos seletores para tentar encontrar os containers de resultados
            seletores_containers = [
                "ul.reusable-search__results-container > li.reusable-search__result-container",
                "div.search-results-container li.reusable-search__result-container",
                "div.search-results-container .reusable-search__result-container",
                "ul.search-results-container li",
                ".search-results-container .reusable-search__result-container"
            ]
            
            containers = []
            for seletor in seletores_containers:
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    if containers:
                        logging.info(f"✅ Encontrados {len(containers)} containers com seletor: {seletor}")
                        break
                except Exception as e:
                    logging.debug(f"Seletor {seletor} falhou: {e}")
                    continue
            
            if not containers:
                logging.error("❌ Nenhum container de resultado encontrado. Verifique se a página carregou corretamente.")
                return []

            logging.info(f"🔍 Processando {len(containers)} containers de resultados...")
            
            for i, container in enumerate(containers):
                try:
                    # Nome
                    nome = ""
                    try:
                        nome_element = container.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                        nome = nome_element.text.strip()
                    except:
                        pass
                    
                    # Cargo
                    cargo = ""
                    try:
                        cargo_element = container.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                        cargo = cargo_element.text.strip()
                    except:
                        pass
                    
                    # Localização
                    localizacao = ""
                    try:
                        localizacao_element = container.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                        localizacao = localizacao_element.text.strip()
                    except:
                        pass
                    
                    # Link
                    link = ""
                    try:
                        link_element = container.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
                        link = link_element.get_attribute('href')
                        if '?' in link:
                            link = link.split('?')[0]
                    except:
                        pass
                    
                    # Ação disponível
                    acao_disponivel = "N/A"
                    try:
                        botao = container.find_element(By.CSS_SELECTOR, "button.artdeco-button")
                        if botao.is_displayed() and botao.is_enabled():
                            texto_botao = botao.text.strip()
                            if "Conectar" in texto_botao:
                                acao_disponivel = "Conectar"
                            elif "Seguir" in texto_botao:
                                acao_disponivel = "Seguir"
                            elif "Pendente" in texto_botao:
                                acao_disponivel = "Pendente"
                            elif "Mensagem" in texto_botao:
                                acao_disponivel = "Mensagem"
                    except:
                        pass
                    
                    # Só adiciona se temos pelo menos nome ou link
                    if nome or link:
                        perfil_data = {
                            'nome': nome,
                            'cargo': cargo,
                            'localizacao': localizacao,
                            'resumo': "",
                            'conexoes_comum': "",
                            'link': link,
                            'acao_disponivel': acao_disponivel,
                            'element_botao': None
                        }
                        perfis_encontrados.append(perfil_data)
                        resultados_unicos.add(link)
                        logging.debug(f"✅ Perfil {i+1}: {nome[:30]}... - {acao_disponivel}")
                    
                except Exception as e:
                    logging.debug(f"Erro ao processar container {i+1}: {e}")
                    continue

            # Log final detalhado
            if perfis_encontrados:
                logging.info(f"✅ Busca concluída com sucesso: {len(perfis_encontrados)} perfis extraídos")
                for i, perfil in enumerate(perfis_encontrados[:3]):
                    logging.info(f"   {i+1}. {perfil['nome'][:30]}... - {perfil['acao_disponivel']}")
                if len(perfis_encontrados) > 3:
                    logging.info(f"   ... e mais {len(perfis_encontrados) - 3} perfis")
            else:
                logging.warning("⚠️ Busca concluída, mas 0 perfis foram extraídos.")
                logging.warning("Possíveis causas:")
                logging.warning("  - Layout do LinkedIn mudou")
                logging.warning("  - Não há resultados para o termo buscado")
                logging.warning("  - Problema de carregamento da página")
                logging.warning("  - Necessário fazer login novamente")
            
            return perfis_encontrados[:limite]

        except Exception as e:
            logging.error(f"❌ Erro inesperado durante a busca de perfis: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _debug_pagina_atual(self):
        """Função de debug para capturar informações da página atual"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            logging.info(f"🔍 Debug - URL atual: {current_url}")
            logging.info(f"🔍 Debug - Título da página: {page_title}")
            
            # Verifica elementos importantes na página
            elementos_importantes = [
                "div.search-results-container",
                "ul.reusable-search__results-container",
                "li.reusable-search__result-container",
                "div.feed-identity-module",
                "nav.global-nav"
            ]
            
            for elemento in elementos_importantes:
                try:
                    encontrados = self.driver.find_elements(By.CSS_SELECTOR, elemento)
                    logging.info(f"🔍 Debug - Elemento '{elemento}': {len(encontrados)} encontrados")
                except Exception as e:
                    logging.debug(f"🔍 Debug - Erro ao verificar '{elemento}': {e}")
            
            # Verifica se há resultados de busca
            try:
                resultados = self.driver.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
                logging.info(f"🔍 Debug - Containers de resultado: {len(resultados)}")
                
                if resultados:
                    # Verifica o primeiro resultado
                    primeiro = resultados[0]
                    try:
                        nome_element = primeiro.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                        nome = nome_element.text.strip()
                        logging.info(f"🔍 Debug - Primeiro perfil: {nome[:50]}...")
                    except:
                        logging.info("🔍 Debug - Não foi possível extrair nome do primeiro perfil")
            except Exception as e:
                logging.debug(f"🔍 Debug - Erro ao verificar resultados: {e}")
                
        except Exception as e:
            logging.error(f"❌ Erro no debug da página: {e}") 