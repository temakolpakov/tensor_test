import requests
from bs4 import BeautifulSoup
import re
import os


class Parser:
    """Класс, вытаскивающий из веб-страницы только основной текст
    """
    def __init__(self, url):
        """
        Конструктор класса
        :param url: str 
        """
        self.url = url
        self.title = None
        self.lines = None
        self.text = None
        self.formatted_text = None

    def get_lines(self):
        """
        Функция, возвращающая объекты BeautifulSoup, каждый из которых является тегом <p>
        :return: list of BeautifulSoup objects 
        """
        response = requests.get(self.url)
        if response.status_code != 200:
            raise RuntimeError('Status code of {} is not 200'.format(self.url))
        bs = BeautifulSoup(response.text, 'html.parser')
        self.title = bs.find('title')
        self.lines = bs.find_all('p')
        self.lines.insert(0, self.title)
        lines_duplicate = self.lines

        # Ищем ссылки в каждой строке и добавляем их
        for i in range(len(lines_duplicate)):
            line = lines_duplicate[i]
            urls = line.find_all('a')
            if urls:
                for url in urls:
                    line = BeautifulSoup(str(line).replace(str(url), '{} {}'.format(url.text, url['href'])), 'html.parser')
                    lines_duplicate[i] = line

        self.lines = lines_duplicate
        return self.lines

    def get_text(self):
        """
        Функция, которая возвращает неформатированный текст
        :return: str
        """
        self.get_lines()
        # разделяем строки текса пустыми строками
        self.text = '\n\n'.join([line.text.strip() for line in self.lines])
        return self.text

    def get_formatted_text(self, splitter, re_url_settings):
        """
        Функция, возвращаюшая форматированный текст
        :param splitter: int 
        :param re_url_settings: regex str from settings
        :return: str
        """
        if not self.lines:
            self.get_lines()
        formatted_lines = []

        # построчно разделяем строки \n, если число символов больше чем n*splitter, где n, splitter - число
        for line in self.lines:
            line_text = line.text.strip()
            formatted_line_text = ''
            i = 0
            while i < len(line_text):
                if i >= splitter:
                    if line_text[i] != ' ':
                        # индекс последнего пробела в текущем секторе сроки
                        index_space = i - splitter + line_text[i - splitter:i].rfind(' ')
                        formatted_line_text += line_text[i - splitter:index_space] + '\n'
                        i -= len(line_text[index_space+1:i])
                    else:
                        formatted_line_text += line_text[i - splitter:i] + '\n'
                if i+splitter < len(line_text):
                    i += splitter
                else:
                    break
            if i < len(line_text):
                formatted_line_text += line_text[i:]
            formatted_lines.append(formatted_line_text)

        # разделяем строки текса пустыми строками
        self.formatted_text = '\n\n'.join(formatted_lines)

        # заменяем ссылки на ссылки в []
        re_url = re.compile(re_url_settings)
        matches = set(re_url.findall(self.formatted_text))
        for match in matches:
            self.formatted_text = self.formatted_text.replace(match, '[{}]'.format(match))
        return self.formatted_text

    def save_to_file(self, base_path):
        """
        Функция, сохраняющая форматированный текст в файл
        :param base_path: str base dir
        :return:
        """
        # определение имени конечной дирректории и имени файла
        splitted_url = self.url.split('//')[1].split('/')
        splitted_url = [elem for elem in splitted_url if ('?' not in elem and '&' not in elem and elem != '')]
        if not os.path.isdir(base_path+'/'.join(splitted_url[:-1])):
            os.makedirs(base_path+'/'.join(splitted_url[:-1]))

        with open(base_path+'/'.join(splitted_url)+'.txt', 'w') as f:
            f.write(self.formatted_text)
