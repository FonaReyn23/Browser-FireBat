import sys
import os
from PyQt6 import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
import webbrowser


class DownloadManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер загрузок")
        self.setMinimumSize(600, 400)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.downloads_list = QListWidget()
        self.layout.addWidget(self.downloads_list)
        
        self.clear_button = QPushButton("Очистить список")
        self.clear_button.clicked.connect(self.clear_downloads)
        self.layout.addWidget(self.clear_button)
        
        self.downloads = []
    
    def add_download(self, download_item):
        item = QListWidgetItem()
        item.setText(f"{download_item.path().split('/')[-1]} - {self.format_size(download_item.totalBytes())}")
        item.setData(Qt.UserRole, download_item)
        self.downloads_list.addItem(item)
        self.downloads.append(download_item)
    
    def format_size(self, size):
        if size < 1024:
            return f"{size} Б"
        elif size < 1024*1024:
            return f"{size/1024:.1f} КБ"
        elif size < 1024*1024*1024:
            return f"{size/(1024*1024):.1f} МБ"
        else:
            return f"{size/(1024*1024*1024):.1f} ГБ"
    
    def clear_downloads(self):
        self.downloads_list.clear()
        self.downloads.clear()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(750,550)
        self.setGeometry(100, 100, 1024, 768)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://google.com"))
        self.setWindowIcon(QIcon("logo1.png"))

        #инициализация менеджера загрузок
        self.download_manager = DownloadManager()

        # Настройка вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Панель инструментов
        navtb = QToolBar()
        navtb.setMovable(False)
        navtb.setIconSize(QSize(24,24))
        navtb.setGeometry(200,200,200,200)
        self.addToolBar(navtb)

        # Контекстное меню
        self.setup_context_menu()
        
        # кнопки навигации

        back_btn = QAction("⇦", self)
        back_btn.setIcon(QIcon("icons/back_btn.png"))
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navtb.addAction(back_btn)
        

        next_btn = QAction("⇨", self)
        next_btn.setIcon(QIcon("icons/forward_btn.png"))
        next_btn.triggered.connect(lambda: self.current_browser().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction("↻", self)
        reload_btn.setIcon(QIcon("icons/reload_btn.png"))
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction("⌂", self)
        home_btn.setIcon(QIcon("icons/home_btn.png"))
        home_btn.triggered.connect(self.home_button)
        navtb.addAction(home_btn)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Введите url или поисковой запрос")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        self.show()

        # Кнопка новой вкладки
        new_tab_btn = QAction('+', self)
        new_tab_btn.setIcon(QIcon("icons/new_tab_btn.png"))
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(new_tab_btn)

        # Кнопка менеджера загрузок
        downloads_btn = QAction("↓", self)
        downloads_btn.setIcon(QIcon("icons/downloads_btn.png"))
        downloads_btn.triggered.connect(self.show_downloads)
        navtb.addAction(downloads_btn)

        self.setStyleSheet("""
            QWebEngineView {
                background-color: #191919;
                padding: 5px;   
                border-radius: 10px;      
            }
            QMainWindow {
                background-color: #1d1d1d;
                border-radius: 15px;
            }
            QToolBar {
                padding: 5px;
                background-color: #191919;
                border-bottom: 1px solid #333;
            }
            QLineEdit {
                padding: 2px;
                border-radius: 15px;
                border: 1px;
                height: 32px;
                color: #f5f5f5;
                background-color: rgb(64, 80, 110);
            }
            QLineEdit:hover {
                background-color: rgb(55, 69, 94);
            }
            QLineEdit:focus {
                background-color: #f5f5f5;
                color: #1a1a1a;
                border: 2px solid rgb(102,157,246);
            }
            QToolButton {
                min-width: 25px;
                padding: 6px;
                color: #f5f5f5;
                font-size: 16pt;
                border-radius: 15px;            }
            QToolButton:hover {
                background-color: rgb(42, 46, 48);
            }
            QTabBar {
                background: #1d1d1d;
                padding: 0px;
                margin-top: 50px;
            }
            QTabBar::tab {
                background: rgb(42, 46, 48);
                color: #fff;
                padding: 7px;
                width: 100px;
                border-radius: 11px;
                margin-top: 3px;
                margin-bottom: 5px;
                margin-right: 2px;
                margin-left: 2px;
            }
            QTabBar::tab:selected {
                background: rgb(57, 61, 64);
                border: 2px solid rgb(102,157,246);
            }
            QTabWidget::pane {
                border: none;
                top: -1px;
            }
""")
        
        # Добавить начальную вкладку
        self.add_new_tab(QUrl('https://www.google.com'), 'Главная')

    def setup_context_menu(self):
        self.menu = QMenu(self)

        actions = [
            ("Новая вкладка", self.add_new_tab, None),
            ("Закрыть вкладку", self.close_tab, None),
            ("Обновить", lambda: self.current_browser().reload(), None)
        ]

        for text, handler, shortcut in actions:
            action = QAction(text, self)
            action.triggered.connect(handler)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            self.menu.addAction(action)

    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Настройка загрузки файлов
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

        # Подключить сигналы
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, browser=browser: self.update_title(browser))
        
        # Добавить вкладку
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def current_browser(self):
        return self.tabs.currentWidget()

    def update_title(self, browser):
        index = self.tabs.indexOf(browser)
        title = browser.page().title()
        self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)
        self.setWindowTitle(f"{title} - FireBat")

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("https")
        self.current_browser().setUrl(q)

    def home_button(self):
        self.browser.setUrl(QUrl("https://google.com/"))

    def current_browser(self):
        return self.tabs.currentWidget()

    def update_urlbar(self, q, browser=None):
        if browser != self.current_browser():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    # downloads menu

    def handle_download(self, download):
        # Запрос пути для сохранения файла
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", 
            os.path.expanduser("~/Downloads/" + download.path().split('/')[-1]),
            "All Files (*)"
        )
        
        if path:
            download.setPath(path)
            download.accept()
            download.finished.connect(lambda: self.download_completed(download))
            self.download_manager.add_download(download)

    def download_completed(self, download):
        QMessageBox.information(self, "Загрузка завершена", 
                              f"Файл {download.path().split('/')[-1]} успешно загружен!")

    def show_downloads(self):
        self.download_manager.show()

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("logo1.png"))
window = MainWindow()
window.show()
sys.exit(app.exec_())
