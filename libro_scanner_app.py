import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

BASE_GOODREADS = "https://www.goodreads.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
AÑOS = range(2020, 2025)
PRECIO_MAX = 3.0
PAGINAS_POR_AÑO = 2  # Puedes aumentar esto para más resultados
UMBRAL_VALORACION = 4.0

def obtener_libros_goodreads(año):
    libros = []
    for pagina in range(1, PAGINAS_POR_AÑO + 1):
        url = f"{BASE_GOODREADS}/book/popular_by_date/{año}?page={pagina}"
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        contenedores = soup.select("div.leftContainer div.bookBox")

        if not contenedores:
            contenedores = soup.select("tr")  # fallback para diseño viejo

        for cont in contenedores:
            try:
                titulo = cont.find("a", class_="bookTitle").get_text(strip=True)
                autor = cont.find("a", class_="authorName").get_text(strip=True)
                valoracion = float(cont.select_one(".minirating").get_text().split("avg rating")[1].split()[0])
                enlace = BASE_GOODREADS + cont.find("a", class_="bookTitle")["href"]
                if valoracion >= UMBRAL_VALORACION:
                    libros.append({"titulo": titulo, "autor": autor, "valoracion": valoracion, "enlace": enlace, "año": año})
            except:
                continue
        time.sleep(2)
    return libros

def buscar_precio_iberlibro(titulo, autor):
    query = f"{titulo} {autor}".replace(" ", "+")
    url = f"https://www.iberlibro.com/servlet/SearchResults?kn={query}&sortby=17"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        precios = soup.find_all("span", class_="item-price")
        for p in precios:
            texto = p.get_text(strip=True)
            if "€" in texto:
                valor = float(texto.replace("€", "").replace(",", "."))
                if valor <= PRECIO_MAX:
                    return valor, url
    except:
        pass
    return None, None

def main():
    resultados = []
    for año in AÑOS:
        print(f"📘 Buscando libros de {año}...")
        libros = obtener_libros_goodreads(año)
        for libro in libros:
            precio, enlace_iberlibro = buscar_precio_iberlibro(libro["titulo"], libro["autor"])
            if precio:
                resultados.append({
                    "Título": libro["titulo"],
                    "Autor": libro["autor"],
                    "Año": libro["año"],
                    "Valoración": libro["valoracion"],
                    "Precio (€)": precio,
                    "Link Goodreads": libro["enlace"],
                    "Link Iberlibro": enlace_iberlibro
                })
            time.sleep(1.5)

    if resultados:
        df = pd.DataFrame(resultados)
        df.to_excel("libros_encontrados.xlsx", index=False)
        print(f"\n✅ ¡Hecho! Se encontraron {len(resultados)} libros. Archivo guardado como 'libros_encontrados.xlsx'")
    else:
        print("❌ No se encontraron libros que cumplan todos los criterios.")

if __name__ == "__main__":
    main()

