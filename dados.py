import sqlite3
import os

# --- DICIONÁRIO CENTRAL DE DADOS ---
# Adicione novos animes seguindo esta estrutura.
MEUS_ANIMES = {
    "Kaoru_Hana": {
        "display_name": "Kaoru Hana wa Rin to Saku",
        "state": "Dublado",
        "temporadas": [
            {
                "numero": 1,
                "nome": "Temporada 1",
                "episodios": [
                    {
                        "numero": 1,
                        "titulo": "Rintaro e Kaoruko",
                        "audio": {
                            "pt_dub": "",
                            "pt_sub": "https://dl.springsfern.in/dl/AAAAAgqplHNFAUYEAAAGSA/dHyG899nxId8t72Tb_DPmVmUp8HfzIrpi6kRpFXWi_8",
                            "jp_dub": "",
                            "jp_sub": "",
                        },
                        "legendas": {
                            "pt": "",
                            "en": "",
                        }
                    },
                    {
                        "numero": 2,
                        "titulo": "Chidori e Kikyo",
                        "audio": {
                            "pt_dub": "https://dl.springsfern.in/dl/AAAAAgqplHNFAUYEAAAGSQ/xt2V5yQsniS2VI1ez-3UWHh87qcx7lWqNSXaodNd9rA",
                            "pt_sub": "https://dl.springsfern.in/dl/AAAAAgqplHNFAUYEAAAGSQ/xt2V5yQsniS2VI1ez-3UWHh87qcx7lWqNSXaodNd9rA",
                            "jp_dub": "",
                            "jp_sub": "",
                        },
                        "legendas": {
                            "pt": "",
                            "en": "",
                        }
                    },
                    {
                        "numero": 3,
                        "titulo": "Uma Pessoa Bondosa",
                        "audio": {
                            "pt_dub": "",
                            "pt_sub": "https://dl.springsfern.in/dl/AAAAAgqplHNFAUYEAAAGSg/SYkfwfp6SVJY5s0cbLqOn7Uf7X2DU8rwPj83D0y42i0",
                            "jp_dub": "",
                            "jp_sub": "",
                        },
                        "legendas": {
                            "pt": "",
                            "en": "",
                        }
                    }
                ]
            }
        ]
    },
}

def configurar_banco():
    conn = sqlite3.connect("Animes.db")
    cursor = conn.cursor()

    # Resetar tabelas para garantir que os novos dados entrem corretamente (opcional)
    cursor.execute("DROP TABLE IF EXISTS episodes")
    cursor.execute("DROP TABLE IF EXISTS seasons")
    cursor.execute("DROP TABLE IF EXISTS animes")

    # Criar tabelas com suporte a novos campos de áudio e legenda
    cursor.execute('''CREATE TABLE IF NOT EXISTS animes (
                        folder_name TEXT PRIMARY KEY, 
                        display_name TEXT, 
                        language_state TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS seasons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        anime_folder TEXT, 
                        season_number INTEGER, 
                        display_name TEXT, 
                        FOREIGN KEY(anime_folder) REFERENCES animes(folder_name))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS episodes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        season_id INTEGER, 
                        episode_number INTEGER, 
                        display_name TEXT, 
                        link_pt_dub TEXT, 
                        link_pt_sub TEXT, 
                        link_jp_dub TEXT, 
                        link_jp_sub TEXT,
                        srt_pt TEXT,
                        srt_en TEXT,
                        FOREIGN KEY(season_id) REFERENCES seasons(id))''')
    
    conn.commit()
    return conn

def popular_banco(conn):
    cursor = conn.cursor()
    
    for folder, dados in MEUS_ANIMES.items():
        # Inserir Anime
        cursor.execute("INSERT OR REPLACE INTO animes VALUES (?, ?, ?)", 
                       (folder, dados["display_name"], dados["state"]))
        
        for temp in dados["temporadas"]:
            # Inserir Temporada
            cursor.execute("INSERT INTO seasons (anime_folder, season_number, display_name) VALUES (?, ?, ?)",
                           (folder, temp["numero"], temp["nome"]))
            season_id = cursor.lastrowid
            
            for ep in temp["episodios"]:
                # Extrair links de áudio e legendas
                audio = ep.get("audio", {})
                srt = ep.get("legendas", {})
                
                cursor.execute('''INSERT INTO episodes 
                    (season_id, episode_number, display_name, 
                     link_pt_dub, link_pt_sub, link_jp_dub, link_jp_sub, 
                     srt_pt, srt_en) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (season_id, ep["numero"], f"Ep {ep['numero']} - {ep['titulo']}",
                     audio.get("pt_dub"), audio.get("pt_sub"), 
                     audio.get("jp_dub"), audio.get("jp_sub"),
                     srt.get("pt"), srt.get("en")))

    conn.commit()
    print("Banco de dados atualizado com sucesso!")

if __name__ == "__main__":
    db_conn = configurar_banco()
    popular_banco(db_conn)
    db_conn.close()