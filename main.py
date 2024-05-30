from PyQt6.QtGui import QCloseEvent, QMouseEvent
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import urllib.request
import time
import sys


class TubeBot():
    def __init__(self, parent= None):
        self.driver = None
        self.parent = parent

    def getPage(self):
        if self.driver is not None:
            self.driver.quit()
        self.driver = webdriver.Chrome()
        self.driver.get('https://www.youtube.com')
        self.driver.implicitly_wait(10)
        # wait for #text-container to exist
        WebDriverWait(self.driver, 7).until(EC.visibility_of_element_located((By.ID, "text-container")))
        time.sleep(5)
        try:
            searchBox = self.driver.find_element(By.NAME, "search_query")
            print("Found search_query")
        except NoSuchElementException:
            print("NoSuchElementException Occured")
        try:
            # first input attempt does notiong for some reason.
            searchBox.clear()
            searchBox.send_keys("\n")
            print("Sended Keys")
        except ElementNotInteractableException:
            print("Not Interactable Exception occured.")

    def search(self):  # TODO: NoSuchWindowException: Message: no such window: target window already closed
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
        except WebDriverException:
            self.getPage()
        try:
            searchBox = self.driver.find_element(By.NAME, "search_query")
            print("Found search_query")
        except NoSuchElementException:
            print("NoSuchElementException Occured")
        try:
            searchBox.clear()
            search_word = self.parent.search_word.text().replace('\n', ' ')
            searchBox.send_keys(search_word + '\n')
            print("Sended Keys")
        except ElementNotInteractableException:
            print("Not Interactable Exception occured.")
        # wait for search results to be loaded
        try:
            try:
                WebDriverWait(self.driver, 2).until_not(EC.presence_of_element_located((By.ID, 'contents')))
            except TimeoutException:
                print('Timeout on until-not-exist')
            WebDriverWait(self.driver, 7).until(EC.presence_of_element_located((By.ID, 'contents')))
            contents = self.driver.find_elements(By.CSS_SELECTOR, '#contents > ytd-video-renderer:nth-of-type(n) > div:nth-of-type(1)')
            print(f'contents count: {len(contents)}')
            WebDriverWait(self.driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'yt-core-image--loaded')))
            time.sleep(1)
            # 무한 스크롤 상태에 빠질 가능성을 방지하기 위한 PAGE_DOWN 50회 제한
            scroll_limit = 50
            for content in contents:
                try:
                    # Video Title
                    title = content.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1) > div:nth-of-type(1) > div > h3 > a').get_attribute('title')
                    # Video Link
                    link = content.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1) > div:nth-of-type(1) > div > h3 > a').get_attribute('href')
                    # Channel Name
                    uploader = content.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1) > div:nth-of-type(2) > ytd-channel-name > div > div > yt-formatted-string > a').text
                    # Thumbnail
                    thumbnail = content.find_element(By.CSS_SELECTOR, 'ytd-thumbnail > a > yt-image > img')
                    src = thumbnail.get_attribute('src')
                    while(src is None):
                        if scroll_limit < 1:
                            break
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                        scroll_limit -= 1
                        time.sleep(0.5)
                        src = thumbnail.get_attribute('src')
                    print('Video Title: '+title+'\nChannel: '+uploader)
                    try:
                        print('imgsrc: '+src)
                    except TypeError:
                        print('Failed to read imgsrc')
                    self.parent.setVideoInfo(title, link, uploader, src)

                except NoSuchElementException:
                    print("NoSuchElementException Occured")
            print(f"Scroll Count: %d", scroll_limit)
        except NoSuchElementException:
            print("NoSuchElementException Occured")

    def goto(self, link):
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
        except NoSuchWindowException:
            self.driver.quit()
            self.driver = webdriver.Chrome()    
        self.driver.switch_to.new_window('tab')
        self.driver.get(link)

    def quit(self):
        self.driver.quit()


class VideoFrame(QFrame):
    def __init__(self, parent, title, link, uploader, thumbnail):
        super().__init__()
        self.parent = parent
        self.title = title
        self.link = link
        self.uploader = uploader
        self.thumbnail = thumbnail
        self.init_ui()

    def init_ui(self):
        infoLayout = QHBoxLayout()
        metaLayout = QVBoxLayout()
        metaLayout.addWidget(QLabel(self.title))
        metaLayout.addWidget(QLabel(self.uploader))
        imgLabel = QLabel()
        pix = QPixmap()
        # Load img From URL and Resize the Widget
        if self.thumbnail is not None:
            image = urllib.request.urlopen(self.thumbnail).read()
            pix.loadFromData(image)
        else:
            # if Failed to load thumbnail, just a Youtube logo
            pix.load('thumbPlaceholder.webp')
        # resize the thumbnail
        imgLabel.setMaximumWidth(210)
        pix = pix.scaledToWidth(210)
        self.setObjectName("borderFrame")
        self.setStyleSheet('#borderFrame {border: 1px solid black;} ')
        imgLabel.setPixmap(pix)
        infoLayout.addWidget(imgLabel)
        infoLayout.addLayout(metaLayout)
        self.setLayout(infoLayout)

    def mousePressEvent(self, a0: QMouseEvent | None):
        self.parent.goto(self.link)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tube_bot = TubeBot(self)
        self.search_word = QLineEdit(self)
        self.btn_start = QPushButton("Connect")
        self.btn_search = QPushButton("Search")
        self.btn_quit = QPushButton("Quit")
        self.btn_start.clicked.connect(self.getSearch)
        self.btn_search.clicked.connect(self.onlySearch)
        self.btn_quit.clicked.connect(self.close)
        self.mainLayout = QVBoxLayout()
        self.contentsLayout = QVBoxLayout()
        self.scrollView = QScrollArea()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('YtScroll')
        print('Hello.')
        mainWidget = QWidget()
        contentsWidget = QWidget()
        contentsWidget.setLayout(self.contentsLayout)
        self.scrollView.setWidget(contentsWidget)
        self.scrollView.setWidgetResizable(True)
        self.scrollView.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.scrollView.setMaximumSize(800, 1400)
        buttonBox = QHBoxLayout()
        buttonBox.addWidget(self.btn_start)
        buttonBox.addWidget(self.btn_search)
        buttonBox.addWidget(self.btn_quit)

        self.mainLayout.addWidget(self.search_word)
        self.search_word.setMaximumHeight(40)
        self.mainLayout.addLayout(buttonBox)
        self.mainLayout.addWidget(self.scrollView)
        mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(mainWidget)
        self.resize(600, 1200)
        self.show()

    def getSearch(self, a0):
        self.btn_start.setFlat(True)
        self.btn_start.setText('Connecting...')
        QApplication.processEvents()
        if self.tube_bot:
            self.tube_bot.getPage()
        self.btn_start.setFlat(False)
        self.btn_start.setText('Connect')
    
    def onlySearch(self, a0):
        if self.tube_bot:
            self.btn_search.setFlat(True)
            self.btn_search.setText('Searching...')
            self.clearVideoInfo()
            QApplication.processEvents()
            self.tube_bot.search()
            self.btn_search.setFlat(False)
            self.btn_search.setText('Search')

    def setVideoInfo(self, title, link, uploader, thumbnail):
        widget = VideoFrame(self, title, link, uploader, thumbnail)
        self.contentsLayout.addWidget(widget)

    def clearVideoInfo(self):
        child = self.contentsLayout.takeAt(0)
        while child is not None:
            child.widget().deleteLater()
            child = self.contentsLayout.takeAt(0)

    def goto(self, link):
        self.tube_bot.goto(link)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        if self.tube_bot:
            self.tube_bot.quit()
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())