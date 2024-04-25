
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
from prompt import prompt_text
import time


with open('secrets.txt', 'r') as file:
    api_key = file.read().strip()

print("API Key:", api_key)

if api_key is None:
    raise ValueError("API_KEY não está definida nas variáveis de ambiente.")
else:
    # Aqui continua o seu código para configurar a API, se a chave existir
    genai.configure(api_key=api_key)

# Inicializar o modelo
model = genai.GenerativeModel('gemini-pro')

st.title("Criador de Pautas")
pdf_file = st.file_uploader("Anexe os books:", type=["pdf"])
pautas_file = st.file_uploader("Anexe as pautas aqui:", type=["pdf"])
def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    
    Args:
    pdf_file (UploadedFile): The PDF file uploaded via Streamlit.
    
    Returns:
    str: The extracted text from the PDF.
    """
    document = fitz.open("pdf", pdf_file.read())  # open PDF from bytes
    text = ""
    for page in document:  # iterate through the pages
        text += page.get_text()
    return text

# Inicialize a variável `extracted_text` fora do bloco if
extracted_text = ""
pautas_text = ""
pautas = "" 
# Inicializa a lista de pautas no estado da sessão se ela ainda não existe
if 'pautas_list' not in st.session_state:
    st.session_state['pautas_list'] = []


# Campo de entrada de texto para digitar o nome do médico
medico = st.text_input("Digite o nome do médico:")
# Campo de entrada de texto para digitar uma nova pauta
new_pauta = st.text_input("Digite a pauta e pressione 'Adicionar Pauta'")

# Botão para adicionar a nova pauta à lista
if st.button('Adicionar Pauta'):
    if new_pauta:  # Verifica se a caixa de texto não está vazia
        # Adiciona a nova pauta à lista no estado da sessão
        st.session_state['pautas_list'].append(new_pauta)
        # Limpa o campo de entrada de texto
        st.text_input("Digite a pauta e pressione 'Adicionar Pauta'", value='', key='input')
    else:
        st.warning('Por favor, digite uma pauta antes de adicionar.')

# Mostra a lista atual de pautas
st.write("Pautas adicionadas:")
for i, pauta in enumerate(st.session_state['pautas_list'], start=1):
    st.write(f"{i}: {pauta}")


generated_pautas = ""
if st.button("Gerar Pautas sem book"):
    if prompt_text and medico:
        pautas_text = extract_text_from_pdf(pautas_file) 
        pautas = model.generate_content(f"pegues os nomes completos das pautas elas estao com a data ao lado para fazer post no instagram mande apenas os nomes das pautas como resposta: {pautas_text}")
        st.write(pautas.text)
        pautas_lines = pautas.text.strip().split("\n")
        st.write(pautas_lines)
        generated_pautas = ""
        progress_bar = st.progress(0)
        for i, pauta_line in enumerate(pautas_lines):
            generated_pautas = model.generate_content(f"@@@System: {prompt_text}@@@ o {medico} faça as pautas a seguir seguindo o layout padrão e coloca o nome da pauta completa no titulo sem alterar: {pauta_line}")
            st.divider()
            st.write(generated_pautas.text)
            progress_bar.progress((i + 1) / len(pautas_lines))
            time.sleep(1)  # Simulate some processing time
    else:
        st.error("Please upload both a PDF file and pautas file before generating pautas.")

if st.button("Gerar Pautas com book"):
    if prompt_text:
        pautas_text = extract_text_from_pdf(pautas_file)
        book_text = extract_text_from_pdf(pdf_file) 
        pautas = model.generate_content(f"pegues os nomes completos das pautas elas estao com a data ao lado para fazer post no instagram mande apenas os nomes das pautas como resposta: {pautas_text}")
        st.write(pautas.text)
        pautas_lines = pautas.text.strip().split("\n")
        generated_pautas = ""
        progress_bar = st.progress(0)
        for i, pauta_line in enumerate(pautas_lines):
            generated_pautas = model.generate_content(f"@@@System: {prompt_text}@@@ use as informacoes do medico a seguir: {book_text} e faça a pauta seguindo o layout padrão e coloca o nome da pauta completa no titulo sem alterar: {pauta_line}")
            st.divider()
            st.write(generated_pautas.text)
            progress_bar.progress((i + 1) / len(pautas_lines))
    else:
        st.error("Please upload both a PDF file and pautas file before generating pautas.")

# Botão para gerar pautas
if st.button("Gerar Pautas manuais"):
    # Verifica se a lista de pautas não está vazia
    if st.session_state['pautas_list']:
        # Aqui você pode processar cada pauta individualmente
        for pauta_line in st.session_state['pautas_list']:
            generated_pauta = f"@@@System: {prompt_text}@@@ faça a pauta para {medico} seguindo o layout padrão e coloque o nome da pauta completa no titulo sem alterar: {pauta_line}"
            # Suponha que model.generate_content() é uma função que você já tem
            generated_pautas = model.generate_content(generated_pauta)
            with st.spinner('Gerando pautas...'):
                st.write(generated_pautas.text)
    else:
        st.error("Por favor, adicione pelo menos uma pauta antes de gerar.")

# The function call is commented out to avoid accidental execution
# streamlit_pdf_extractor_app()
