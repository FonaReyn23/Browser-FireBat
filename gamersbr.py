import sys
import os
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import webbrowser

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumSize(750,550)
        self.setGeometry(100, 100, 1024, 768)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://google.com"))

        # Настройка вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Панель инструментов
        navtb = QToolBar()
        navtb.setMovable(False)
        self.addToolBar(navtb)

        # Контекстное меню
        self.setup_context_menu()
        
        # кнопки навигации

        back_btn = QAction("⇦", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navtb.addAction(back_btn)
        

        next_btn = QAction("⇨", self)
        next_btn.triggered.connect(lambda: self.current_browser().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction("⌂", self)
        home_btn.triggered.connect(self.home_button)
        navtb.addAction(home_btn)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Введите url или поисковой запрос")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)
        self.show()

        # Кнопка новой вкладки
        new_tab_btn = QAction('+', self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(new_tab_btn)

        self.setStyleSheet("""
            QWebEngineView {
                background-color: #191919;
                padding: 5px;         
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
                height: 28px;
            }
            QToolButton {
                background-color: rgb(42, 46, 48);
                border-radius: 15px;
                min-width: 25px;
                padding: 5px;
                border: 1px;
                color: #f5f5f5;
                font-size: 15pt;
            }
            QToolButton:hover {
                background: rgb(57, 61, 64);
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
                margin-top: 5px;
                margin-bottom: 5px;
                margin-right: 2px;
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

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("logo1.png"))
window = MainWindow()
window.show()
sys.exit(app.exec_())
