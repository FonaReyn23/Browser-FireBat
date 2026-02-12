import sys
import os
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *


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


        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Настройка вкладок
        self.tabs = QTabBar()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.switch_tab)
        mainLayout.addWidget(self.tabs)
        
        
        # Панель инструментов
        navtb = QWidget()
        navlt = QHBoxLayout(navtb)
        mainLayout.addWidget(navtb)
        navlt.setContentsMargins(5, 5, 5, 5)
        # Контекстное меню
        self.setup_context_menu()
        
        # кнопки навигации

        # Кнопка "Назад"
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("back_btn.png"))
        back_btn.setToolTip("Назад")
        back_btn.clicked.connect(lambda: self.current_browser().back())
        navlt.addWidget(back_btn)

        # Кнопка "Вперёд"
        forward_btn = QPushButton()
        forward_btn.setIcon(QIcon("forward_btn.png"))
        forward_btn.setToolTip("Вперёд")
        forward_btn.clicked.connect(lambda: self.current_browser().forward())
        navlt.addWidget(forward_btn)

        # Кнопка "Обновить"
        reload_btn = QPushButton()
        reload_btn.setIcon(QIcon("reload_btn.png"))
        reload_btn.setToolTip("Обновить")
        reload_btn.clicked.connect(lambda: self.current_browser().reload())
        navlt.addWidget(reload_btn)

        # Кнопка "Домой"
        home_btn = QPushButton()
        home_btn.setIcon(QIcon("home_btn.png"))
        home_btn.setToolTip("Домашняя страница")
        home_btn.clicked.connect(self.home_button)
        navlt.addWidget(home_btn)

        # Строка URL
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Введите URL или поисковый запрос")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navlt.addWidget(self.urlbar)

        # Кнопка "Новая вкладка"
        new_tab_btn = QPushButton()
        new_tab_btn.setIcon(QIcon("new_tab_btn.png"))
        new_tab_btn.setToolTip("Новая вкладка")
        new_tab_btn.clicked.connect(self.add_new_tab)
        navlt.addWidget(new_tab_btn)

        # Кнопка "Загрузки"
        downloads_btn = QPushButton()
        downloads_btn.setIcon(QIcon("downloads_btn.png"))
        downloads_btn.setToolTip("Менеджер загрузок")
        downloads_btn.clicked.connect(self.show_downloads)
        navlt.addWidget(downloads_btn)

        # Кнопка "О программе"
        about_btn = QPushButton()
        about_btn.setIcon(QIcon("Frame 14.svg"))
        about_btn.setToolTip("О программе")
        about_btn.clicked.connect(self.abtProg)
        navlt.addWidget(about_btn)

         # 3. Стек страниц браузера
        self.stack = QStackedWidget()
        mainLayout.addWidget(self.stack)

        # --- Настройка профиля для загрузок (один раз) ---
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.handle_download)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1d1d1d;
            }
            QTabBar {
                background: #212121;
                qproperty-drawBase: 0;
                border-bottom: 1px solid #333;
            }
            QTabBar::tab {
                background: rgb(42, 46, 48);
                color: #fff;
                padding: 7px;
                width: 100px;
                border-radius: 15px;
            }
            QTabBar::tab:selected {
                background: rgb(57, 61, 64);
                border: 2px solid rgb(102,157,246);
            }
            QPushButton {
                min-width: 22px;
                min-height: 22px;
                padding: 6px;
                border-radius: 16px;
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgb(42, 46, 48);
            }
            QLineEdit {
                padding: 2px;
                border-radius: 16px;
                border: 1px solid #333;
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
            QStackedWidget {
                border: none;
            }
        """)

        self.setup_context_menu()
        
        # Добавить начальную вкладку
        self.add_new_tab(QUrl('https://www.google.com'), 'Главная')

    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')
        elif isinstance(qurl, bool):  # защита от случайного bool
            qurl = QUrl("https://www.google.com")
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Добавляем браузер в стек
        self.stack.addWidget(browser)

        # Подключаем сигналы браузера
        browser.urlChanged.connect(lambda url, b=browser: self.update_urlbar(url, b))
        browser.loadFinished.connect(lambda _, b=browser: self.update_title(b))

        #Сохранение вкладки в сам браузер
        tabIndex = self.tabs.addTab(label)
        self.tabs.setTabData(tabIndex, browser)
        
        # Добавить вкладку
        self.tabs.setCurrentIndex(tabIndex)
        self.stack.setCurrentWidget(browser)

    def close_tab(self, tab_index):
        """Закрывает вкладку по её индексу."""
        if self.tabs.count() > 1:
            browser = self.tabs.tabData(tab_index)
            self.stack.removeWidget(browser)
            browser.deleteLater()       # освобождаем память
            self.tabs.removeTab(tab_index)
        else:
            self.close()               # последняя вкладка – закрыть окно

    def switch_tab(self, tab_index):
        """Переключает стек при выборе другой вкладки."""
        browser = self.tabs.tabData(tab_index)
        if browser:
            self.stack.setCurrentWidget(browser)
            # Обновляем адресную строку
            self.urlbar.setText(browser.url().toString())
            self.urlbar.setCursorPosition(0)


    def current_browser(self):
        currentIdx = self.tabs.currentIndex()
        if currentIdx >= 0 :
            return self.tabs.tabData(currentIdx)
        return None

    def update_title(self, browser):
        """Обновляет заголовок вкладки и окна."""
        # Ищем, какой вкладке принадлежит этот браузер
        for tab_idx in range(self.tabs.count()):
            if self.tabs.tabData(tab_idx) is browser:
                title = browser.page().title()
                short_title = title[:15] + "..." if len(title) > 15 else title
                self.tabs.setTabText(tab_idx, short_title)
                self.setWindowTitle(f"{title} - FireBat")
                break

    def navigate_to_url(self):
        """Переход по URL из адресной строки."""
        url = self.urlbar.text().strip()
        if not url:
            return
        q = QUrl(url)
        if q.scheme() == "":
            q.setScheme("https")
        browser = self.current_browser()
        if browser:
            browser.setUrl(q)

    def home_button(self):
        """Переход на домашнюю страницу."""
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl("https://www.google.com/"))

    def update_urlbar(self, url, browser=None):
        """Обновляет текст в адресной строке при смене URL."""
        if browser != self.current_browser():
            return
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(0)

    def home_button(self):
        """Переход на домашнюю страницу."""
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl("https://www.google.com/"))

    def update_urlbar(self, url, browser=None):
        """Обновляет текст в адресной строке при смене URL."""
        if browser != self.current_browser():
            return
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(0)

    def setup_context_menu(self):
        self.menu = QMenu(self)
        actions = [
            ("Новая вкладка", self.add_new_tab, None),
            ("Закрыть вкладку", lambda: self.close_tab(self.tabs.currentIndex()), None),
            ("Обновить", lambda: self.current_browser().reload(), None)
        ]
        for text, handler, shortcut in actions:
            action = QAction(text, self)
            action.triggered.connect(handler)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            self.menu.addAction(action)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def abtProg(self):
        QMessageBox.about(self, "О программе", "\nВерсия 1.0\n\nСоздано на PyQt5")

    def handle_download(self, download):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo1.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
