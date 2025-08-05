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
        """Verifica se o login foi bem sucedido"""
        try:
            wait = WebDriverWait(self.driver, 5)
            # Procura por elementos que indicam que o usuário está logado
            wait.until(EC.any_of(
                EC.presence_of_element_located((By.ID, "global-nav")),
                EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.feed-identity-module")))
            )
            return True
        except TimeoutException:
            # Verifica se há desafio de segurança
            if "checkpoint" in self.driver.current_url or "challenge" in self.driver.current_url:
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
            return False
        except Exception as e:
            logging.warning(f"Erro ao verificar login: {e}")
            return False

    def processar_planilha_linkedin(self, planilha_path, mensagem_path, stop_flag=lambda: False):
        """Processa uma planilha com perfis do LinkedIn independente da configuração"""
        try:
            # Lê a planilha
            try:
                if planilha_path.endswith('.csv'):
                    df = pd.read_csv(planilha_path)
                else:
                    df = pd.read_excel(planilha_path)
            except Exception as e:
                logging.error(f"❌ Erro ao ler o arquivo: {e}")
                raise ValueError("Não foi possível ler o arquivo. Verifique se é uma planilha válida (.xlsx ou .csv).")

            # Lista expandida de possíveis nomes de coluna para links do LinkedIn
            colunas_link = [
                'link', 'url', 'perfil', 'profile', 'linkedin', 'linkedin_url',
                'linkedin_profile', 'perfil_linkedin', 'link_linkedin', 'endereco',
                'endereço', 'profile_url', 'contato', 'contact'
            ]

            # Procura por qualquer coluna que contenha esses termos
            todas_colunas = [col.lower().strip() for col in df.columns]
            coluna_link_encontrada = None

            # Primeiro tenta encontrar uma correspondência exata
            for col in df.columns:
                if col.lower().strip() in colunas_link:
                    coluna_link_encontrada = col
                    break

            # Se não encontrou, procura por colunas que contenham os termos
            if not coluna_link_encontrada:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if any(termo in col_lower for termo in ['linkedin', 'perfil', 'profile', 'url', 'link']):
                        coluna_link_encontrada = col
                        break

            # Se ainda não encontrou, tenta identificar uma coluna que pareça conter URLs do LinkedIn
            if not coluna_link_encontrada:
                for col in df.columns:
                    primeira_celula = str(df[col].iloc[0]).lower().strip() if not df.empty else ""
                    if 'linkedin.com' in primeira_celula:
                        coluna_link_encontrada = col
                        logging.info(f"🔍 Coluna de link identificada automaticamente: '{col}'")
                        break
            
            if not coluna_link_encontrada:
                raise ValueError("❌ Não foi possível encontrar a coluna de links do LinkedIn. Por favor, certifique-se de que a planilha contém uma coluna com links do LinkedIn ou URLs de perfil.")

            # Renomeia colunas para um formato padrão
            df = df.rename(columns={col: col.lower().strip().replace(' ', '_') for col in df.columns})
            coluna_link_encontrada = coluna_link_encontrada.lower().strip().replace(' ', '_')

            logging.info(f"🔍 Coluna de link identificada: '{coluna_link_encontrada}'")
            
            with open(mensagem_path, 'r', encoding='utf-8') as f:
                mensagem_template = f.read().strip()

            total_perfis = len(df)
            sucessos = 0
            logging.info(f"📊 Iniciando processamento de {total_perfis} perfis da planilha.")

            for idx, row in df.iterrows():
                if stop_flag():
                    logging.info("🛑 Processamento interrompido pelo usuário.")
                    break

                try:
                    # Processa e valida o URL do perfil
                    perfil_url = str(row.get(coluna_link_encontrada, '')).strip()
                    if not perfil_url or pd.isna(perfil_url):
                        logging.warning(f"⚠️ Linha {idx+1}: Link vazio, pulando...")
                        continue

                    # Limpa e normaliza o URL
                    perfil_url = perfil_url.replace('\\', '/').strip()
                    
                    # Remove parâmetros de URL desnecessários
                    if '?' in perfil_url:
                        perfil_url = perfil_url.split('?')[0]

                    # Lida com diferentes formatos de URL
                    if 'linkedin.com' in perfil_url:
                        # Se já é um URL do LinkedIn, normaliza
                        if not perfil_url.startswith('http'):
                            perfil_url = 'https://' + perfil_url.lstrip('/')
                    else:
                        # Se é apenas um username/identificador
                        username = perfil_url.split('/')[-1] if '/' in perfil_url else perfil_url
                        username = username.strip('@').strip()  # Remove @ se presente
                        perfil_url = f"https://www.linkedin.com/in/{username}"

                    # Verifica se o URL parece válido
                    if not re.match(r'https?://[^/]+/in/[^/]+/?$', perfil_url):
                        logging.warning(f"⚠️ Linha {idx+1}: Link parece inválido: {perfil_url}")

                    logging.info(f"🔄 [{idx+1}/{total_perfis}] Processando: {perfil_url}")

                    if self.acessar_perfil_especifico(perfil_url):
                        mensagem_personalizada = self._preparar_mensagem(mensagem_template, row)
                        
                        if self.executar_acao_perfil(mensagem_personalizada, "auto"):
                            sucessos += 1
                            logging.info(f"✅ Ação executada com sucesso para {perfil_url}")
                        else:
                            logging.warning(f"⚠️ Não foi possível executar ação no perfil {perfil_url}")
                    else:
                        logging.error(f"❌ Não foi possível acessar o perfil {perfil_url}")

                    intervalo = random.uniform(5, 12)
                    logging.info(f"⏳ Aguardando {intervalo:.1f}s...")
                    time.sleep(intervalo)

                except Exception as e:
                    logging.error(f"❌ Erro ao processar linha {idx+1}: {e}")
                    continue

            taxa_sucesso = (sucessos / total_perfis) * 100 if total_perfis > 0 else 0
            logging.info("\n📊 Relatório Final:")
            logging.info(f"✅ Sucessos: {sucessos} | ❌ Falhas: {total_perfis - sucessos} | 📈 Taxa: {taxa_sucesso:.1f}%")
            return True

        except Exception as e:
            logging.error(f"❌ Erro grave ao processar planilha: {e}")
            return False

    def _preparar_mensagem(self, template, dados):
        """Prepara mensagem personalizada com dados do perfil. (Tornado público para uso na UI)"""
        try:
            mensagem = template
            # Usa um dicionário para os dados, facilitando o acesso
            dados_dict = dados.to_dict() if isinstance(dados, pd.Series) else dados
            
            for coluna, valor in dados_dict.items():
                placeholder = f"{{{coluna}}}"
                if placeholder in mensagem and pd.notna(valor):
                    mensagem = mensagem.replace(placeholder, str(valor))
            
            # Remove placeholders não substituídos
            mensagem = re.sub(r'\{[^}]+\}', '', mensagem).strip()
            mensagem = re.sub(r'\s+', ' ', mensagem)
            return mensagem

        except Exception as e:
            logging.error(f"❌ Erro ao preparar mensagem: {e}. Usando template original.")
            return template

    def acessar_perfil_especifico(self, url):
        """
        Acessa um perfil específico do LinkedIn de forma robusta,
        aguardando por múltiplos seletores possíveis.
        """
        try:
            if not url: return False
            if not url.startswith('http'): url = f"https://www.linkedin.com/in/{url.split('linkedin.com/in/')[-1]}"

            self.driver.get(url)
            # Um pequeno tempo de espera aleatório para simular comportamento humano
            time.sleep(random.uniform(1.5, 3.0))

            wait = WebDriverWait(self.driver, 20) # Aumentado o timeout para 20 segundos

            # Lista de possíveis seletores que indicam um perfil carregado (do mais ao menos provável)
            # Usamos tuplas (By, "seletor") para maior clareza
            locators = [
                (By.CSS_SELECTOR, ".pvs-profile-actions"),  # Contêiner dos botões de ação (Conectar, Mensagem, Seguir) - MUITO CONFIÁVEL
                (By.ID, "experience"),                      # Seção de Experiência
                (By.CSS_SELECTOR, "h1.text-heading-xlarge"),# Nome do perfil
                (By.CSS_SELECTOR, ".pv-top-card"),          # Layout antigo, mas ainda pode aparecer
                (By.CSS_SELECTOR, ".profile-view"),         # Outro seletor de contêiner de perfil
                (By.XPATH, "//*[contains(text(), 'perfil não está disponível')]") # Mensagem de perfil indisponível
            ]

            # Converte a lista de localizadores para uma lista de Expected Conditions
            conditions = [EC.presence_of_element_located(loc) for loc in locators]

            # Espera até que QUALQUER um dos seletores acima seja encontrado
            wait.until(EC.any_of(*conditions))

            # Agora, verificamos se a página carregada é de um perfil indisponível
            try:
                unavailable_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'perfil não está disponível')]")
                if unavailable_element.is_displayed():
                    logging.warning(f"ℹ️ Perfil inacessível ou privado: {url}")
                    return False
            except NoSuchElementException:
                # Se não encontrou a mensagem de "indisponível", o perfil é válido.
                logging.info(f"✅ Perfil acessado e validado com sucesso: {url}")
                return True

            # Se chegou aqui, algo estranho aconteceu (encontrou a condição, mas não era o que esperávamos)
            logging.info(f"✅ Perfil acessado, mas pode ter conteúdo limitado: {url}")
            return True # Retorna True para tentar prosseguir

        except TimeoutException:
            # Se mesmo após 20s NENHUM dos seletores foi encontrado
            if "authwall" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                logging.error("❌ LinkedIn solicitou autenticação. Tentando relogin...")
                if self._relogin():
                    return self.acessar_perfil_especifico(url) # Tenta acessar novamente após o relogin
                return False

            logging.warning(f"⚠️ Timeout final ao tentar validar o perfil: {url}")
            logging.warning("   Isso pode ocorrer se o perfil não existir, for restrito, ou o layout do LinkedIn mudou drasticamente.")
            # Uma última verificação pela URL
            if '/in/' in self.driver.current_url:
                logging.warning("   A URL parece correta, mas o conteúdo não foi reconhecido pelo bot.")

            return False
        except Exception as e:
            logging.error(f"❌ Erro inesperado ao acessar o perfil {url}: {e}")
            return False

    def _find_first_available_button(self, locators):
        """Helper para encontrar o primeiro botão visível e clicável de uma lista de localizadores."""
        for by, value in locators:
            try:
                elements = self.driver.find_elements(by, value)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Faz um scroll suave para garantir que o elemento esteja na tela
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(0.5) # Pequena pausa para o scroll finalizar
                        return element
            except (NoSuchElementException, WebDriverException):
                continue
        return None

    def executar_acao_perfil(self, mensagem, tipo_acao="auto"):
        """Executa uma ação em um perfil (conectar, seguir ou enviar mensagem) de forma robusta."""
        try:
            wait = WebDriverWait(self.driver, 10)

            # --- Definição de múltiplos localizadores para cada ação ---
            pendente_locators = [
                (By.XPATH, "//button[contains(., 'Pendente')]") ,
                (By.CSS_SELECTOR, "button[aria-label*='Pendente']"),
                (By.XPATH, SELETOR_BOTAO_PENDENTE_LINKEDIN.replace('xpath=', ''))
            ]
            conectar_locators = [
                (By.XPATH, "//button[.//span[text()='Conectar']]") ,
                (By.XPATH, "//button[contains(., 'Conectar')]") ,
                (By.CSS_SELECTOR, ".pvs-profile-actions button[aria-label*='Conectar']"),
                (By.XPATH, SELETOR_BOTAO_CONECTAR_LINKEDIN.replace('xpath=', ''))
            ]
            seguir_locators = [
                (By.XPATH, "//button[.//span[text()='Seguir']]") ,
                (By.XPATH, "//button[contains(., 'Seguir')]") ,
                (By.CSS_SELECTOR, "button[aria-label*='Seguir']"),
                (By.XPATH, SELETOR_BOTAO_SEGUIR_LINKEDIN.replace('xpath=', ''))
            ]
            mensagem_locators = [
                (By.CSS_SELECTOR, ".pvs-profile-actions .message-anywhere-button"),
                (By.XPATH, "//a[contains(@href, '/messaging/thread/')]") ,
                (By.XPATH, "//button[.//span[text()='Mensagem']]")
            ]

            # --- Lógica de Ação ---
            # 1. Verifica se a conexão já está pendente
            if self._find_first_available_button(pendente_locators):
                logging.info("ℹ️ Conexão já está pendente ou foi aceita.")
                return True

            # 2. Encontra os botões de ação disponíveis
            btn_conectar = self._find_first_available_button(conectar_locators)
            btn_seguir = self._find_first_available_button(seguir_locators)
            btn_mensagem = self._find_first_available_button(mensagem_locators)

            # 3. Decide a ação se for 'auto'
            if tipo_acao == "auto":
                if btn_conectar: tipo_acao = 'conectar'
                elif btn_mensagem: tipo_acao = 'mensagem' # Prioriza mensagem se já for conexão
                elif btn_seguir: tipo_acao = 'seguir'
                else:
                    logging.warning("⚠️ Nenhuma ação principal (Conectar, Mensagem, Seguir) encontrada.")
                    return False
                logging.info(f"🎯 Ação automática escolhida: {tipo_acao.capitalize()}")

            # 4. Executa a ação escolhida
            if tipo_acao == 'conectar' and btn_conectar:
                btn_conectar.click()
                time.sleep(1.5)
                # Lida com a janela modal de conexão
                if mensagem: # Envia com nota se houver mensagem
                    try:
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Adicionar nota']"))).click()
                        time.sleep(1)
                        wait.until(EC.presence_of_element_located((By.ID, "custom-message"))).send_keys(mensagem[:300])
                        time.sleep(1)
                    except TimeoutException:
                        logging.warning("⚠️ Não foi possível adicionar nota (janela pode não ter aparecido). Enviando sem nota.")
                
                # Clica em Enviar
                send_button_locators = [
                    (By.CSS_SELECTOR, "button[aria-label='Enviar agora']"),
                    (By.CSS_SELECTOR, "button[aria-label='Enviar']")
                ]
                btn_enviar = self._find_first_available_button(send_button_locators)
                if btn_enviar:
                    btn_enviar.click()
                    logging.info("✅ Convite de conexão enviado.")
                    return True
                else:
                    logging.error("❌ Não foi possível encontrar o botão 'Enviar' no modal de conexão.")
                    return False

            elif tipo_acao == 'seguir' and btn_seguir:
                btn_seguir.click()
                logging.info("✅ Perfil seguido com sucesso.")
                return True

            elif tipo_acao == 'mensagem' and btn_mensagem:
                btn_mensagem.click()
                composer_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".msg-form__contenteditable[role='textbox']")))
                composer_input.send_keys(mensagem)
                time.sleep(1)
                send_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".msg-form__send-button")))
                send_button.click()
                time.sleep(2)
                try: # Tenta fechar a janela de chat
                    close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-control-name='overlay.close_conversation_window'], li-icon[type='close']")
                    for btn in close_buttons:
                        if btn.is_displayed():
                            btn.click()
                            break
                except:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                logging.info("✅ Mensagem enviada com sucesso.")
                return True

            logging.warning(f"⚠️ Ação '{tipo_acao}' não pôde ser executada (botão não encontrado ou desabilitado).")
            return False

        except Exception as e:
            logging.error(f"❌ Erro crítico ao executar ação no perfil: {e}")
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
        Busca perfis e agora também identifica o botão de ação disponível
        para cada um diretamente na página de resultados.
        Versão com seletores atualizados para 2024.
        """
        try:
            if not termo:
                logging.error("❌ O termo de busca não pode ser vazio.")
                return []

            termo_busca_completo = f"{termo} {nicho} {regiao}".strip()
            from urllib.parse import quote_plus
            keywords = quote_plus(termo_busca_completo)
            url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER"
            
            logging.info(f"🚀 Iniciando busca por: '{termo_busca_completo}'")
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-results-container")))
            
            perfis_encontrados = []
            resultados_unicos = set()
            scrolls_sem_novos_resultados = 0

            while len(perfis_encontrados) < limite:
                # --- SELETOR PRINCIPAL ATUALIZADO ---
                # Este é o seletor mais importante. Ele procura por cada item 'li' na lista de resultados de busca.
                resultados_atuais = self.driver.find_elements(By.CSS_SELECTOR, "ul.reusable-search__results-container > li.reusable-search__result-container")
                
                if not resultados_atuais:
                    # Se não encontrar nada com o seletor principal, pode ser uma página sem resultados.
                    logging.info("ℹ️ Nenhum container de resultado encontrado na página atual.")
                    break

                novos_perfis_nesta_rolagem = 0
                for resultado in resultados_atuais:
                    if len(perfis_encontrados) >= limite:
                        break
                    
                    try:
                        link_element = resultado.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                        link = link_element.get_attribute('href')
                        if "/in/" not in link or "/search/" in link: continue
                        if link in resultados_unicos: continue
                        
                        nome = link_element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.strip()
                        if not nome: continue

                        subtitulo = ""
                        try:
                            subtitulo = resultado.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle").text.strip()
                        except NoSuchElementException: pass

                        acao_disponivel = "N/A"
                        element_botao = None
                        try:
                            # Tenta encontrar o botão "Conectar"
                            try:
                                botao = resultado.find_element(By.XPATH, ".//button[.//span[text()='Conectar']]")
                                if botao.is_displayed() and botao.is_enabled():
                                    acao_disponivel = "Conectar"
                                    element_botao = botao
                            except NoSuchElementException:
                                # Se não encontrar "Conectar", tenta "Seguir"
                                try:
                                    botao = resultado.find_element(By.XPATH, ".//button[.//span[text()='Seguir']]")
                                    if botao.is_displayed() and botao.is_enabled():
                                        acao_disponivel = "Seguir"
                                        element_botao = botao
                                except NoSuchElementException:
                                    # Se não encontrar "Seguir", tenta outros estados
                                    try:
                                        botao = resultado.find_element(By.XPATH, ".//button[.//span[text()='Pendente']]")
                                        if botao.is_displayed() and botao.is_enabled():
                                            acao_disponivel = "Pendente"
                                            element_botao = botao
                                    except NoSuchElementException:
                                        try:
                                            botao = resultado.find_element(By.XPATH, ".//button[.//span[text()='Mensagem']]")
                                            if botao.is_displayed() and botao.is_enabled():
                                                acao_disponivel = "Mensagem"
                                                element_botao = botao
                                        except NoSuchElementException:
                                            acao_disponivel = "Indisponível"
                        except Exception:
                            acao_disponivel = "Indisponível"
                        
                        perfil_data = {
                            'nome': nome,
                            'cargo': subtitulo,
                            'empresa': "",
                            'link': link,
                            'acao_disponivel': acao_disponivel,
                            'element_botao': element_botao
                        }

                        perfis_encontrados.append(perfil_data)
                        resultados_unicos.add(link)
                        novos_perfis_nesta_rolagem += 1

                    except Exception: continue
                
                if len(perfis_encontrados) >= limite: break

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2.5, 4.0))
                
                if novos_perfis_nesta_rolagem == 0:
                    scrolls_sem_novos_resultados += 1
                else:
                    scrolls_sem_novos_resultados = 0
                
                if scrolls_sem_novos_resultados >= 2:
                    logging.info("ℹ️ Fim da página de resultados alcançado.")
                    break

            # Adiciona um log final para confirmar o que foi extraído.
            if perfis_encontrados:
                logging.info(f"✅ Busca concluída. {len(perfis_encontrados)} perfis extraídos e prontos na lista.")
            else:
                logging.warning("⚠️ Busca concluída, mas 0 perfis foram extraídos. Verifique se há resultados na página ou se o layout do LinkedIn mudou.")
            
            return perfis_encontrados[:limite]

        except Exception as e:
            logging.error(f"❌ Erro inesperado durante a busca de perfis: {e}")
            import traceback
            traceback.print_exc()
            return []