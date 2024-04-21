from PyQt6.QtGui import QCloseEvent
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
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

    def search(self):
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
            # 검색결과가 새 것으로 바뀌기까지 기다리는 방법을 찾지 못해 임시로 time.sleep 사용
            time.sleep(2)
            # WebDriverWait(self.driver, 7).until(EC.invisibility_of_element((By.ID, 'contents')))
            WebDriverWait(self.driver, 7).until(EC.presence_of_element_located((By.ID, 'contents')))
            contents = self.driver.find_elements(By.XPATH, '//*[@id="contents"]/ytd-video-renderer')
            print('contents count: ' + str(len(contents)))
            WebDriverWait(self.driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'yt-core-image--loaded')))
            time.sleep(1)
            #무한 스크롤 상태에 빠질 가능성을 방지하기 위한 PAGE_DOWN 50회 제한
            scroll_limit = 50
            for i in range(len(contents)):
                try:
                    # Video Title
                    title = self.driver.find_element(By.XPATH, '//*[@id="contents"]/ytd-video-renderer['+str(i+1)+']/div[1]/div[1]/div[1]/div/h3/a').get_attribute('title')
                    # Channel Name
                    uploader = self.driver.find_element(By.XPATH, '//*[@id="contents"]/ytd-video-renderer['+str(i+1)+']/div[1]/div[1]/div[2]/ytd-channel-name/div/div/yt-formatted-string/a').text
                    # Thumbnail
                    thumbnail = self.driver.find_element(By.XPATH, '//*[@id="contents"]/ytd-video-renderer['+str(i+1)+']/div[1]/ytd-thumbnail/a/yt-image/img')
                    src = None
                    while(src is None):
                        if scroll_limit < 1:
                            break
                        time.sleep(0.5)
                        src = thumbnail.get_attribute('src')
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                        scroll_limit -= 1
                    print('Video Title: '+title+'\nChannel: '+uploader)
                    try:
                        print('imgsrc: '+src)
                    except TypeError:
                        print('Failed to read imgsrc')
                    self.parent.setVideoInfo(title, uploader, src)

                except NoSuchElementException:
                    print("NoSuchElementException Occured")
            print(f"Scroll Count: %d", scroll_limit)
        except NoSuchElementException:
            print("NoSuchElementException Occured")


    def quit(self):
        self.driver.quit()

class QBorder(QWidget):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

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

    def setVideoInfo(self, title, uploader, thumbnail):
        infoLayout = QHBoxLayout()
        metaLayout = QVBoxLayout()
        metaLayout.addWidget(QLabel(title))
        metaLayout.addWidget(QLabel(uploader))
        imgLabel = QLabel()
        pix = QPixmap()

        #TODO: Load img From URL and Resize the Widget
        if thumbnail is not None:
            image = urllib.request.urlopen(thumbnail).read()
            pix.loadFromData(image)
        else:
            pix.load('thumbPlaceholder.webp')
        imgLabel.setMaximumWidth(210)
        # imgLabel.setMaximumHeight(118)
        pix = pix.scaledToWidth(210)
        imgLabel.setPixmap(pix)
        infoLayout.addWidget(imgLabel)
        infoLayout.addLayout(metaLayout)

        # TODO: QBorder를 활용한 테두리 그리기 왜 안되는지 알아내기
        widget = QBorder()
        widget.setStyleSheet('QBorder {border: 1px solid black;} ')
        widget.setLayout(infoLayout)
        self.contentsLayout.addWidget(widget)

    def clearVideoInfo(self):
        child = self.contentsLayout.takeAt(0)
        while child is not None:
            child.widget().deleteLater()
            child = self.contentsLayout.takeAt(0)

        

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        if self.tube_bot:
            self.tube_bot.quit()
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())