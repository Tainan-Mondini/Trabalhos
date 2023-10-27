import tkinter as tk
import random
from tkinter import ttk, messagebox
import sqlite3
import time
import threading

# Função para criar a tabela no banco de dados se não existir
def create_table():
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            sexo TEXT,
            idade INTEGER,
            cidade TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vital_signs (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            heart_rate INTEGER,
            blood_pressure_sys INTEGER,
            blood_pressure_dia INTEGER,
            temperature REAL,
            oxygen_saturation INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Função para adicionar um novo paciente ao banco de dados
def add_patient():
    nome = nome_entry.get()
    sexo = sexo_var.get()
    idade = idade_entry.get()
    cidade = cidade_entry.get()

    if nome and sexo and idade and cidade:
        conn = sqlite3.connect('patients.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO patients (nome, sexo, idade, cidade) VALUES (?, ?, ?, ?)', (nome, sexo, idade, cidade))
        conn.commit()
        conn.close()

        update_patient_list()
        clear_entries()

# Função para atualizar a lista de pacientes a partir do banco de dados
def update_patient_list():
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome FROM patients')
    patient_data = cursor.fetchall()
    conn.close()

    lista_pacientes.delete(0, tk.END)
    for paciente in patient_data:
        lista_pacientes.insert(tk.END, paciente[0])

# Função para limpar os campos de entrada após adicionar um paciente
def clear_entries():
    nome_entry.delete(0, tk.END)
    idade_entry.delete(0, tk.END)
    cidade_entry.delete(0, tk.END)

# Função para pesquisar pacientes por nome na aba de consulta
def search_patients():
    search_query = search_entry.get().strip()
    if search_query:
        conn = sqlite3.connect('patients.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM patients WHERE nome LIKE ?', (f'%{search_query}%',))
        search_results = cursor.fetchall()
        conn.close()

        lista_pacientes.delete(0, tk.END)
        for paciente in search_results:
            lista_pacientes.insert(tk.END, paciente[0])


# Função pra gerar sinais vitais aleatórios
def generate_random_vital_signs():
    vital_signs = {
        'blood_pressure_sys': random.randint(100, 140),
        'blood_pressure_dia': random.randint(60, 90),
        'heart_rate': random.randint(60, 100),
        'temperature': round(random.uniform(36.0, 38.0), 1),
        'oxygen_saturation': random.randint(95, 100)
    }
    return vital_signs

# Função pra exibir um pop-up de anomalia
def show_anomaly_popup(paciente, sinal_vital, mensagem):
    messagebox.showwarning(f"Anomalia nos Sinais Vitais - {paciente}", f"O paciente {paciente} apresenta uma anomalia no sinal vital {sinal_vital}:\n{mensagem}")

# Função pra iniciar a verificação de anomalias
def start_anomaly_check():
    while True:
        conn = sqlite3.connect('patients.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nome, idade, sexo FROM patients')
        patient_data = cursor.fetchall()
        conn.close()

        for nome, idade, sexo in patient_data:
            vital_signs = generate_random_vital_signs()

            # Verificar a pressão arterial
            limites_pressao_arterial = {
                "Feminino": {
                    "19-24": (120, 79),
                    "25-29": (120, 80),
                    "30-35": (122, 81),
                    "36-39": (123, 82),
                    "40-45": (124, 83),
                    "46-49": (124, 83),
                    "50-55": (129, 85),
                    "56-59": (130, 86),
                    "60+": (134, 84),
                },
                "Masculino": {
                    "19-24": (120, 79),
                    "25-29": (121, 80),
                    "30-35": (123, 82),
                    "36-39": (124, 83),
                    "40-45": (125, 83),
                    "46-49": (127, 84),
                    "50-55": (128, 85),
                    "56-59": (131, 87),
                    "60+": (135, 88),
                }
            }

            # Verificar a frequência cardíaca
            limites_frequencia_cardiaca = {
                "Feminino": {
                    "0-1": (100, 160),
                    "1-10": (70, 120),
                    "10+": (60, 100),
                },
                "Masculino": {
                    "0-1": (100, 160),
                    "1-10": (70, 120),
                    "10+": (60, 100),
                },
            }

            # Verificar a temperatura
            limites_temperatura = (36.1, 37.2)

            # Verificar a saturação de oxigênio
            limites_saturacao_oxigenio = (95, 100)

            

            if (
                sexo in limites_pressao_arterial and idade in limites_pressao_arterial[sexo]
                and (
                    vital_signs['blood_pressure_sys'] < limites_pressao_arterial[sexo][idade][0]
                    or vital_signs['blood_pressure_dia'] < limites_pressao_arterial[sexo][idade][1]
                )
            ):
                show_anomaly_popup(nome, 'Pressão Arterial', "Variação anormal na pressão arterial")

            if (
                sexo in limites_frequencia_cardiaca and idade in limites_frequencia_cardiaca[sexo]
                and (
                    vital_signs['heart_rate'] < limites_frequencia_cardiaca[sexo][idade][0]
                    or vital_signs['heart_rate'] > limites_frequencia_cardiaca[sexo][idade][1]
                )
            ):
                show_anomaly_popup(nome, 'Frequência Cardíaca', "Variação anormal na frequência cardíaca")

            if (
                vital_signs['temperature'] < limites_temperatura[0]
                or vital_signs['temperature'] > limites_temperatura[1]
            ):
                show_anomaly_popup(nome, 'Temperatura Corporal', "Variação anormal na temperatura corporal")

            if (
                vital_signs['oxygen_saturation'] < limites_saturacao_oxigenio[0]
                or vital_signs['oxygen_saturation'] > limites_saturacao_oxigenio[1]
            ):
                show_anomaly_popup(nome, 'Saturação de Oxigênio', "Variação anormal na saturação de oxigênio")

        time.sleep(60)

# Função para criar uma nova linha pra verificar anomalias
def start_anomaly_check_thread():
    anomaly_check_thread = threading.Thread(target=start_anomaly_check)
    anomaly_check_thread.daemon = True
    anomaly_check_thread.start()

# Função para exibir as informações do paciente na aba de consulta
def show_patient_info():
    selected_patient = lista_pacientes.get(tk.ACTIVE)
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome, sexo, idade, cidade FROM patients WHERE nome = ?', (selected_patient,))
    patient_data = cursor.fetchone()

    if patient_data:
        nome, sexo, idade, cidade = patient_data
        paciente_info_label.config(
            text=f"Nome: {nome}\nSexo: {sexo}\nIdade: {idade} anos\nCidade: {cidade}")

        # Recuperar os sinais vitais do paciente
        cursor.execute('SELECT heart_rate, blood_pressure_sys, blood_pressure_dia, temperature, oxygen_saturation FROM vital_signs WHERE patient_name = ?', (selected_patient,))
        vital_signs_data = cursor.fetchone()

        if vital_signs_data:
            heart_rate, blood_pressure_sys, blood_pressure_dia, temperature, oxygen_saturation = vital_signs_data
            paciente_info_label.config(paciente_info_label.cget("text") +
                f"\n\nFrequência Cardíaca: {heart_rate} bpm\nPressão Arterial: {blood_pressure_sys}/{blood_pressure_dia} mmHg\nTemperatura Corporal: {temperature} °C\nSaturação de Oxigênio: {oxygen_saturation}%")
        else:
            paciente_info_label.config(paciente_info_label.cget("text") + "\n\nDados de Sinais Vitais não encontrados.")
    else:
        paciente_info_label.config(text="Paciente não encontrado.")

# Função para pesquisar pacientes por nome na aba de verificação
def search_patients_verification():
    search_query = search_entry_verification.get().strip()
    if search_query:
        conn = sqlite3.connect('patients.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM patients WHERE nome LIKE ?', (f'%{search_query}%',))
        search_results = cursor.fetchall()
        conn.close()

        lista_pacientes_verification.delete(0, tk.END)
        for paciente in search_results:
            lista_pacientes_verification.insert(tk.END, paciente[0])

# Função para exibir as informações do paciente na aba de verificação
def show_patient_info_verification():
    selected_patient = lista_pacientes_verification.get(tk.ACTIVE)  # Obtém o paciente selecionado na lista da aba de verificação
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nome, sexo, idade, cidade FROM patients WHERE nome = ?', (selected_patient,))
    patient_data = cursor.fetchone()

    if patient_data:
        nome, sexo, idade, cidade = patient_data
        paciente_info_label_verification.config(
            text=f"Nome: {nome}\nSexo: {sexo}\nIdade: {idade} anos\nCidade: {cidade}")

        # Recupere os sinais vitais do paciente
        cursor.execute('SELECT heart_rate, blood_pressure_sys, blood_pressure_dia, temperature, oxygen_saturation FROM vital_signs WHERE patient_name = ?', (selected_patient,))
        vital_signs_data = cursor.fetchone()

        if vital_signs_data:
            heart_rate, blood_pressure_sys, blood_pressure_dia, temperature, oxygen_saturation = vital_signs_data

            paciente_info_label_verification.config(paciente_info_label_verification.cget("text") +
                f"\n\nFrequência Cardíaca: {heart_rate} bpm\nPressão Arterial: {blood_pressure_sys}/{blood_pressure_dia} mmHg\nTemperatura Corporal: {temperature} °C\nSaturação de Oxigênio: {oxygen_saturation}%")

            # Atualize os rótulos de sinais vitais
            heart_rate_label_verification.config(text=f"Frequência Cardíaca: {heart_rate} bpm")
            blood_pressure_label_verification.config(text=f"Pressão Arterial: {blood_pressure_sys}/{blood_pressure_dia} mmHg")
            temperature_label_verification.config(text=f"Temperatura Corporal: {temperature} °C")
            oxygen_saturation_label_verification.config(text=f"Saturação de Oxigênio: {oxygen_saturation}%")
        else:
            # Se os dados de sinais vitais não forem encontrados, limpe os rótulos
            heart_rate_label_verification.config(text="Frequência Cardíaca: ")
            blood_pressure_label_verification.config(text="Pressão Arterial: ")
            temperature_label_verification.config(text="Temperatura Corporal: ")
            oxygen_saturation_label_verification.config(text="Saturação de Oxigênio: ")
    else:
        paciente_info_label_verification.config(text="Paciente não encontrado.")

# Configuração da janela principal
root = tk.Tk()
root.title("Cadastro e Consulta de Pacientes")

# Cria a tabela no banco de dados se não existir
create_table()

# Cria as abas para cadastro, consulta e verificação de pacientes usando ttk.Notebook
tab_control = ttk.Notebook(root)

# Aba de cadastro de pacientes
cadastro_tab = ttk.Frame(tab_control)
tab_control.add(cadastro_tab, text="Cadastro")

# Aba de consulta de pacientes
consulta_tab = ttk.Frame(tab_control)
tab_control.add(consulta_tab, text="Consulta")

# Aba de verificação de pacientes
verification_tab = ttk.Frame(tab_control)
tab_control.add(verification_tab, text="Verificação")

tab_control.pack(expand=1, fill="both")

# Widgets da aba de cadastro
nome_label = tk.Label(cadastro_tab, text="Nome do Paciente")
nome_label.grid(row=0, column=0, padx=10, pady=10)
nome_entry = tk.Entry(cadastro_tab)
nome_entry.grid(row=0, column=1, padx=10, pady=10)

sexo_label = tk.Label(cadastro_tab, text="Sexo")
sexo_label.grid(row=1, column=0, padx=10, pady=10)
sexo_var = tk.StringVar()
sexo_var.set("Masculino")
sexo_menu = ttk.Combobox(cadastro_tab, textvariable=sexo_var, values=["Masculino", "Feminino"])
sexo_menu.grid(row=1, column=1, padx=10, pady=10)

idade_label = tk.Label(cadastro_tab, text="Idade")
idade_label.grid(row=2, column=0, padx=10, pady=10)
idade_entry = tk.Entry(cadastro_tab)
idade_entry.grid(row=2, column=1, padx=10, pady=10)

cidade_label = tk.Label(cadastro_tab, text="Cidade")
cidade_label.grid(row=3, column=0, padx=10, pady=10)
cidade_entry = tk.Entry(cadastro_tab)
cidade_entry.grid(row=3, column=1, padx=10, pady=10)

add_button = tk.Button(cadastro_tab, text="Adicionar Paciente", command=add_patient)
add_button.grid(row=4, columnspan=2, padx=10, pady=10)

# Widgets da aba de consulta
search_label = tk.Label(consulta_tab, text="Pesquisar por Nome")
search_label.grid(row=0, column=0, padx=10, pady=10)
search_entry = tk.Entry(consulta_tab)
search_entry.grid(row=0, column=1, padx=10, pady=10)
search_button = tk.Button(consulta_tab, text="Pesquisar", command=search_patients)
search_button.grid(row=0, column=2, padx=10, pady=10)

lista_pacientes = tk.Listbox(consulta_tab, width=40, height=10)
lista_pacientes.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
lista_pacientes.bind('<<ListboxSelect>>', lambda event: show_patient_info())

paciente_info_label = tk.Label(consulta_tab, text="", justify="left")
paciente_info_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Widgets da aba de verificação
search_label_verification = tk.Label(verification_tab, text="Pesquisar por Nome")
search_label_verification.grid(row=0, column=0, padx=10, pady=10)
search_entry_verification = tk.Entry(verification_tab)
search_entry_verification.grid(row=0, column=1, padx=10, pady=10)
search_button_verification = tk.Button(verification_tab, text="Pesquisar", command=search_patients_verification)
search_button_verification.grid(row=0, column=2, padx=10, pady=10)

lista_pacientes_verification = tk.Listbox(verification_tab, width=40, height=10)
lista_pacientes_verification.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
lista_pacientes_verification.bind('<<ListboxSelect>>', lambda event: show_patient_info_verification())

paciente_info_label_verification = tk.Label(verification_tab, text="", justify="left")
paciente_info_label_verification.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Adiciona os rótulos de sinais vitais na aba de verificação
heart_rate_label_verification = tk.Label(verification_tab, text="Frequência Cardíaca: ", justify="left")
heart_rate_label_verification.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

blood_pressure_label_verification = tk.Label(verification_tab, text="Pressão Arterial: ", justify="left")
blood_pressure_label_verification.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

temperature_label_verification = tk.Label(verification_tab, text="Temperatura Corporal: ", justify="left")
temperature_label_verification.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

oxygen_saturation_label_verification = tk.Label(verification_tab, text="Saturação de Oxigênio: ", justify="left")
oxygen_saturation_label_verification.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# Inicie a verificação de anomalias em uma thread separada
start_anomaly_check_thread()

root.mainloop()
