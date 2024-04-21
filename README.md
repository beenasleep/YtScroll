# YtScroll: Youtube search result
이 프로그램은 비 로그인 상태에서 입력된 검색어로 유튜브 검색 후 필요 없는 정보를 제외하고 보여주기 위한 도구입니다.
## 주 기능(main.py 실행)
### Connect
Selenium을 가동해 Youtube에 접속합니다.
### Search
프로그램 상단의 입력창에 입력되어 있는 검색어의 검색 결과 페이지에서 검색 결과에 해당하는 것만 가져옵니다.

유튜브에서 검색을 해 보면 순수 검색결과 외에 광고, 채널, Shorts, 관련 동영상 등이 중간에 섞여 있습니다. 이들은 가져오지 않습니다.
### Quit
Selenium과 함께 해당 프로그램을 종료합니다.

# 클래스
## TubeBot
selenium webdriver의 전반적인 동작을 수행하는 클래스입니다.
### def __init__(parent= None)
생성자 메소드. webdriver와 parent(MainWindow)를 선언합니다.
### def getPage()
webdriver.Chrome()을 생성하고
https://www.youtube.com 에 접속합니다.
### def search()
검색하고 검색 결과를 읽어 MainWindow에 전달합니다.
### def quit()
selenium webdriver를 종료합니다.
## MainWindow
ui를 담당하며, TubeBot을 멤버 변수로 가지고 필요한 동작을 요청합니다.
### def __init__()
생성자 메소드. 관리가 필요한 변수를 전부 선언하고 버튼과 메소드를 연결한 후 init_ui()를 호출합니다.
### def init_ui()
필요한 ui 요소들을 배치하고 프로그램 창을 보여줍니다.
### def getSearch(a0)
'connect' 버튼을 누르면 호출되는 메소드로, TubeBot의 getPage()를 호출합니다.

메소드 동작 중에는 'connect' 버튼의 텍스트를 'Connecting...'으로 표시합니다.
### def onlySearch(a0)
'search' 버튼을 누르면 호출되는 메소드로, TubeBot의 search()를 호출합니다.

메소드 동작 중에는 'search' 버튼의 텍스트를 'Searching...'으로 표시합니다.
### def setVideoInfo(title, uploader, thumbnail)
TubeBot.search() 동작 중 호출될 메소드입니다.

제목, 채널명, 썸네일을 전달받아 ui에 추가합니다.
### def clearVideoInfo()
'search' 버튼을 누르면 호출되는 메소드로,검색을 진행하기 전에 이전 기록을 ui에서 삭제합니다.
### def closeEvent(self, a0: QCloseEvent | None)
창을 닫을 때 'quit' 버튼이 아닌 우상단 '**x**' 버튼으로 닫을 경우에 selenium webdriver 프로세스가 종료되지 않는 문제를 방지하기 위한 오버라이드 메소드입니다.