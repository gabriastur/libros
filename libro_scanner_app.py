import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

st.set_page_config(page_title="Radar de Libros", layout="wide")

st.title("📚 Radar de Libros con Valoración Alta y Precio Bajo")

st.markdown("Busca libros publicados desde 2020 con valoración alta (según OpenLibrary) y disponibles en Iberlibro por menos de un precio que tú elijas.")

# Filtros de usuario
año_min = st.slider("📆 Año de publicación mínimo", 2020, 2025, 2022)
precio_max = st.slider("💰 Precio máximo (EUR)", 1.0, 10.0, 3.0, 0.5)
limite_resultados = st.slider("🔍 Nº de libros a analizar (por año)", 10, 100, 30)

HEADERS = {"User-Agent": "Mozilla/5.0"}
UMBRAL_ESTRELLAS = 4.0

def obtener_libros_openlibrary(año, limite):
    url = f"https://openlibrary.org/search.json?publish_year={año}&language=eng&limit={limite}"
    r = requests.get(url)
    return r.json().get("docs", [])

def buscar_en_iberlibro(titulo, autor):
    query = f"{titulo} {autor}".replace(" ", "+")
    url = f"https://www.iberlibro.com/servlet/SearchResults?kn={query}&sortby=17"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    precios = soup.find_all("span", class_="item-price")
    for p in precios:
        texto = p.get_text(strip=True)
        if "€" in texto:
            try:
                valor = float(texto.replace("€", "").replace(",", "."))
                if valor <= precio_max:
                    return valor, url
            except:
                continue
    return None, None

resultados = []
with st.spinner("🔎 Buscando gangas literarias..."):
    for año in range(año_min, 2025):
        libros = obtener_libros_openlibrary(año, limite_resultados)
        for libro in libros:
            titulo = libro.get("title")
            autor = libro.get("author_name", [""])[0]
            if not titulo or not autor:
                continue
            precio, enlace = buscar_en_iberlibro(titulo, autor)
            if precio:
                resultados.append({
                    "📘 Título": titulo,
                    "✍️ Autor": autor,
                    "📆 Año": año,
                    "💵 Precio (€)": precio,
                    "🔗 Enlace": enlace
                })
            time.sleep(1.5)

if resultados:
    df = pd.DataFrame(resultados)
    st.success(f"✅ Se encontraron {len(resultados)} libros que cumplen los criterios")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar en CSV", data=csv, file_name='libros_baratos.csv', mime='text/csv')
else:
    st.warning("No se encontraron resultados que coincidan. ¡Prueba con un precio mayor o más años!")
