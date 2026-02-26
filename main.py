import sys
import os
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QStackedWidget, QGridLayout, QComboBox, 
                             QSlider, QProgressBar, QSizePolicy)
from PySide6.QtGui import QPixmap, QFont, QColor, QCursor, QLinearGradient, QPalette, QKeyEvent
from PySide6.QtCore import Qt, QTimer, Signal, QUrl, QSize, QPoint
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# --- CONFIGURAÇÕES DE DADOS E ASSETS ---

DB_NAME = "Animes.db"
LISTA_BANNER = ["Kaoru_Hana", "Your_Lie_In_April", "Horimiya"]
RECOMENDADOS = ["Kaoru_Hana", "Your_Lie_In_April", "Horimiya", "Spy_x_Family"]
LISTA_ANIMES = ["Jujutsu_Kaisen", "One_Piece", "You_And_I_Are_Polar_Opposites", "Frieren", "Spy_x_Family", "Horimiya", "Your_Lie_In_April", "Kaoru_Hana", "Love_Is_War"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "Assets")
ANIME_PATH = os.path.join(ASSETS_PATH, "Animes")
LOGO_PATH = os.path.join(ASSETS_PATH, "Logo.png")

# --- TELA DE CARREGAMENTO (SPLASH SCREEN) ---

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)
        
        self.layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #121212;
                color: white;
                border-radius: 15px;
                border: 1px solid #333;
            }
        """)
        self.layout.addWidget(self.container)
        
        self.inner_layout = QVBoxLayout(self.container)
        self.inner_layout.setAlignment(Qt.AlignCenter)
        
        self.label_title = QLabel()
        if os.path.exists(LOGO_PATH):
            pix_logo = QPixmap(LOGO_PATH).scaledToHeight(125, Qt.SmoothTransformation)
            self.label_title.setPixmap(pix_logo)
        else:
            self.label_title.setText("Ababahtomato")
            self.label_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FF6D1E;")
        
        self.inner_layout.addWidget(self.label_title, alignment=Qt.AlignCenter)

        self.label_subtitle = QLabel("Carregando...")
        self.label_subtitle.setStyleSheet("font-size: 14px; color: #888; border: none; margin-bottom: 20px;")
        self.inner_layout.addWidget(self.label_subtitle, alignment=Qt.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(400)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #222;
                color: transparent;
                border-radius: 5px;
                text-align: center;
                height: 10px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #FF6D1E;
                border-radius: 5px;
            }
        """)
        self.progress.setValue(0)
        self.inner_layout.addWidget(self.progress, alignment=Qt.AlignCenter)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(25)
        self.counter = 0

    def update_progress(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.main_window = InterfaceRoblox()
            self.main_window.show()
            self.close()

# --- FUNÇÕES DE BANCO DE DADOS ---

def inicializar_banco_dados():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS animes (folder_name TEXT PRIMARY KEY, display_name TEXT, banner_path TEXT, card_banner_path TEXT, language_state TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS seasons (id INTEGER PRIMARY KEY AUTOINCREMENT, anime_folder TEXT, season_number INTEGER, display_name TEXT, FOREIGN KEY(anime_folder) REFERENCES animes(folder_name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS episodes (id INTEGER PRIMARY KEY AUTOINCREMENT, season_id INTEGER, episode_number INTEGER, display_name TEXT, thumb_path TEXT, link_pt_dub TEXT, link_pt_sub TEXT, link_jp_dub TEXT, link_jp_sub TEXT, srt_pt TEXT, srt_en TEXT, FOREIGN KEY(season_id) REFERENCES seasons(id))''')
    conn.commit()
    conn.close()

def db_obter_info_anime(nome_pasta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT display_name, language_state FROM animes WHERE folder_name = ?", (nome_pasta,))
    res = cursor.fetchone()
    conn.close()
    if res: return {"DisplayName": res[0], "State": res[1]}
    return {"DisplayName": nome_pasta.replace("_", " "), "State": "Dub | Leg"}

def db_obter_temporadas(nome_pasta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, display_name FROM seasons WHERE anime_folder = ? ORDER BY season_number", (nome_pasta,))
    res = cursor.fetchall()
    conn.close()
    return res

def db_obter_episodios(season_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT display_name, link_pt_dub, link_pt_sub, link_jp_dub, link_jp_sub, srt_pt, srt_en FROM episodes WHERE season_id = ? ORDER BY episode_number", (season_id,))
    res = cursor.fetchall()
    conn.close()
    return res

# --- CLASSES AUXILIARES ---

class ClickableFrame(QFrame):
    clicked = Signal(str)
    def __init__(self, data_id, parent=None):
        super().__init__(parent)
        self.data_id = data_id
        self.setCursor(Qt.PointingHandCursor)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit(self.data_id)

class ClickableVideoWidget(QVideoWidget):
    clicked = Signal()
    double_clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.clicked.emit()
        super().mousePressEvent(event)
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton: self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

# --- INTERFACE PRINCIPAL ---

class InterfaceRoblox(QMainWindow):
    def __init__(self):
        self._initialized = False 
        super().__init__()
        inicializar_banco_dados()
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.video_duration = 0
        self.is_fullscreen_mode = False
        self.currentAnimeInBanner = 0 
        self.maxAnimes = len(LISTA_BANNER)

        self.construir_interface()
        
        self.setWindowTitle("Ababahtomato - Anime Stream")
        self.setStyleSheet("background-color: #000000; color: white; border: none;")
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        self._initialized = True 
        self.showFullScreen()
        QTimer.singleShot(100, self.posicionar_elementos_banner)
        
    def construir_interface(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()

        self.construir_topbar()
        self.main_layout.addWidget(self.stacked_widget)

        # Home
        self.page_home = QWidget()
        self.layout_home = QVBoxLayout(self.page_home)
        self.layout_home.setContentsMargins(0, 0, 0, 0)
        self.construir_homepage()
        self.stacked_widget.addWidget(self.page_home)

        # Anime
        self.page_anime = QWidget()
        self.layout_anime = QVBoxLayout(self.page_anime)
        self.layout_anime.setContentsMargins(0, 0, 0, 0)
        self.stacked_widget.addWidget(self.page_anime)

        # Player
        self.page_player = QWidget()
        self.layout_player = QVBoxLayout(self.page_player)
        self.layout_player.setContentsMargins(0, 0, 0, 0)
        self.stacked_widget.addWidget(self.page_player)
        
        # Dev
        self.page_dev = QWidget()
        self.layout_dev = QVBoxLayout(self.page_dev)
        self.construir_tela_desenvolvimento()
        self.stacked_widget.addWidget(self.page_dev)

    def construir_topbar(self):
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(80)
        self.top_bar.setStyleSheet("background-color: #121212;")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(30, 0, 30, 0)
        top_layout.setSpacing(25)

        self.logo_label = QLabel()
        if os.path.exists(LOGO_PATH):
            pix_logo = QPixmap(LOGO_PATH).scaledToHeight(60, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pix_logo)
        else:
            self.logo_label.setText("Ababahtomato")
            self.logo_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #FF6D1E;")
        
        self.logo_label.setCursor(Qt.PointingHandCursor)
        self.logo_label.mousePressEvent = lambda e: self.voltar_para_home()
        top_layout.addWidget(self.logo_label)

        btn_style = "QPushButton { background: transparent; color: #C8C8C8; font-size: 16px; font-weight: bold; padding: 10px; } QPushButton:hover { color: white; }"
        for txt in ["Novidades", "Simulcasts", "Categorias"]:
            btn = QPushButton(txt)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda: self.abrir_aba_dev())
            top_layout.addWidget(btn)

        top_layout.addStretch()
        self.main_layout.addWidget(self.top_bar)

    def voltar_para_home(self):
        self.media_player.stop()
        if self.is_fullscreen_mode: self.desativar_fullscreen()
        self.top_bar.show()
        self.stacked_widget.setCurrentWidget(self.page_home)

    def abrir_aba_dev(self):
        self.media_player.stop()
        if self.is_fullscreen_mode: self.desativar_fullscreen()
        self.top_bar.show()
        self.stacked_widget.setCurrentWidget(self.page_dev)

    def construir_tela_desenvolvimento(self):
        self.layout_dev.addStretch()
        icon_dev = QLabel("🛠️")
        icon_dev.setStyleSheet("font-size: 80px;")
        icon_dev.setAlignment(Qt.AlignCenter)
        self.layout_dev.addWidget(icon_dev)
        
        msg_title = QLabel("Função em Desenvolvimento")
        msg_title.setStyleSheet("font-size: 32px; font-weight: bold; color: #FF6D1E;")
        msg_title.setAlignment(Qt.AlignCenter)
        self.layout_dev.addWidget(msg_title)
        
        msg_sub = QLabel("Estamos a trabalhar nisso! Esta função será lançada em breve.")
        msg_sub.setStyleSheet("font-size: 18px; color: #C8C8C8;")
        msg_sub.setAlignment(Qt.AlignCenter)
        self.layout_dev.addWidget(msg_sub)
        
        btn_back = QPushButton("VOLTAR PARA HOME")
        btn_back.setFixedWidth(250)
        btn_back.setStyleSheet("QPushButton { background-color: #333; color: white; font-weight: bold; padding: 15px; border-radius: 5px; margin-top: 20px; } QPushButton:hover { background-color: #444; }")
        btn_back.clicked.connect(self.voltar_para_home)
        
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(btn_back)
        btn_container.addStretch()
        self.layout_dev.addLayout(btn_container)
        self.layout_dev.addStretch()

    def construir_homepage(self):
        self.scroll_area_home = QScrollArea()
        self.scroll_area_home.setWidgetResizable(True)
        self.scroll_area_home.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_home.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 40)
        self.content_layout.setSpacing(20) 

        self.banner_frame = QFrame()
        self.banner_frame.setFixedHeight(600)
        self.banner_frame.setStyleSheet("background: transparent;")
        
        self.banner_img_label = QLabel(self.banner_frame)
        self.banner_img_label.setAlignment(Qt.AlignCenter)
        self.banner_img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.banner_overlay = QFrame(self.banner_frame)
        self.banner_overlay.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(0,0,0,0), stop:0.6 rgba(0,0,0,0.4), stop:1 rgba(0,0,0,1));")
        
        self.banner_text_container = QWidget(self.banner_frame)
        self.banner_text_container.setStyleSheet("background: transparent;")
        self.banner_text_layout = QVBoxLayout(self.banner_text_container)
        self.banner_text_layout.setContentsMargins(50, 0, 50, 50)

        self.banner_title_label = QLabel("A carregar...")
        self.banner_title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")
        
        self.banner_info_label = QLabel("")
        self.banner_info_label.setStyleSheet("font-size: 16px; color: #CCCCCC;")
        
        self.btn_watch_banner = QPushButton("ASSISTIR AGORA")
        self.btn_watch_banner.setFixedWidth(200)
        self.btn_watch_banner.setStyleSheet("background-color: #FF6D1E; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
        self.btn_watch_banner.clicked.connect(lambda: self.abrir_tela_anime(LISTA_BANNER[self.currentAnimeInBanner]))

        self.banner_text_layout.addStretch()
        self.banner_text_layout.addWidget(self.banner_title_label)
        self.banner_text_layout.addWidget(self.banner_info_label)
        self.banner_text_layout.addWidget(self.btn_watch_banner)

        self.btn_left = QPushButton("<", self.banner_frame)
        self.btn_right = QPushButton(">", self.banner_frame)
        nav_style = "QPushButton { background: transparent; color: white; font-size: 40px; border: none; } QPushButton:hover { color: #FF6D1E; }"
        self.btn_left.setStyleSheet(nav_style)
        self.btn_right.setStyleSheet(nav_style)
        self.btn_left.setFixedSize(60, 100)
        self.btn_right.setFixedSize(60, 100)
        self.btn_left.clicked.connect(lambda: self.mudar_banner(-1))
        self.btn_right.clicked.connect(lambda: self.mudar_banner(1))

        self.content_layout.addWidget(self.banner_frame)

        rec_title = QLabel("Sugestões para ti")
        rec_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-left: 40px; margin-top: 10px;")
        self.content_layout.addWidget(rec_title)
        self.content_layout.addWidget(self.criar_fila_animes(RECOMENDADOS))

        disponiveis_title = QLabel("Animes Disponíveis")
        disponiveis_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-left: 40px; margin-top: 20px;")
        self.content_layout.addWidget(disponiveis_title)
        self.content_layout.addWidget(self.criar_fila_animes(LISTA_ANIMES))

        self.scroll_area_home.setWidget(self.content_container)
        self.layout_home.addWidget(self.scroll_area_home)
        
        QTimer.singleShot(200, self.atualizar_banner_visual)

    def criar_fila_animes(self, lista_nomes):
        area_scroll = QScrollArea()
        area_scroll.setFixedHeight(380)
        area_scroll.setWidgetResizable(True)
        area_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        area_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area_scroll.setStyleSheet("background: transparent; border: none;")
        
        container_fila = QWidget()
        layout_fila = QHBoxLayout(container_fila)
        layout_fila.setContentsMargins(40, 10, 40, 10)
        layout_fila.setSpacing(25)
        layout_fila.setSizeConstraint(QHBoxLayout.SetFixedSize)

        for pasta in lista_nomes:
            info = db_obter_info_anime(pasta)
            card = ClickableFrame(pasta)
            card.setFixedWidth(180)
            card.clicked.connect(self.abrir_tela_anime)
            
            card_v = QVBoxLayout(card)
            card_v.setContentsMargins(0,0,0,0)
            
            img = QLabel()
            img.setFixedSize(180, 260)
            img.setStyleSheet("background-color: #1A1A1A; border-radius: 8px;")
            
            v_path = os.path.join(ANIME_PATH, pasta, "VerticalBanner.png")
            if os.path.exists(v_path):
                img.setPixmap(QPixmap(v_path).scaled(180, 260, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            
            txt = QLabel(f"<b>{info['DisplayName']}</b><br><span style='color:#A0A0A0;'>{info['State']}</span>")
            txt.setWordWrap(True)
            txt.setStyleSheet("margin-top: 5px;")
            
            card_v.addWidget(img)
            card_v.addWidget(txt)
            layout_fila.addWidget(card)

        area_scroll.setWidget(container_fila)
        return area_scroll

    def abrir_tela_anime(self, nome_pasta):
        while self.layout_anime.count():
            item = self.layout_anime.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        info = db_obter_info_anime(nome_pasta)
        temporadas = db_obter_temporadas(nome_pasta)
        self.anime_page_container = QFrame()
        lay = QVBoxLayout(self.anime_page_container)
        lay.setContentsMargins(0, 0, 0, 0)

        # Imagem de fundo ajustável
        self.anime_bg_label = QLabel(self.anime_page_container)
        self.anime_bg_label.setGeometry(0, 0, self.width(), 600)
        h_path = os.path.join(ANIME_PATH, nome_pasta, "HorizontalBanner.png")
        self.current_anime_h_path = h_path
        if os.path.exists(h_path):
            self.anime_bg_label.setPixmap(QPixmap(h_path).scaled(self.width(), 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

        overlay = QFrame(self.anime_page_container)
        overlay.setGeometry(0, 0, self.width(), 600)
        overlay.setStyleSheet("background: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(0,0,0,0.3), stop:1 rgba(0,0,0,1));")

        scroll = QScrollArea(self.anime_page_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 300, 0, 40)
        
        info_container = QWidget()
        info_lay = QVBoxLayout(info_container)
        info_lay.setContentsMargins(50, 0, 50, 0)
        
        title = QLabel(info["DisplayName"])
        title.setStyleSheet("font-size: 42px; font-weight: bold;")
        info_lay.addWidget(title)

        header = QHBoxLayout()
        header.addWidget(QLabel("Episódios", styleSheet="font-size: 22px; font-weight: bold;"))
        header.addStretch()
        
        combo = QComboBox()
        for s_id, s_name in temporadas: combo.addItem(s_name, s_id)
        combo.setStyleSheet("background: #222; color: white; padding: 8px; border-radius: 5px; min-width: 160px;")
        combo.setVisible(len(temporadas) > 0)
        
        header.addWidget(combo)
        info_lay.addLayout(header)
        c_lay.addWidget(info_container)

        self.grid_wrapper = QWidget()
        self.grid_wrapper_lay = QVBoxLayout(self.grid_wrapper)
        self.grid_wrapper_lay.setContentsMargins(50, 20, 50, 0) 
        
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.no_episodes_label = QLabel("Nenhum episódio disponível.")
        self.no_episodes_label.setStyleSheet("font-size: 18px; color: #888; padding: 40px;")
        self.no_episodes_label.setAlignment(Qt.AlignCenter)
        self.no_episodes_label.setVisible(False)
        self.grid_wrapper_lay.addWidget(self.no_episodes_label)

        def carregar_episodios_ui():
            while self.grid_layout.count():
                w = self.grid_layout.takeAt(0).widget()
                if w: w.deleteLater()
            s_id = combo.currentData()
            eps = db_obter_episodios(s_id) if s_id is not None else []
            
            if not eps:
                self.no_episodes_label.setVisible(True)
                self.grid_container.setVisible(False)
            else:
                self.no_episodes_label.setVisible(False)
                self.grid_container.setVisible(True)
                
                # Definir largura fixa para evitar que o grid expanda além do container
                largura_disponivel = self.width() - 100 # 50 de cada lado
                num_colunas = max(1, largura_disponivel // 305) # 280 card + 25 spacing
                
                for i, ep_data in enumerate(eps):
                    card = ClickableFrame(ep_data[0])
                    card.setFixedSize(280, 210)
                    card.setStyleSheet("QFrame { background: #1A1A1A; border-radius: 10px; } QFrame:hover { background: #252525; }")
                    card.clicked.connect(lambda name, index=i, lista=eps: self.abrir_player_episodio(index, lista, info["DisplayName"], nome_pasta))
                    
                    v = QVBoxLayout(card)
                    v.setContentsMargins(0,0,0,0)
                    img_ep = QLabel()
                    img_ep.setFixedSize(280, 157)
                    img_ep.setStyleSheet("background: #333; border-top-left-radius: 10px; border-top-right-radius: 10px;")
                    if os.path.exists(h_path): 
                        img_ep.setPixmap(QPixmap(h_path).scaled(280, 157, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                    v.addWidget(img_ep)
                    lbl_ep = QLabel(f" {ep_data[0]}")
                    lbl_ep.setStyleSheet("padding: 10px; font-weight: bold;")
                    v.addWidget(lbl_ep)
                    
                    self.grid_layout.addWidget(card, i // num_colunas, i % num_colunas)
                
                # Stretch para alinhar à esquerda
                self.grid_layout.setColumnStretch(num_colunas, 1)

        self.recarregar_episodios = carregar_episodios_ui
        combo.currentIndexChanged.connect(carregar_episodios_ui)
        if temporadas: carregar_episodios_ui()
        else: self.no_episodes_label.setVisible(True)

        self.grid_wrapper_lay.addWidget(self.grid_container)
        c_lay.addWidget(self.grid_wrapper)
        c_lay.addStretch()
        
        scroll.setWidget(content)
        lay.addWidget(scroll)
        self.layout_anime.addWidget(self.anime_page_container)
        self.stacked_widget.setCurrentWidget(self.page_anime)

    def abrir_player_episodio(self, current_index, episodes_list, anime_name, folder_name):
        while self.layout_player.count():
            item = self.layout_player.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.scroll_player = QScrollArea()
        self.scroll_player.setWidgetResizable(True)
        self.scroll_player.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_player.setStyleSheet("background-color: transparent; border: none;")
        
        self.container_player = QWidget()
        self.p_lay = QVBoxLayout(self.container_player)
        self.p_lay.setContentsMargins(40, 20, 40, 40)
        self.p_lay.setSpacing(15)

        current_ep = episodes_list[current_index]
        ep_name = current_ep[0]
        links_disponiveis = {"Dublado (PT-BR)": current_ep[2], "Legendado (PT-BR)": current_ep[3], "Dublado (JP)": current_ep[4], "Original (JP)": current_ep[5]}
        opcoes_validas = {k: v for k, v in links_disponiveis.items() if v}
        video_link = list(opcoes_validas.values())[0] if opcoes_validas else None

        self.player_header_widget = QWidget()
        self.player_header = QHBoxLayout(self.player_header_widget)
        self.player_header.setContentsMargins(0,0,0,0)
        btn_back = QPushButton("⬅ VOLTAR")
        btn_back.setStyleSheet("background: #222; padding: 10px 20px; border-radius: 5px; font-weight: bold;")
        btn_back.clicked.connect(lambda: self.parar_e_voltar_anime())
        self.player_header.addWidget(btn_back)
        self.player_header.addStretch()
        ep_title = QLabel(f"<span style='color:#FF6D1E;'>{anime_name}</span> - {ep_name}")
        ep_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.player_header.addWidget(ep_title)
        self.p_lay.addWidget(self.player_header_widget)

        self.video_container_wrapper = QWidget()
        self.video_container_wrapper.setMinimumHeight(600)
        self.video_layout = QVBoxLayout(self.video_container_wrapper)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = ClickableVideoWidget()
        self.video_widget.setStyleSheet("background-color: black; border-radius: 10px;")
        self.video_widget.clicked.connect(self.toggle_playback)
        self.video_widget.double_clicked.connect(self.toggle_fullscreen)
        self.media_player.setVideoOutput(self.video_widget)
        self.video_layout.addWidget(self.video_widget)
        
        self.fs_controls_overlay = QFrame()
        self.fs_controls_overlay.setAttribute(Qt.WA_TranslucentBackground)
        self.fs_controls_overlay.setFixedHeight(60)
        
        self.fs_lay = QHBoxLayout(self.fs_controls_overlay)
        self.fs_lay.setContentsMargins(20, 0, 20, 0)
        self.fs_lay.setSpacing(15)
        
        shadow_style = "color: white; font-weight: bold; border: none; background: transparent; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);"
        
        self.btn_play_small = QPushButton("⏸")
        self.btn_play_small.setStyleSheet(f"font-size: 22px; {shadow_style}")
        self.btn_play_small.clicked.connect(self.toggle_playback)
        self.fs_lay.addWidget(self.btn_play_small)
        
        self.time_label_current = QLabel("00:00")
        self.time_label_current.setStyleSheet(shadow_style)
        self.fs_lay.addWidget(self.time_label_current)
        
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setStyleSheet("""
            QSlider::groove:horizontal { border: none; height: 6px; background: rgba(255,255,255,60); border-radius: 3px; } 
            QSlider::sub-page:horizontal { background: #FF6D1E; border-radius: 3px; } 
            QSlider::handle:horizontal { background: white; width: 14px; margin: -4px 0; border-radius: 7px; }
        """)
        self.time_slider.sliderMoved.connect(self.set_position)
        self.fs_lay.addWidget(self.time_slider)
        
        self.time_label_total = QLabel("00:00")
        self.time_label_total.setStyleSheet(shadow_style)
        self.fs_lay.addWidget(self.time_label_total)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal { border: none; height: 4px; background: rgba(255,255,255,40); }
            QSlider::handle:horizontal { background: #FF6D1E; width: 12px; margin: -4px 0; border-radius: 6px; }
        """)
        self.volume_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100))
        self.fs_lay.addWidget(self.volume_slider)
        
        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setStyleSheet(f"font-size: 20px; {shadow_style}")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.fs_lay.addWidget(self.btn_fullscreen)
        
        self.p_lay.addWidget(self.video_container_wrapper)
        self.p_lay.addWidget(self.fs_controls_overlay)

        self.player_controls_bottom_widget = QWidget()
        self.player_controls_bottom = QHBoxLayout(self.player_controls_bottom_widget)
        self.combo_audio = QComboBox()
        if opcoes_validas:
            for nome, link in opcoes_validas.items(): self.combo_audio.addItem(nome, link)
        self.combo_audio.currentIndexChanged.connect(lambda: self.mudar_faixa_video(self.combo_audio.currentData()))
        self.combo_audio.setStyleSheet("background: #222; color: white; padding: 5px 15px; border-radius: 5px;")
        self.player_controls_bottom.addWidget(self.combo_audio)
        self.player_controls_bottom.addStretch()
        self.p_lay.addWidget(self.player_controls_bottom_widget)

        if video_link:
            self.media_player.setSource(QUrl(video_link))
            self.media_player.play()
        
        self.nav_container_player_widget = QWidget()
        self.nav_container_player = QHBoxLayout(self.nav_container_player_widget)
        h_path = os.path.join(ANIME_PATH, folder_name, "HorizontalBanner.png")
        
        def criar_card_nav(index, text_prefix):
            ep_data = episodes_list[index]
            card = ClickableFrame(ep_data[0])
            card.setFixedSize(280, 210)
            card.setStyleSheet("QFrame { background: #1A1A1A; border-radius: 10px; }")
            card.clicked.connect(lambda _: self.abrir_player_episodio(index, episodes_list, anime_name, folder_name))
            v = QVBoxLayout(card)
            v.setContentsMargins(0,0,0,0)
            img_ep = QLabel()
            img_ep.setFixedSize(280, 157)
            if os.path.exists(h_path): img_ep.setPixmap(QPixmap(h_path).scaled(280, 157, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            v.addWidget(img_ep)
            lbl_ep = QLabel(f"<span style='color:#FF6D1E;'>{text_prefix}</span><br><b>{ep_data[0]}</b>")
            lbl_ep.setStyleSheet("padding: 8px;")
            v.addWidget(lbl_ep)
            return card

        if current_index > 0: self.nav_container_player.addWidget(criar_card_nav(current_index - 1, "ANTERIOR"))
        else: self.nav_container_player.addStretch()
        if current_index < len(episodes_list) - 1: self.nav_container_player.addWidget(criar_card_nav(current_index + 1, "PRÓXIMO"))
        else: self.nav_container_player.addStretch()
        self.p_lay.addWidget(self.nav_container_player_widget)

        self.scroll_player.setWidget(self.container_player)
        self.layout_player.addWidget(self.scroll_player)
        self.stacked_widget.setCurrentWidget(self.page_player)
        
        QTimer.singleShot(150, self.ajustar_controles_overlay)

    def ajustar_controles_overlay(self):
        if not hasattr(self, 'fs_controls_overlay') or not self.fs_controls_overlay: return

        if self.is_fullscreen_mode:
            self.fs_controls_overlay.setParent(self.video_widget)
            self.fs_controls_overlay.show()
            self.fs_controls_overlay.raise_()
            largura_ctrl = int(self.video_widget.width() * 0.8) 
            x = (self.video_widget.width() - largura_ctrl) // 2
            y = self.video_widget.height() - 100 
            self.fs_controls_overlay.setGeometry(x, y, largura_ctrl, 60)
            self.fs_controls_overlay.setStyleSheet("QFrame { background: transparent !important; border: none; }")
        else:
            if hasattr(self, 'p_lay') and hasattr(self, 'container_player'):
                self.fs_controls_overlay.setParent(self.container_player)
                self.p_lay.insertWidget(2, self.fs_controls_overlay)
                self.fs_controls_overlay.setFixedSize(self.container_player.width() - 80, 60)
                self.fs_controls_overlay.setStyleSheet("QFrame { background: #121212; border-radius: 10px; border: none; }")

    def toggle_fullscreen(self):
        if self.stacked_widget.currentWidget() != self.page_player: return
        if not self.is_fullscreen_mode: self.ativar_fullscreen()
        else: self.desativar_fullscreen()

    def ativar_fullscreen(self):
        self.is_fullscreen_mode = True
        self.top_bar.hide()
        self.player_header_widget.hide()
        self.player_controls_bottom_widget.hide()
        self.nav_container_player_widget.hide()
        self.scroll_player.setWidgetResizable(False)
        self.container_player.setFixedSize(self.size())
        self.p_lay.setContentsMargins(0, 0, 0, 0)
        self.video_container_wrapper.setFixedSize(self.size())
        self.video_widget.setStyleSheet("background-color: black; border-radius: 0px;")
        self.ajustar_controles_overlay()

    def desativar_fullscreen(self):
        self.is_fullscreen_mode = False
        self.top_bar.show()
        self.player_header_widget.show()
        self.player_controls_bottom_widget.show()
        self.nav_container_player_widget.show()
        self.scroll_player.setWidgetResizable(True)
        self.container_player.setMinimumSize(0,0)
        self.container_player.setMaximumSize(16777215, 16777215)
        self.p_lay.setContentsMargins(40, 20, 40, 40)
        self.video_container_wrapper.setMinimumHeight(600)
        self.video_container_wrapper.setMaximumSize(16777215, 16777215)
        self.video_widget.setStyleSheet("background-color: black; border-radius: 10px;")
        self.ajustar_controles_overlay()

    def position_changed(self, position):
        if hasattr(self, 'time_slider') and self.time_slider: self.time_slider.setValue(position)
        if hasattr(self, 'time_label_current') and self.time_label_current: self.time_label_current.setText(self.format_time(position))
    def duration_changed(self, duration):
        self.video_duration = duration
        if hasattr(self, 'time_slider') and self.time_slider: self.time_slider.setRange(0, duration)
        if hasattr(self, 'time_label_total') and self.time_label_total: self.time_label_total.setText(self.format_time(duration))
    def set_position(self, position): self.media_player.setPosition(position)
    def format_time(self, ms):
        s = round(ms / 1000); m, s = divmod(s, 60); h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
    
    def parar_e_voltar_anime(self): 
        self.media_player.stop()
        if self.is_fullscreen_mode: self.desativar_fullscreen()
        self.stacked_widget.setCurrentWidget(self.page_anime)
        
    def toggle_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause(); self.btn_play_small.setText("▶")
        else:
            self.media_player.play(); self.btn_play_small.setText("⏸")
            
    def mudar_faixa_video(self, novo_link):
        if novo_link:
            pos = self.media_player.position()
            self.media_player.setSource(QUrl(novo_link))
            self.media_player.play()
            QTimer.singleShot(500, lambda: self.media_player.setPosition(pos))
            
    def mudar_banner(self, d): self.currentAnimeInBanner = (self.currentAnimeInBanner + d) % self.maxAnimes; self.atualizar_banner_visual()
    
    def atualizar_banner_visual(self):
        if not hasattr(self, 'banner_img_label'): return
        largura = self.width()
        nome = LISTA_BANNER[self.currentAnimeInBanner]
        info = db_obter_info_anime(nome)
        path = os.path.join(ANIME_PATH, nome, "HorizontalBanner.png")
        if os.path.exists(path): self.banner_img_label.setPixmap(QPixmap(path).scaled(largura, 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.banner_overlay.setGeometry(0, 0, largura, 600)
        self.banner_text_container.setGeometry(0, 0, largura, 600)
        self.banner_title_label.setText(info["DisplayName"])
        self.banner_info_label.setText(info["State"])
        
    def posicionar_elementos_banner(self):
        if hasattr(self, 'banner_frame'):
            y = (self.banner_frame.height() // 2) - 50
            self.btn_left.move(10, y); self.btn_right.move(self.banner_frame.width() - 70, y)
            self.atualizar_banner_visual()
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_F:
            if self.stacked_widget.currentWidget() == self.page_player: self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen_mode: self.desativar_fullscreen()
            elif self.stacked_widget.currentWidget() == self.page_player: self.parar_e_voltar_anime()
            elif self.stacked_widget.currentWidget() == self.page_anime: self.voltar_para_home()
        elif event.key() == Qt.Key_Space:
             if self.stacked_widget.currentWidget() == self.page_player: self.toggle_playback()
        super().keyPressEvent(event)

    def resizeEvent(self, event): 
        if not hasattr(self, '_initialized') or not self._initialized:
            super().resizeEvent(event)
            return
            
        super().resizeEvent(event)
        
        # Reposicionar banner
        self.posicionar_elementos_banner()
        
        # Ajustar background da página de anime se estiver visível
        if self.stacked_widget.currentWidget() == self.page_anime and hasattr(self, 'anime_bg_label'):
            self.anime_bg_label.setGeometry(0, 0, self.width(), 600)
            if hasattr(self, 'current_anime_h_path') and os.path.exists(self.current_anime_h_path):
                self.anime_bg_label.setPixmap(QPixmap(self.current_anime_h_path).scaled(self.width(), 600, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            
            # Recalcular grid para caber na nova largura
            if hasattr(self, 'recarregar_episodios'):
                self.recarregar_episodios()

        # Ajustar controles do player
        if self.stacked_widget.currentWidget() == self.page_player:
            self.ajustar_controles_overlay()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec()) 
