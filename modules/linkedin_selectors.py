# Arquivo de seletores centralizados para LinkedIn
# Use este arquivo para importar seletores em outros módulos do projeto

SELETOR_BOTAO_SEGUIR_LINKEDIN = 'xpath=//button[@aria-label="Seguir"]'
SELETOR_BOTAO_SEGUINDO_EMPRESA_LINKEDIN = 'xpath=//button[@aria-label="Seguindo"]'
SELETOR_SPAN_PRIMEIRO_CONTATO_LINKEDIN = 'xpath=//span[contains(@class, "dist-value")]'
SELETOR_BOTAO_CONECTAR_LINKEDIN = 'xpath=//main//button[contains(@aria-label, "conectar")]'
SELETOR_BOTAO_PENDENTE_LINKEDIN = 'xpath=//main//button[contains(@aria-label, "Pendente")]'
SELETOR_BOTAO_MAIS_LINKEDIN = 'xpath=//div[not(contains(@class, "header"))]/div/button/span[contains(text(), "Mais")]'
SELETOR_BOTAO_MAIS_CONECTAR_LINKEDIN = SELETOR_BOTAO_MAIS_LINKEDIN + '/../..//span[contains(text(), "Conectar")]'
SELETOR_BOTAO_ADICIONAR_NOTA_LINKEDIN = 'xpath=//div[contains(@id, "modal")]//span[text()="Adicionar nota"]'
SELETOR_TEXT_AREA_LINKEDIN = 'xpath=//div[contains(@id, "modal")]//textarea[@name="message"]'
SELETOR_BOTAO_ENVIAR_MENSAGEM_LINKEDIN = 'xpath=//button[not(@disabled)][@aria-label="Enviar convite"]'
SELETOR_BOTAO_FECHAR_MENSAGEM_LINKEDIN = 'xpath=//button[@aria-label="Fechar"]'
SELETOR_ELEMENTO_EMPRESA_ATUAL_LINKEDIN = 'xpath=//div//span[contains(text(), "Experiência")][not(@class)]//..//..//..//..//..//..//ul/li[1]//a[contains(@href, "company")][//img[contains(@alt, "Logo da empresa")]]'
