import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# Configurações de UI
st.set_page_config(page_title="Scraper Mystery Books", page_icon="📚")
st.title("📚 Book Scraper - Categoria Mystery")
st.markdown("Este robô extrai dados do site *Books to Scrape* para o processo seletivo GAM.")

# Constantes
EXCHANGE_RATE = 7.00 

def convert_rating(star_text):
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return ratings.get(star_text, 0)

def scrape_mystery_books():
    books_data = []
    page_url = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
    
    # Barra de progresso visual
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while page_url:
        status_text.text(f"Extraindo: {page_url.split('/')[-1]}")
        response = requests.get(page_url)
        if response.status_code != 200: break
        
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            try:
                title = book.h3.a["title"]
                price_text = book.find("p", class_="price_color").text
                price = float(price_text.replace("£", "").replace("Â", "").strip())
                availability = book.find("p", class_="instock availability").text.strip()
                rating_class = book.find("p", class_="star-rating")["class"][1]
                rating = convert_rating(rating_class)
                
                books_data.append({
                    "Título": title,
                    "Preço (GBP)": price,
                    "Preço (BRL)": price * EXCHANGE_RATE,
                    "Disponibilidade": availability,
                    "Avaliação (Estrelas)": rating
                })
            except Exception as e:
                continue

        next_button = soup.find("li", class_="next")
        if next_button:
            next_page = next_button.a["href"]
            page_url = "https://books.toscrape.com/catalogue/category/books/mystery_3/" + next_page
        else:
            page_url = None
            
    progress_bar.progress(100)
    status_text.text("Extração concluída!")
    return books_data

# Interface do Botão
if st.button('🚀 Iniciar Extração de Dados'):
    try:
        with st.spinner('O robô está trabalhando nas páginas...'):
            dados = scrape_mystery_books()
            
            if dados:
                df = pd.DataFrame(dados)
                st.success(f"✅ Sucesso! Encontrados {len(df)} livros.")
                
                # Mostra uma prévia dos dados
                st.dataframe(df.head(10)) 

                # Gerar o Excel na memória
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='MysteryBooks')
                
                st.download_button(
                    label="📥 Baixar Planilha Completa (Excel)",
                    data=output.getvalue(),
                    file_name="mystery_books_GAM.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("Nenhum dado foi encontrado. Verifique a conexão com o site alvo.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")