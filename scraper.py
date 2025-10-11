from bs4 import BeautifulSoup
import requests
import re
from unidecode import unidecode
import time
import random

def get_all_songs_from_artist(artist_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Acessando: {artist_url}")
        response = requests.get(artist_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # encontra o nome do artista para usar no padrao URL
        artist_name_in_url = artist_url.split('/')[-1]
        
        song_urls = []
        
        # 1. busca na sessao populares
        popular_section = soup.find('div', {'id': 'popularSongs'})
        if popular_section:
            song_links = popular_section.find_all('a', href=True)
            for link in song_links:
                href = link['href']
                if href.endswith('.html') and artist_name_in_url in href:
                    full_url = f"https://www.vagalume.com.br{href}"
                    if full_url not in song_urls:
                        song_urls.append(full_url)
        
        # 2. tenta encontrar em outras listas
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            # verifica se é do artista atual
            if (href.endswith('.html') and 
                href.startswith(f'/{artist_name_in_url}/') and
                not any(x in href for x in ['/discografia/', '/news/', '/popular/', '/related/'])):
                
                full_url = f"https://www.vagalume.com.br{href}"
                if full_url not in song_urls:
                    song_urls.append(full_url)
        
        # 3. se nao encontrou muitas musicas
        if len(song_urls) < 10:
            all_songs_url = f"{artist_url}/index.js"
            try:
                print(f"tentando acessar pagina completa: {all_songs_url}")
                response_all = requests.get(all_songs_url, headers=headers, timeout=15)
                if response_all.status_code == 200:
                    all_songs_soup = BeautifulSoup(response_all.content, "html.parser")
                    all_links_js = all_songs_soup.find_all('a', href=True)
                    
                    for link in all_links_js:
                        href = link['href']
                        if (href.endswith('.html') and 
                            href.startswith(f'/{artist_name_in_url}/') and
                            not any(x in href for x in ['/discografia/', '/news/', '/popular/', '/related/'])):
                            
                            full_url = f"https://www.vagalume.com.br{href}"
                            if full_url not in song_urls:
                                song_urls.append(full_url)
            except:
                pass  # se falahar, continua com que temos
        
        print(f"encontradas {len(song_urls)} musicas para o artista")
        return song_urls
        
    except Exception as e:
        print(f"erro ao buscar musicas do artista: {e}")
        return []

def get_lyrics_from_url(song_url):
    """extrai a letra da musica"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        time.sleep(random.uniform(1, 2))
        
        response = requests.get(song_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        lyrics_div = soup.find("div", {"id": "lyrics"})
        if lyrics_div:
            return lyrics_div.get_text(separator="\n", strip=True)
        
        lyrics_div = soup.find("div", {"class": "lyrics"})
        if lyrics_div:
            return lyrics_div.get_text(separator="\n", strip=True)
        
        return None
        
    except Exception as e:
        print(f"erro ao buscar letra de {song_url}: {e}")
        return None

def normalize_text(text):
    if not text:
        return ""
    
    text = unidecode(text.lower())
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text).strip()
    return text

def get_song_name_from_url(song_url):
    return song_url.split('/')[-1].replace('.html', '').replace('-', ' ').title()

def get_artist_name_from_url(artist_url):
    return artist_url.split('/')[-1].replace('-', ' ').title()

def process_artist(artist_url, output_file="corpus.txt"):
    artist_name = get_artist_name_from_url(artist_url)
    print(f"\n=== Processando artista: {artist_name} ===")
    
    song_urls = get_all_songs_from_artist(artist_url)
    
    if not song_urls:
        print(f"Nenhuma musica encontrada para {artist_name}")
        # tenta um metodo alternativo
        alternative_url = f"{artist_url}/musicas.html"
        print(f"Tentando URL alternativa: {alternative_url}")
        song_urls = get_all_songs_from_artist(alternative_url)
        
        if not song_urls:
            return
    
    print(f"encontradas {len(song_urls)} musicas. iniciando extracao...")
    
    successful_songs = 0
    # abrindo o arquivo e salvando no final
    with open(output_file, "a", encoding="utf-8") as f:
        for i, song_url in enumerate(song_urls, 1):
            print(f"[{i}/{len(song_urls)}] processando: {song_url}")
            
            # extrai a letra da musica
            lyrics = get_lyrics_from_url(song_url)
            
            if lyrics:
                # extrai o nome da musica do URL
                song_name = get_song_name_from_url(song_url)
                
                # normaliza o texto
                normalized_lyrics = normalize_text(lyrics)
                
                # f.write(f"{artist_name} - {song_name}\n")
                f.write(f"{normalized_lyrics}\n\n")
                f.flush()
                
                successful_songs += 1
                print(f"salvo: {song_name}")
            else:
                print(f"letra não encontrada")
            
            # Delay para não sobrecarregar o servidor
            time.sleep(random.uniform(1, 2))
    
    print(f"FEITO: {successful_songs}/{len(song_urls)} musicas processadas com sucesso para {artist_name}")

# Da para criar uma lista com os URLs de cada artista e iterar por ela


print("iniciando coleta de letras musicais...")
process_artist("https://www.vagalume.com.br/titas", "corpus_teste2.txt")
print("coleta concluida! Corpus salvo em 'corpus.txt'")