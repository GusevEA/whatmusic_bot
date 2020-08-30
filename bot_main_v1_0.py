from time import sleep
import bs4
from urllib import request
from selenium import webdriver
from moviepy.editor import *
import requests
from selenium.webdriver.common.keys import Keys


class DirectPage:

    def __init__(self, browser):
        self.browser = browser
        self.browser.get('https://www.instagram.com/accounts/login/?next=/direct/inbox/')

    def login(self, username, password):
        username_input = self.browser.find_element_by_css_selector("input[name='username']")
        password_input = self.browser.find_element_by_css_selector("input[name='password']")
        username_input.send_keys(username)
        sleep(2)
        password_input.send_keys(password)
        sleep(2)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        sleep(4)
        self.browser.find_element_by_css_selector('button.sqdOP:nth-child(1)').click()
        sleep(4)
        self.browser.find_element_by_css_selector('button.aOOlW:nth-child(2)').click()
        sleep(2)

    def new_messages(self):
        num_new = len(self.browser.find_elements_by_css_selector('.soMvl'))
        return num_new

    def click_message(self):
        global username
        username = ''
        message = self.browser.find_elements_by_css_selector('.qyrsm')[-1].text  # получение текста сообщения
        username = self.browser.find_elements_by_css_selector('.qyrsm')[0].text  # получение имя пользователя

        # Click на новое сообщение
        try:
            self.browser.find_elements_by_css_selector('.qyrsm')[-1].click()
            sleep(2)
        except:
            event = 'cotninue'
            print('[EXCEPT] click on new message')

        # проверка последнего сообщения на IGTV
        try:
            is_IGTV = bool(
                self.browser.find_elements_by_css_selector('.iXTil')[-1].find_element_by_css_selector('.XTCZH'))
        except:
            is_IGTV = False

        if message == 'Отправил(-а) публикацию' or is_IGTV == True:
            event = 'video'
        elif message == 'Отправил(-а) историю':
            event = 'stories'
        elif message == '/help':
            event = 'help'
        else:
            event = 'error'

        # видео + сторис последнее сообщение
        try:
            self.browser.find_elements_by_css_selector('.iXTil')[-1].click()
            sleep(4)
        except:
            print('[EXCEPT] click last message')

        print('[INFO] EVENT: ' + event)
        return event

    def event_process(self, event):
        # get url from video
        # event = video
        url = None
        video_html = self.browser.page_source
        soup = bs4.BeautifulSoup(video_html)
        if event == 'video':
            url_soup = soup.find(class_='_5wCQW')
            if url_soup is not None:
                url = url_soup.find(class_='tWeCl').get('src')
            else:
                print('[EXCEPT] try find video [1]')
                self.browser.refresh()
                sleep(2)
                video_html = self.browser.page_source
                soup = bs4.BeautifulSoup(video_html)
                url_soup = soup.find(class_='_5wCQW')

                if url_soup is not None:
                    url = url_soup.find(class_='tWeCl').get('src')
                else:
                    print('[EXCEPT] try find video [2]')
                    self.browser.back()
                    sleep(3)
                    text_ru = "Недопустимый формат🤷🏼‍♂️ Отправьте '/help'"
                    text_eng = "Invalid format🤷🏼‍♂️ Send '/help'"
                    try:
                        self.send_message(text_eng=text_eng, text_ru=text_ru)
                    except:
                        print('[EXCEPT] cant send error message (event == "video")')

        # event = stories
        elif event == 'stories':
            try:
                url = soup.find(class_='y-yJ5 OFkrO').find('source').get('src')
            except:
                print('[EXCEPT] try find stories')
                text_ru = "Недопустимый формат🤷🏼‍♂️ Отправьте '/help'"
                text_eng = "Invalid format🤷🏼‍♂️ Send '/help'"
                try:
                    self.send_message(text_eng=text_eng, text_ru=text_ru)
                except:
                    print('[EXCEPT] cant send error message (event == "stories")')

        elif event == 'help':  # дописать, что будет в хелпе  !!!! # ссылка на пост с помощью

            text_eng = "The page is under construction🛠"
            text_ru = "Страница в разработке🛠"

            self.send_message(text_eng=text_eng, text_ru=text_ru)

        # event = error / person video
        else:
            text_ru = "Недопустимый формат🤷🏼‍♂️ Отправьте '/help'"
            text_eng = "Invalid format🤷🏼‍♂️ Send '/help'"

            user_text = self.browser.find_elements_by_css_selector('.iXTil')[-1].text

            reels_text = 'Используйте последнюю версию приложения\nЧтобы посмотреть это видео Reels, используйте последнюю версию приложения Instagram.'

            # person video?
            if user_text == '':
                try:
                    video_html = browser.find_elements_by_css_selector('.xATCy')[-1].get_attribute('innerHTML')
                    # print(video_html)
                    soup = bs4.BeautifulSoup(video_html)
                    url = soup.find('source').get('src')
                    print('[INFO] PERSON VIDEO')
                    self.browser.find_elements_by_css_selector('.wpO6b')[-1].click()
                    return url
                except:
                    print('[INFO] INVALID FORMAT')
                    try:
                        self.send_message(text_eng=text_eng, text_ru=text_ru)
                    except:
                        print('[EXCEPT] cant send error message (event == error -> if)')

            elif user_text == reels_text:
                print('[INFO] REELS POST')
                text_eng = 'Reels format is not supported at the moment🙄'
                text_ru = 'Формат Reels не поддерживается на данный момент🙄'
                try:
                    self.send_message(text_eng=text_eng, text_ru=text_ru)
                except:
                    print('[EXCEPT] cant send error message (event == error -> reels)')


            else:
                print('[INFO] INVALID FORMAT')
                try:
                    self.send_message(text_eng=text_eng, text_ru=text_ru)
                except:
                    print('[EXCEPT] cant send error message (event == error) -> invalid')

        # out from video/page
        self.browser.back()
        sleep(1)

        return url

    def get_audio(self, url, num):
        request.urlretrieve(url, os.getcwd() + f'\\video\\{str(num)}.mp4')
        video = VideoFileClip(os.getcwd() + f'\\video\\{str(num)}.mp4')
        print('[INFO] VIDEO UPLOAD')
        audio = video.audio
        audio.write_audiofile(os.getcwd() + f'\\video\\{str(num)}.ogg')
        print('[INFO] AUDIO UPLOAD')

        # processing message
        if username == 'n_salykina':
            text_eng = 'Обрабатываю, зайка❤️'
            text_ru = ''
        else:
            text_eng = 'Processing...🚀'
            text_ru = ''
            # text_ru = 'Обрабатываю...🚀'
        self.send_message(text_eng=text_eng, text_ru=text_ru)

    def telegram_track(self, browser_tel):
        browser_tel.find_elements_by_css_selector('.im_dialog_wrap')[0].click()  # поиск сообщения в телеграмме

        num_diag = len(browser_tel.find_elements_by_css_selector('.im_dialog_peer'))
        for i in range(num_diag):
            if browser_tel.find_elements_by_css_selector('.im_dialog_peer')[i].text == 'Яндекс.Музыка':
                browser_tel.find_elements_by_css_selector('.im_dialog_peer')[i].click()

        browser_tel.find_elements_by_css_selector('input[type=file]')[0].send_keys(
            os.getcwd() + f'\\video\\{str(num)}.ogg')

        sleep(8)

        text = browser_tel.find_elements_by_css_selector('.im_message_text')[-1].text
        if text == '':
            text = browser_tel.find_elements_by_css_selector('.im_message_text')[-2].text

        music_data = text.split('\n')
        print('[INFO] GET INFO FROM TELEGRAM')

        return music_data

    def send_track(self, music_data):
        music_name = music_data[0]
        yandex_link = music_data[1]

        print('[INFO] MUSIC IS FOUND: ' + music_name)

        apple_link = self.get_applemusic_link(music_name)
        youtube_link = self.get_youtube_link(music_name)

        # type message
        NEW_LINE = Keys.SHIFT + Keys.ENTER
        # music name
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            music_name + Keys.ENTER)

        sleep(0.5)

        # apple music
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            '[APPLE MUSIC]:' + NEW_LINE)
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            apple_link)

        # new line
        self.new_line_message()

        # yandex music
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            '[YANDEX MUSIC]:' + NEW_LINE)
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            yandex_link)

        # new line
        self.new_line_message()

        # youtube
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            '[YOUTUBE]:' + NEW_LINE)
        self.browser.find_element_by_css_selector('textarea[placeholder="Напишите сообщение..."]').send_keys(
            youtube_link + Keys.ENTER)

        sleep(5)

    def not_found(self):
        print('[INFO] MUSIC NOT FOUND')
        text_ru = 'К сожалению, я не могу найти её в своем каталоге😔'
        text_eng = 'Sorry, I cant find it in my directory😔'
        self.send_message(text_eng=text_eng, text_ru=text_ru)

        sleep(1)

    def get_applemusic_link(self, music_name):
        # apple music link
        url_apple_music = 'https://music.apple.com/us/search?at=1000l4QJ&ct=401&itscg=10000&itsct=401x&term='
        music_name_apple = '%20'.join(music_name.split(' '))
        url_apple_music += music_name_apple
        html_apple_music = requests.get(url_apple_music).text
        soup = bs4.BeautifulSoup(html_apple_music)
        if soup.find(class_='dt-link-to') is not None:
            apple_link = soup.find(class_='dt-link-to').get('href')
        else:
            apple_link = '-------'

        return apple_link

    def get_youtube_link(self, music_name):
        # youtube link
        youtube_link = 'https://www.youtube.com/results?search_query='
        music_name_youtube = '+'.join(music_name.split(' '))
        youtube_link += music_name_youtube
        return youtube_link

    def new_line_message(self):
        NEW_LINE = Keys.SHIFT + Keys.ENTER
        self.browser.find_element_by_css_selector(
            'textarea[placeholder="Напишите сообщение..."]').send_keys(NEW_LINE)
        self.browser.find_element_by_css_selector(
            'textarea[placeholder="Напишите сообщение..."]').send_keys(NEW_LINE)

    def send_message(self, text_eng=None, text_ru=None):
        try:
            self.browser.find_element_by_css_selector(
                'textarea[placeholder="Напишите сообщение..."]').send_keys(text_eng)

            self.new_line_message()

            self.browser.find_element_by_css_selector(
                'textarea[placeholder="Напишите сообщение..."]').send_keys(text_ru + '\n')
            sleep(2)
        except:
            print('[EXCEPT] cant send message')

    def back_direct(self):
        self.browser.get('https://www.instagram.com/direct/inbox/')

    # ЗАПРОСЫ НА СООБЩЕНИЯ
    def new_requests(self):
        try:
            num = int(self.browser.find_element_by_css_selector('.yWX7d').text[0])  # запрос на подписку
        except:
            try:
                num = int(self.browser.find_element_by_css_selector('.yWX7d').text[-1])
            except:
                num = 0

        return num

    def accept_request(self):
        try:
            self.browser.find_element_by_css_selector('.yWX7d').click()  # открыть запросы
            self.browser.find_elements_by_css_selector('.DPiy6')[-2].click()  # нажать на запрос
            self.browser.find_elements_by_css_selector('._8A5w5')[-1].click()  # принять
        except:
            print("[EXCEPTION] can't accept request")

    def back_request(self):
        self.browser.get('https://www.instagram.com/direct/requests/')


def main():
    # telegram
    browser_tel = webdriver.Chrome()
    browser_tel.implicitly_wait(5)
    browser_tel.get('https://web.telegram.org/#/im')
    number = '9268589598'
    phone = browser_tel.find_elements_by_css_selector('input[type="tel" i]')[-1]
    phone.send_keys(number + '\n')
    browser_tel.find_elements_by_css_selector('.btn-md-primary')[-1].click()

    # instagram
    login = 'whatmusic_bot'
    password = 'gordon12'
    browser = webdriver.Firefox()
    browser.implicitly_wait(5)
    dm = DirectPage(browser)
    dm.login(login, password)

    def process_message(dm, browser_tel, i):
        print(f'---------- N: {i} ----------')
        event = dm.click_message()
        if event != 'continue':
            video_url = dm.event_process(event)
            if video_url is not None:
                dm.get_audio(video_url, num)
                music_data = dm.telegram_track(browser_tel)
                if len(music_data) == 2:
                    dm.send_track(music_data)
                else:
                    dm.not_found()
            else:
                print('[EXCEPT] VIDEO URL IS NONE')

        dm.back_direct()

    mess_num = 1
    req_num = 0

    while True:

        # processing new messages
        num_new = dm.new_messages()
        for num in range(num_new):
            process_message(dm, browser_tel, mess_num)
            mess_num += 1
            print('[INFO] DONE')
            sleep(1)

        # processing new requests
        num_req = dm.new_requests()
        for num in range(num_req):
            dm.accept_request()
            dm.back_request()
            req_num += 1
            print('----------')
            print(f'[INFO] ACCEPT REQUEST ({req_num})')
            print('----------')
            sleep(1)

        dm.back_direct()

        sleep(4)


if __name__ == '__main__':
    main()
