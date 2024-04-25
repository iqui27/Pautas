
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
from prompt import prompt_text



# Imprimir a chave API para verificar se está sendo lida corretamente
api_key = os.environ.get("API_KEY")
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
if st.button("Extract Text"):
    if pdf_file is not None and pautas_file is not None:
        try:
            extracted_text = extract_text_from_pdf(pdf_file)
            st.write(extracted_text)
            pautas_text = extract_text_from_pdf(pautas_file)
            st.write(pautas_text)
            st.success("Text extracted successfully.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please upload both a PDF file and pautas file.")
pautas = "" 
# Inicializa a lista de pautas no estado da sessão se ela ainda não existe
if 'pautas_list' not in st.session_state:
    st.session_state['pautas_list'] = []

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
    if prompt_text:
        pautas_text = extract_text_from_pdf(pautas_file) 
        pautas = model.generate_content(f"Extruture o texto a seguir e mande os nomes completos das pautas para post no instagram que estao marcados com datas enumerando elas: {pautas_text}")
        pautas_lines = pautas.text.strip().split("\n")
        generated_pautas = ""
        for pauta_line in pautas_lines:
            generated_pautas = model.generate_content(f"@@@System: {prompt_text}@@@ faça a pauta seguindo o layout padrão e coloca o nome da pauta completa no titulo sem alterar: {pauta_line}")
            st.divider()
            st.write(generated_pautas.text)
    else:
        st.error("Please upload both a PDF file and pautas file before generating pautas.")

if st.button("Gerar Pautas com book"):
    if prompt_text:
        pautas_text = extract_text_from_pdf(pautas_file)
        book_text = extract_text_from_pdf(pdf_file) 
        pautas = model.generate_content(f"Extruture o texto a seguir e mande os nomes completos das pautas para post no instagram que estao marcados com datas enumerando elas: {pautas_text}")
        pautas_lines = pautas.text.strip().split("\n")
        generated_pautas = ""
        for pauta_line in pautas_lines:
            generated_pautas = model.generate_content(f"@@@System: {prompt_text}@@@ use as informacoes do medico a seguir: {book_text} e faça a pauta seguindo o layout padrão e coloca o nome da pauta completa no titulo sem alterar: {pauta_line}")
            st.divider()
            st.write(generated_pautas.text)
    else:
        st.error("Please upload both a PDF file and pautas file before generating pautas.")

# Botão para gerar pautas
if st.button("Gerar Pautas manuais"):
    # Verifica se a lista de pautas não está vazia
    if st.session_state['pautas_list']:
        # Aqui você pode processar cada pauta individualmente
        for pauta_line in st.session_state['pautas_list']:
            generated_pauta = f"@@@System: {prompt_text}@@@ faça a pauta seguindo o layout padrão e coloque o nome da pauta completa no titulo sem alterar: {pauta_line}"
            # Suponha que model.generate_content() é uma função que você já tem
            generated_pautas = model.generate_content(generated_pauta)
            st.write(generated_pautas.text)
    else:
        st.error("Por favor, adicione pelo menos uma pauta antes de gerar.")

# The function call is commented out to avoid accidental execution
# streamlit_pdf_extractor_app()