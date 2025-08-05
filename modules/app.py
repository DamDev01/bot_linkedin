import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import queue
import time
import logging
import random
import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from modules.logging_utils import QueueHandler
from modules.linkedin_bot import LinkedInBot

class App(tk.Tk):
    # Métodos de ação e utilidade
    def process_log_queue(self):
        try:
            mensagens_processadas = 0
            while mensagens_processadas < 10:
                try:
                    record = self.log_queue.get_nowait()
                    msg = self.queue_handler.format(record)
                    self.adicionar_log(msg)
                    mensagens_processadas += 1
                except queue.Empty:
                    break
        except Exception as e:
            print(f"Erro ao processar logs: {e}")
        finally:
            self.after(100, self.process_log_queue)

    def adicionar_log(self, mensagem):
        def add_to_log():
            self.log_text.config(state="normal")
            timestamp = time.strftime('%H:%M:%S')
            linha_completa = f"[{timestamp}] {mensagem}\n"
            self.log_text.insert(tk.END, linha_completa)
            if "ERROR" in mensagem.upper():
                start_index = self.log_text.index("end-2c linestart")
                end_index = self.log_text.index("end-1c")
                self.log_text.tag_add("error", start_index, end_index)
                self.log_text.tag_config("error", foreground="red")
            elif "WARNING" in mensagem.upper():
                start_index = self.log_text.index("end-2c linestart")
                end_index = self.log_text.index("end-1c")
                self.log_text.tag_add("warning", start_index, end_index)
                self.log_text.tag_config("warning", foreground="orange")
            elif "SUCCESS" in mensagem.upper() or "SUCESSO" in mensagem.upper():
                start_index = self.log_text.index("end-2c linestart")
                end_index = self.log_text.index("end-1c")
                self.log_text.tag_add("success", start_index, end_index)
                self.log_text.tag_config("success", foreground="green")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 1000:
                self.log_text.config(state="normal")
                self.log_text.delete("1.0", f"{len(lines)-1000}.0")
                self.log_text.config(state="disabled")
        self.after(0, add_to_log)

    def fazer_login(self):
        if not self.email_var.get() or not self.senha_var.get():
            messagebox.showerror("Erro", "Por favor, insira email e senha")
            return
        threading.Thread(target=self._fazer_login_thread, daemon=True).start()

    def _fazer_login_thread(self):
        try:
            if not self.linkedin_bot:
                self.linkedin_bot = LinkedInBot()
            self.atualizar_status("Fazendo login...", "orange")
            sucesso = self.linkedin_bot.fazer_login(self.email_var.get(), self.senha_var.get())
            if sucesso:
                self.atualizar_status("Conectado", "green")
                logging.info("Login realizado com sucesso!")
            else:
                self.atualizar_status("Erro no login", "red")
                logging.error("Falha no login. Verifique suas credenciais.")
        except Exception as e:
            self.atualizar_status("Erro", "red")
            logging.error(f"Erro durante o login: {e}")

    def verificar_status(self):
        if not self.linkedin_bot:
            self.atualizar_status("Bot não inicializado", "red")
            return
        threading.Thread(target=self._verificar_status_thread, daemon=True).start()

    def _verificar_status_thread(self):
        try:
            if self.linkedin_bot.is_logged_in and self.linkedin_bot._verificar_login():
                self.atualizar_status("Conectado", "green")
                logging.info("Status: Conectado e funcionando")
            else:
                self.atualizar_status("Desconectado", "red")
                logging.warning("Status: Não conectado")
        except Exception as e:
            self.atualizar_status("Erro", "red")
            logging.error(f"Erro ao verificar status: {e}")

    def testar_perfil(self):
        if not self.linkedin_bot or not self.linkedin_bot.is_logged_in:
            messagebox.showerror("Erro", "Faça login primeiro")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Testar Perfil")
        dialog.geometry("500x150")
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="URL ou username do perfil:").pack(pady=5)
        url_var = tk.StringVar()
        ttk.Entry(frame, textvariable=url_var, width=60).pack(pady=5, fill=tk.X)
        def testar():
            url = url_var.get().strip()
            if url:
                dialog.destroy()
                threading.Thread(target=self._testar_perfil_thread, args=(url,), daemon=True).start()
        ttk.Button(frame, text="Testar", command=testar).pack(pady=10)

    def _testar_perfil_thread(self, url):
        try:
            logging.info(f"Testando acesso ao perfil: {url}")
            sucesso = self.linkedin_bot.acessar_perfil_especifico(url)
            if sucesso:
                logging.info("✅ Perfil acessado com sucesso!")
                resultado = self.linkedin_bot.executar_acao_perfil("Mensagem de teste", self.acao_var.get())
                if resultado:
                    logging.info("✅ Ação executada com sucesso!")
                else:
                    logging.warning("⚠️ Não foi possível executar ação no perfil")
            else:
                logging.error("❌ Falha ao acessar perfil")
        except Exception as e:
            logging.error(f"Erro durante teste: {e}")

        # NOVO MÉTODO COMPLETO (substitua o antigo)
    def _iniciar_acao_direta_busca(self, tree, acao_desejada):
        """Inicia uma ação (Conectar/Seguir) diretamente na página de busca."""
        perfis_selecionados = []
        items_selecionados = tree.selection()

        if not items_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um perfil na lista.")
            return
            
        for item in items_selecionados:
            # Pega os dados do perfil, incluindo o elemento do botão
            perfil_data = tree.resultados_data[tree.index(item)]
            perfis_selecionados.append(perfil_data)

        confirmacao = messagebox.askyesno("Confirmar Ação", 
            f"Você confirma a execução da ação '{acao_desejada.capitalize()}' em {len(perfis_selecionados)} perfil(s) diretamente na página de busca?")
        
        if confirmacao:
            threading.Thread(target=self._executar_acao_direta_thread, args=(perfis_selecionados, acao_desejada), daemon=True).start()

    def _executar_acao_direta_thread(self, perfis, acao_desejada):
        """Executa a ação diretamente na página de busca para os perfis selecionados."""
        sucessos = 0
        total = len(perfis)
        
        for i, perfil in enumerate(perfis):
            try:
                logging.info(f"[{i+1}/{total}] Tentando ação direta em: {perfil['nome']}")
                
                acao_disponivel = perfil.get('acao_disponivel')
                element_botao = perfil.get('element_botao')

                if not element_botao or not acao_disponivel:
                    logging.warning(f"⚠️ Botão de ação não encontrado para {perfil['nome']}.")
                    continue

                if acao_desejada.lower() in acao_disponivel.lower():
                    # Ação desejada corresponde ao botão visível
                    element_botao.click()
                    sucessos += 1
                    logging.info(f"✅ Ação '{acao_disponivel}' executada para {perfil['nome']}.")

                    # Lida com o modal de conexão se aparecer
                    if acao_desejada.lower() == 'conectar':
                        try:
                            # Espera e clica em enviar sem nota (mais rápido)
                            enviar_btn = WebDriverWait(self.linkedin_bot.driver, 3).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Enviar agora'], button[aria-label='Send now']"))
                            )
                            enviar_btn.click()
                            logging.info("   ↳ Convite enviado (sem nota).")
                        except TimeoutException:
                            # Se o modal não aparecer ou demorar, apenas continue
                            logging.info("   ↳ Modal de conexão não detectado, ação direta concluída.")
                            pass

                elif acao_disponivel == "Pendente":
                    logging.info(f"ℹ️ Conexão já pendente para {perfil['nome']}.")
                else:
                    logging.warning(f"⚠️ Ação '{acao_desejada}' não disponível para {perfil['nome']} (Disponível: {acao_disponivel}).")

                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                logging.error(f"❌ Erro ao executar ação direta em {perfil['nome']}: {e}")
                continue

        logging.info(f"🎯 Ação direta concluída: {sucessos}/{total} sucessos.")

    def abrir_janela_busca(self):
        if not self.linkedin_bot or not self.linkedin_bot.is_logged_in:
            messagebox.showerror("Erro", "Faça login primeiro")
            return
        
        busca_window = tk.Toplevel(self)
        busca_window.title("Buscar Perfis no LinkedIn")
        busca_window.geometry("750x700") # Aumentado a largura e altura
        busca_window.grab_set()

        PLACEHOLDER_TEXT = "Ex: 'Desenvolvedor Python' ou 'Gerente de Vendas'"
        PLACEHOLDER_COLOR = 'grey'
        DEFAULT_COLOR = 'black'

        def on_focus_in(event):
            if termo_entry.get() == PLACEHOLDER_TEXT:
                termo_entry.delete(0, tk.END)
                termo_entry.config(foreground=DEFAULT_COLOR)

        def on_focus_out(event):
            if not termo_entry.get():
                termo_entry.insert(0, PLACEHOLDER_TEXT)
                termo_entry.config(foreground=PLACEHOLDER_COLOR)

        main_frame = ttk.Frame(busca_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Busca Avançada de Perfis", font=("Arial", 14, "bold")).pack(pady=10)
        criterios_frame = ttk.LabelFrame(main_frame, text="Critérios de Busca", padding="10")
        criterios_frame.pack(fill=tk.X, pady=5)
        linha1 = ttk.Frame(criterios_frame)
        linha1.pack(fill=tk.X, pady=2)
        ttk.Label(linha1, text="Termo:", width=12).pack(side=tk.LEFT)
        termo_var = tk.StringVar()
        termo_entry = ttk.Entry(linha1, textvariable=termo_var, width=40)
        termo_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        termo_entry.insert(0, PLACEHOLDER_TEXT)
        termo_entry.config(foreground=PLACEHOLDER_COLOR)
        termo_entry.bind("<FocusIn>", on_focus_in)
        termo_entry.bind("<FocusOut>", on_focus_out)

        linha2 = ttk.Frame(criterios_frame)
        linha2.pack(fill=tk.X, pady=5)
        ttk.Label(linha2, text="Nicho (opcional):", width=15).pack(side=tk.LEFT)
        nicho_var = tk.StringVar()
        ttk.Combobox(linha2, textvariable=nicho_var, width=20, values=('', 'saude', 'tech', 'educacao', 'financas', 'marketing')).pack(side=tk.LEFT, padx=5)
        ttk.Label(linha2, text="Região (opcional):", width=15).pack(side=tk.LEFT, padx=(20, 5))
        regiao_var = tk.StringVar()
        ttk.Entry(linha2, textvariable=regiao_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(criterios_frame, text="🔍 Buscar Perfis", command=lambda: self._executar_busca_janela(
            termo_var.get(), 'pessoa', nicho_var.get(), regiao_var.get(), resultados_tree, busca_window, PLACEHOLDER_TEXT
        )).pack(pady=10)

        # Atualizamos as colunas para mostrar a ação disponível
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="5")
        resultados_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        colunas = ('nome', 'cargo', 'acao_disponivel', 'link')
        headers = {'nome': 'Nome', 'cargo': 'Cargo/Subtítulo', 'acao_disponivel': 'Ação na Busca', 'link': 'Link'}

        resultados_tree = ttk.Treeview(resultados_frame, columns=colunas, show='headings', height=12)
        for col in colunas:
            resultados_tree.heading(col, text=headers.get(col, col.capitalize()), anchor='w')
            if col == 'link':
                resultados_tree.column(col, width=200, anchor='w')
            elif col == 'acao_disponivel':
                resultados_tree.column(col, width=100, anchor='center')
            else:
                resultados_tree.column(col, width=180, anchor='w')

        v_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL, command=resultados_tree.yview)
        h_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.HORIZONTAL, command=resultados_tree.xview)
        resultados_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        resultados_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        resultados_frame.grid_rowconfigure(0, weight=1)
        resultados_frame.grid_columnconfigure(0, weight=1)
        resultados_tree.resultados_data = []

        # --- NOVOS BOTÕES PARA AÇÃO DIRETA ---
        acoes_diretas_frame = ttk.LabelFrame(main_frame, text="Ação Rápida (Direto na Busca)", padding="10")
        acoes_diretas_frame.pack(fill=tk.X, pady=5)
        ttk.Label(acoes_diretas_frame, text="Para os perfis selecionados na lista acima, clique em:").pack(anchor='w')
        
        botoes_diretos_frame = ttk.Frame(acoes_diretas_frame)
        botoes_diretos_frame.pack(pady=5)
        ttk.Button(botoes_diretos_frame, text="Conectar com Selecionados", command=lambda: self._iniciar_acao_direta_busca(resultados_tree, 'Conectar')).pack(side=tk.LEFT, padx=10)
        ttk.Button(botoes_diretos_frame, text="Seguir Selecionados", command=lambda: self._iniciar_acao_direta_busca(resultados_tree, 'Seguir')).pack(side=tk.LEFT, padx=10)
        
        # O frame de exportação permanece
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=5)
        ttk.Button(export_frame, text="Exportar Resultados para Excel", command=lambda: self._exportar_resultados(resultados_tree)).pack(side=tk.RIGHT, padx=5)
        resultados_tree = ttk.Treeview(resultados_frame, columns=colunas, show='headings', height=12)
        for col in colunas:
            resultados_tree.heading(col, text=headers.get(col, col.capitalize()))
            if col == 'link':
                resultados_tree.column(col, width=200, anchor='w')
            else:
                resultados_tree.column(col, width=150, anchor='w')
        v_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL, command=resultados_tree.yview)
        h_scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.HORIZONTAL, command=resultados_tree.xview)
        resultados_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        resultados_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        resultados_frame.grid_rowconfigure(0, weight=1)
        resultados_frame.grid_columnconfigure(0, weight=1)
        resultados_tree.resultados_data = []

        acoes_lote_frame = ttk.LabelFrame(main_frame, text="Ações em Lote", padding="10")
        acoes_lote_frame.pack(fill=tk.X, pady=5)
        conectar_frame = ttk.Frame(acoes_lote_frame)
        conectar_frame.pack(fill=tk.X, pady=2)
        ttk.Label(conectar_frame, text="Conectar:", width=12).pack(side=tk.LEFT)
        ttk.Button(conectar_frame, text="Selecionado(s)", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "conectar", "selecionado")).pack(side=tk.LEFT, padx=5)
        ttk.Button(conectar_frame, text="Todos na Lista", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "conectar", "todos")).pack(side=tk.LEFT, padx=5)
        seguir_frame = ttk.Frame(acoes_lote_frame)
        seguir_frame.pack(fill=tk.X, pady=2)
        ttk.Label(seguir_frame, text="Seguir:", width=12).pack(side=tk.LEFT)
        ttk.Button(seguir_frame, text="Selecionado(s)", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "seguir", "selecionado")).pack(side=tk.LEFT, padx=5)
        ttk.Button(seguir_frame, text="Todos na Lista", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "seguir", "todos")).pack(side=tk.LEFT, padx=5)
        mensagem_frame = ttk.Frame(acoes_lote_frame)
        mensagem_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mensagem_frame, text="Mensagem:", width=12).pack(side=tk.LEFT)
        ttk.Button(mensagem_frame, text="Selecionado(s)", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "mensagem", "selecionado")).pack(side=tk.LEFT, padx=5)
        ttk.Button(mensagem_frame, text="Todos na Lista", command=lambda: self._iniciar_acao_em_lote(resultados_tree, "mensagem", "todos")).pack(side=tk.LEFT, padx=5)
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, pady=5)
        ttk.Button(export_frame, text="Exportar Resultados para Excel", command=lambda: self._exportar_resultados(resultados_tree)).pack(side=tk.RIGHT, padx=5)

    # MÉTODO MODIFICADO (para ignorar o placeholder)
    def _executar_busca_janela(self, termo, tipo, nicho, regiao, tree, window, placeholder_text):
        termo_final = termo.strip()
        
        # Ignora a busca se o campo estiver vazio ou com o placeholder
        if not termo_final or termo_final == placeholder_text:
            messagebox.showerror("Erro", "Por favor, digite um termo de busca válido.", parent=window)
            return
            
        # Limpa resultados anteriores
        for item in tree.get_children():
            tree.delete(item)
        tree.resultados_data = []
        
        # Inicia a busca em uma nova thread
        threading.Thread(target=self._buscar_perfis_thread, args=(termo_final, tipo, nicho, regiao, tree), daemon=True).start()
    def _buscar_perfis_thread(self, termo, tipo, nicho, regiao, tree):
        try:
            limite = int(self.limite_var.get()) if self.limite_var.get().isdigit() else 10
            logging.info(f"Iniciando busca: {termo} (tipo: {tipo}, limite: {limite})")
            resultados = self.linkedin_bot.buscar_perfis(termo, tipo, nicho, regiao, limite)
            def atualizar_tree():
                for item in tree.get_children():
                    tree.delete(item)
                tree.resultados_data = resultados
                for resultado in resultados:
                    values = [resultado.get(col, '') for col in tree['columns']]
                    tree.insert('', tk.END, values=values)
            self.after(0, atualizar_tree)
            logging.info(f"✅ Busca concluída: {len(resultados)} resultados")
        except Exception as e:
            logging.error(f"Erro durante busca: {e}")

    def _obter_mensagem_dialog(self, title, prompt):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.grab_set()

        ttk.Label(dialog, text=prompt, wraplength=430, padding=(10, 10, 10, 0)).pack()
        
        text_frame = ttk.Frame(dialog, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        msg_text = tk.Text(text_frame, height=10, width=50, wrap=tk.WORD, font=("Arial", 10))
        msg_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=msg_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        msg_text.config(yscrollcommand=scrollbar.set)
        
        msg_text.focus_set()

        message_content = {"value": None}

        def on_ok():
            message_content["value"] = msg_text.get("1.0", tk.END).strip()
            if not message_content["value"]:
                messagebox.showwarning("Aviso", "A mensagem não pode estar vazia.", parent=dialog)
                return
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog, padding=(0, 0, 10, 10))
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Confirmar", command=on_ok, style="Accent.TButton").pack(side=tk.RIGHT)
        
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        self.wait_window(dialog)
        
        return message_content["value"]

    def _iniciar_acao_em_lote(self, tree, acao, escopo):
        perfis = []
        if escopo == 'selecionado':
            items_selecionados = tree.selection()
            if not items_selecionados:
                messagebox.showwarning("Aviso", "Selecione pelo menos um perfil na lista.")
                return
            for item in items_selecionados:
                perfis.append(tree.resultados_data[tree.index(item)])
        else: # escopo == 'todos'
            if not tree.resultados_data:
                messagebox.showwarning("Aviso", "Não há perfis na lista para processar.")
                return
            perfis = tree.resultados_data

        if not perfis:
            return

        mensagem_texto = "Olá! Gostaria de me conectar." # Padrão para seguir/conectar
        if acao == "mensagem":
            mensagem_texto = self._obter_mensagem_dialog(
                "Enviar Mensagem", 
                "Digite a mensagem. Use {nome}, {cargo}, etc. para personalizar."
            )
            if mensagem_texto is None: return # Usuário cancelou
        elif acao == "conectar":
             mensagem_texto = self._obter_mensagem_dialog(
                "Adicionar Nota de Conexão", 
                "Digite a nota (limite de 300 caracteres). Deixe em branco para enviar sem nota."
            )
             if mensagem_texto is None: return # Usuário cancelou

        confirmacao = messagebox.askyesno("Confirmar Ação", 
            f"Você confirma a execução da ação '{acao.capitalize()}' em {len(perfis)} perfil(s)?")
        if confirmacao:
            threading.Thread(target=self._executar_acao_multipla, args=(perfis, acao, mensagem_texto), daemon=True).start()

    def _executar_acao_multipla(self, perfis, acao, mensagem_texto):
        try:
            total = len(perfis)
            sucessos = 0
            for i, perfil in enumerate(perfis):
                if not self.automation_running: # Permitir parada pela automação principal
                    break
                try:
                    logging.info(f"[{i+1}/{total}] Processando: {perfil.get('nome', 'N/A')}")
                    
                    if not self.linkedin_bot.acessar_perfil_especifico(perfil.get('link')):
                        logging.error(f"❌ Erro ao acessar o perfil: {perfil.get('nome', 'N/A')}")
                        continue

                    # Prepara a mensagem personalizada para cada perfil
                    mensagem_personalizada = self.linkedin_bot._preparar_mensagem(mensagem_texto, perfil)

                    if self.linkedin_bot.executar_acao_perfil(mensagem_personalizada, acao):
                        sucessos += 1
                        logging.info(f"✅ Sucesso com {acao}: {perfil.get('nome', 'N/A')}")
                    else:
                        logging.warning(f"⚠️ Falha com {acao}: {perfil.get('nome', 'N/A')}")
                    
                    # Aplica intervalo
                    if self.intervalo_aleatorio_var.get():
                        intervalo = random.uniform(5, 12)
                    else:
                        intervalo = float(self.intervalo_var.get() or 7)
                    time.sleep(intervalo)
                except Exception as e:
                    logging.error(f"Erro no perfil {perfil.get('nome', 'N/A')}: {e}")
                    continue
            logging.info(f"🎯 Processamento em lote concluído: {sucessos}/{total} sucessos para a ação '{acao}'")
        except Exception as e:
            logging.error(f"Erro durante processamento múltiplo: {e}")

    def _exportar_resultados(self, tree):
        if not tree.resultados_data:
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar")
            return
        try:
            import pandas as pd
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")], title="Exportar Resultados")
            if file_path:
                df = pd.DataFrame(tree.resultados_data)
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:
                    df.to_excel(file_path, index=False)
                logging.info(f"✅ Resultados exportados: {file_path}")
                messagebox.showinfo("Sucesso", f"Resultados exportados:\n{file_path}")
        except Exception as e:
            logging.error(f"Erro ao exportar: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def iniciar_automacao(self):
        if not self.email_var.get() or not self.senha_var.get():
            messagebox.showerror("Erro", "Insira credenciais")
            return
        if not self.planilha_path.get() or not self.mensagem_path.get():
            messagebox.showerror("Erro", "Selecione planilha e mensagem")
            return
        import os
        if not os.path.exists(self.planilha_path.get()):
            messagebox.showerror("Erro", "Planilha não encontrada")
            return
        if not os.path.exists(self.mensagem_path.get()):
            messagebox.showerror("Erro", "Arquivo de mensagem não encontrado")
            return
        confirmacao = messagebox.askyesno("Confirmar", "Iniciar automação completa?\n\nIsso processará todos os perfis da planilha.")
        if not confirmacao:
            return
        self.automation_running = True
        self._atualizar_botoes_automacao(True)
        threading.Thread(target=self._executar_automacao_completa, daemon=True).start()

    def parar_automacao(self):
        self.automation_running = False
        self.progress_var.set("Parando...")
        logging.info("🛑 Automação interrompida pelo usuário")

    def _executar_automacao_completa(self):
        try:
            if not self.linkedin_bot:
                self.linkedin_bot = LinkedInBot()
            self.progress_var.set("Fazendo login...")
            if not self.linkedin_bot.is_logged_in:
                if not self.linkedin_bot.fazer_login(self.email_var.get(), self.senha_var.get()):
                    raise Exception("Falha no login")
            self.progress_var.set("Processando planilha...")
            sucesso = self.linkedin_bot.processar_planilha_linkedin(
                self.planilha_path.get(),
                self.mensagem_path.get(),
                stop_flag=lambda: not self.automation_running
            )
            if sucesso:
                self.progress_var.set("✅ Automação concluída!")
                logging.info("🎉 Automação completa finalizada com sucesso!")
                messagebox.showinfo("Sucesso", "Automação concluída com sucesso!")
            else:
                self.progress_var.set("❌ Automação com erros")
                logging.warning("⚠️ Automação finalizada com erros")
                messagebox.showwarning("Aviso", "Automação concluída com alguns erros")
        except Exception as e:
            self.progress_var.set("❌ Erro na automação")
            logging.error(f"Erro na automação: {e}")
            messagebox.showerror("Erro", f"Erro na automação:\n{e}")
        finally:
            self.automation_running = False
            self._atualizar_botoes_automacao(False)

    def _atualizar_botoes_automacao(self, executando):
        if executando:
            self.btn_iniciar.config(state="disabled")
            self.btn_parar.config(state="normal")
        else:
            self.btn_iniciar.config(state="normal")
            self.btn_parar.config(state="disabled")
            if not executando:
                self.progress_var.set("Pronto para iniciar")

    def atualizar_status(self, status, cor):
        def update():
            self.status_var.set(status)
            if hasattr(self, 'status_label'):
                if cor == "green":
                    self.status_label.config(foreground="green")
                elif cor == "red":
                    self.status_label.config(foreground="red")
                elif cor == "orange":
                    self.status_label.config(foreground="orange")
        self.after(0, update)

    def fechar_navegador(self):
        if self.linkedin_bot:
            self.linkedin_bot.fechar()
            self.linkedin_bot = None
            self.atualizar_status("Desconectado", "red")
            logging.info("Navegador fechado")
        else:
            logging.info("Nenhum navegador aberto")

    def selecionar_planilha(self):
        file_path = filedialog.askopenfilename(title="Selecionar Planilha", filetypes=[("Excel", "*.xlsx *.xls"), ("CSV", "*.csv")])
        if file_path:
            self.planilha_path.set(file_path)
            logging.info(f"Planilha selecionada: {file_path}")

    def selecionar_mensagem(self):
        file_path = filedialog.askopenfilename(title="Selecionar Mensagem", filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if file_path:
            self.mensagem_path.set(file_path)
            logging.info(f"Mensagem selecionada: {file_path}")

    def mostrar_exemplo_planilha(self):
        exemplo = """📋 ESTRUTURA DA PLANILHA\n\nSua planilha Excel deve ter as seguintes colunas:\n\n| link                                | nome          | empresa    | cargo         |\n|-------------------------------------|---------------|------------|---------------|\n| https://linkedin.com/in/joao-silva | João Silva    | TechCorp   | Desenvolvedor |\n| linkedin.com/in/maria-santos       | Maria Santos  | StartupXYZ | Gerente       |\n| carlos-oliveira                     | Carlos        | Empresa    | Analista      |\n\n✅ FORMATOS ACEITOS PARA LINKS:\n• URL completa: https://www.linkedin.com/in/usuario\n• URL simples: linkedin.com/in/usuario  \n• Apenas username: usuario\n\n📝 PERSONALIZAÇÃO DE MENSAGENS:\n• Use {nome}, {empresa}, {cargo} na mensagem\n• Exemplo: \"Olá {nome}! Vi que trabalha na {empresa}...\"\n\n💡 DICAS:\n• A coluna 'link' é obrigatória\n• Outras colunas são opcionais mas úteis para personalização\n• Mantenha dados limpos e organizados"""
        messagebox.showinfo("Exemplo de Planilha", exemplo)

    def mostrar_exemplo_mensagem(self):
        exemplo = """💬 EXEMPLO DE MENSAGEM PERSONALIZADA\n\nOlá {nome}!\n\nVi seu perfil e fiquei impressionado com sua experiência na {empresa} \ncomo {cargo}. \n\nGostaria de me conectar para trocarmos experiências sobre o mercado \ne possíveis oportunidades de colaboração.\n\nAbraços!\n\n🔄 PLACEHOLDERS DISPONÍVEIS:\n• {nome} - Nome da pessoa\n• {empresa} - Empresa atual  \n• {cargo} - Cargo/posição\n• {qualquer_coluna} - Use qualquer coluna da planilha\n\n💡 DICAS:\n• Mantenha mensagens curtas e pessoais\n• LinkedIn limita mensagens a 300 caracteres\n• Seja genuíno e profissional\n• Evite linguagem muito comercial"""
        messagebox.showinfo("Exemplo de Mensagem", exemplo)

    def limpar_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
        logging.info("Logs limpos")

    def salvar_logs(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt"), ("Todos", "*.*")], title="Salvar Logs")
            if file_path:
                conteudo = self.log_text.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                logging.info(f"✅ Logs salvos: {file_path}")
                messagebox.showinfo("Sucesso", f"Logs salvos em:\n{file_path}")
        except Exception as e:
            logging.error(f"Erro ao salvar logs: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar logs: {e}")

    def _salvar_configuracoes(self):
        """Salva as configurações do usuário em um arquivo JSON"""
        try:
            config = {
                'email': self.email_var.get(),
                'senha': self.senha_var.get() if self.salvar_senha_var.get() else '',
                'salvar_senha': self.salvar_senha_var.get(),
                'intervalo': self.intervalo_var.get(),
                'acao': self.acao_var.get(),
                'limite': self.limite_var.get(),
                'intervalo_aleatorio': self.intervalo_aleatorio_var.get(),
                'ultima_planilha': self.planilha_path.get(),
                'ultima_mensagem': self.mensagem_path.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            # Não loga aqui para não poluir os logs
        except Exception as e:
            logging.error(f"❌ Erro ao salvar configurações: {e}")

    def _carregar_configuracoes(self):
        """Carrega as configurações salvas do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Carrega as configurações nas variáveis
                self.email_var.set(config.get('email', ''))
                self.salvar_senha_var.set(config.get('salvar_senha', False))
                if self.salvar_senha_var.get():
                    self.senha_var.set(config.get('senha', ''))
                self.intervalo_var.set(config.get('intervalo', '7'))
                self.acao_var.set(config.get('acao', 'auto'))
                self.limite_var.set(config.get('limite', '10'))
                self.intervalo_aleatorio_var.set(config.get('intervalo_aleatorio', True))
                self.planilha_path.set(config.get('ultima_planilha', ''))
                self.mensagem_path.set(config.get('ultima_mensagem', ''))
                
                logging.info("✅ Configurações carregadas com sucesso")
        except Exception as e:
            logging.error(f"❌ Erro ao carregar configurações: {e}")

    def _criar_interface(self):
        """Cria a interface do usuário"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Título
        title_label = ttk.Label(main_frame, text="LinkedIn Automation Bot - Versão Otimizada", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        # Frame de credenciais
        self._criar_frame_credenciais(main_frame)
        # Frame de ações principais
        self._criar_frame_acoes(main_frame)
        # Frame de configurações
        self._criar_frame_configuracoes(main_frame)
        # Frame de arquivos
        self._criar_frame_arquivos(main_frame)
        # Frame de controle de automação
        self._criar_frame_automacao(main_frame)
        # Frame de logs
        self._criar_frame_logs(main_frame)

    def _criar_frame_credenciais(self, parent):
        cred_frame = ttk.LabelFrame(parent, text="Credenciais LinkedIn", padding="10")
        cred_frame.pack(fill=tk.X, pady=5)
        
        # Frame do email
        email_frame = ttk.Frame(cred_frame)
        email_frame.pack(fill=tk.X, pady=2)
        ttk.Label(email_frame, text="Email:", width=15).pack(side=tk.LEFT)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=40)
        self.email_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Frame da senha
        senha_frame = ttk.Frame(cred_frame)
        senha_frame.pack(fill=tk.X, pady=2)
        ttk.Label(senha_frame, text="Senha:", width=15).pack(side=tk.LEFT)
        self.senha_var = tk.StringVar()
        self.senha_entry = ttk.Entry(senha_frame, textvariable=self.senha_var, show="*", width=40)
        self.senha_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Checkbox para salvar senha
        opcoes_frame = ttk.Frame(cred_frame)
        opcoes_frame.pack(fill=tk.X, pady=2)
        self.salvar_senha_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opcoes_frame, 
            text="Salvar credenciais", 
            variable=self.salvar_senha_var
        ).pack(side=tk.LEFT, padx=5)

    def _criar_frame_acoes(self, parent):
        acoes_frame = ttk.LabelFrame(parent, text="Ações Principais", padding="10")
        acoes_frame.pack(fill=tk.X, pady=5)
        linha1 = ttk.Frame(acoes_frame)
        linha1.pack(fill=tk.X, pady=2)
        ttk.Button(linha1, text="Fazer Login", command=self.fazer_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(linha1, text="Buscar Perfis", command=self.abrir_janela_busca).pack(side=tk.LEFT, padx=5)
        ttk.Button(linha1, text="Testar Perfil", command=self.testar_perfil).pack(side=tk.LEFT, padx=5)
        linha2 = ttk.Frame(acoes_frame)
        linha2.pack(fill=tk.X, pady=2)
        ttk.Button(linha2, text="Verificar Status", command=self.verificar_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(linha2, text="Fechar Navegador", command=self.fechar_navegador).pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="Desconectado")
        self.status_label = ttk.Label(linha2, textvariable=self.status_var, foreground="red")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        ttk.Label(linha2, text="Status:").pack(side=tk.RIGHT)

    def _criar_frame_configuracoes(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Configurações", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        linha1 = ttk.Frame(config_frame)
        linha1.pack(fill=tk.X, pady=2)
        ttk.Label(linha1, text="Intervalo (s):", width=15).pack(side=tk.LEFT)
        self.intervalo_var = tk.StringVar(value="7")
        ttk.Entry(linha1, textvariable=self.intervalo_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(linha1, text="Ação:", width=10).pack(side=tk.LEFT, padx=(20, 5))
        self.acao_var = tk.StringVar(value="auto")
        acao_combo = ttk.Combobox(linha1, textvariable=self.acao_var, width=15, values=('auto', 'conectar', 'seguir', 'mensagem'))
        acao_combo.pack(side=tk.LEFT, padx=5)
        acao_combo.state(['readonly'])
        linha2 = ttk.Frame(config_frame)
        linha2.pack(fill=tk.X, pady=2)
        ttk.Label(linha2, text="Limite resultados:", width=15).pack(side=tk.LEFT)
        self.limite_var = tk.StringVar(value="10")
        ttk.Entry(linha2, textvariable=self.limite_var, width=10).pack(side=tk.LEFT, padx=5)
        self.intervalo_aleatorio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(linha2, text="Intervalo aleatório", variable=self.intervalo_aleatorio_var).pack(side=tk.LEFT, padx=(20, 5))

    def _criar_frame_arquivos(self, parent):
        arquivos_frame = ttk.LabelFrame(parent, text="Arquivos", padding="10")
        arquivos_frame.pack(fill=tk.X, pady=5)
        planilha_frame = ttk.Frame(arquivos_frame)
        planilha_frame.pack(fill=tk.X, pady=2)
        ttk.Label(planilha_frame, text="Planilha:", width=15).pack(side=tk.LEFT)
        self.planilha_path = tk.StringVar()
        ttk.Entry(planilha_frame, textvariable=self.planilha_path, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(planilha_frame, text="Selecionar", command=self.selecionar_planilha).pack(side=tk.RIGHT)
        ttk.Button(planilha_frame, text="Exemplo", command=self.mostrar_exemplo_planilha).pack(side=tk.RIGHT, padx=5)
        mensagem_frame = ttk.Frame(arquivos_frame)
        mensagem_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mensagem_frame, text="Mensagem:", width=15).pack(side=tk.LEFT)
        self.mensagem_path = tk.StringVar()
        ttk.Entry(mensagem_frame, textvariable=self.mensagem_path, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(mensagem_frame, text="Selecionar", command=self.selecionar_mensagem).pack(side=tk.RIGHT)
        ttk.Button(mensagem_frame, text="Exemplo", command=self.mostrar_exemplo_mensagem).pack(side=tk.RIGHT, padx=5)

    def _criar_frame_automacao(self, parent):
        auto_frame = ttk.LabelFrame(parent, text="Controle de Automação", padding="10")
        auto_frame.pack(fill=tk.X, pady=5)
        botoes_frame = ttk.Frame(auto_frame)
        botoes_frame.pack(fill=tk.X)
        self.btn_iniciar = ttk.Button(botoes_frame, text="Iniciar Automação Completa", command=self.iniciar_automacao, style="Accent.TButton")
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_parar = ttk.Button(botoes_frame, text="Parar Automação", command=self.parar_automacao, state="disabled")
        self.btn_parar.pack(side=tk.LEFT, padx=5)
        self.progress_var = tk.StringVar(value="Pronto para iniciar")
        ttk.Label(botoes_frame, textvariable=self.progress_var).pack(side=tk.RIGHT, padx=5)

    def _criar_frame_logs(self, parent):
        logs_frame = ttk.LabelFrame(parent, text="Logs do Sistema")
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        log_container = ttk.Frame(logs_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = tk.Text(log_container, height=12, width=70, state="disabled", wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(log_controls, text="Limpar Logs", command=self.limpar_logs).pack(side=tk.LEFT)
        ttk.Button(log_controls, text="Salvar Logs", command=self.salvar_logs).pack(side=tk.LEFT, padx=5)

    def __init__(self):
        super().__init__()
        # Configuração de logs
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        logging.basicConfig(
            level=logging.INFO,
            handlers=[self.queue_handler],
            format='%(message)s' # Simplificado para não duplicar timestamp
        )

        self.title("LinkedIn Automation Bot - Versão Otimizada")
        self.geometry("800x750") # Aumentada altura
        self.minsize(700, 600)

        # Temas
        self.style = ttk.Style(self)
        self.style.configure("Accent.TButton", foreground="white", background="#0078D7")


        # Variáveis de controle
        self.linkedin_bot = None
        self.automation_running = False
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


        self._criar_interface()
        self._carregar_configuracoes()

        # Processar fila de logs
        self.after(100, self.process_log_queue)

    def on_closing(self):
        """Trata fechamento da aplicação"""
        try:
            self._salvar_configuracoes()
            
            if hasattr(self, 'automation_running') and self.automation_running:
                self.automation_running = False
                time.sleep(1)
            
            if hasattr(self, 'linkedin_bot') and self.linkedin_bot:
                self.linkedin_bot.fechar()
            
            self.destroy()
        except Exception as e:
            # Não usar logging aqui, pois pode não funcionar durante o fechamento
            print(f"Erro ao fechar aplicação: {e}")
            self.destroy()