import requests
import bs4
import json
import re


class JadvalyabCrawler:
    def __init__(self, years):
        self.base_url = 'https://www.jadvalyab.ir/halejadval/classic'
        self.years = years

    def crawl(self):
        for year in self.years:
            self.crawl_links_in_page(f'{self.base_url}?year={year}')

    def crawl_links_in_page(self, url):
        reg = f'{self.base_url}/(.*)'
        page = 1
        while True:
            r = requests.get(f'{url}&page={page}')
            bs = bs4.BeautifulSoup(r.text, 'html.parser')
            links = bs.find_all('a')
            find_link = False
            for link in links:
                href = link.get('href')
                if re.match(reg, href):
                    find_link = True
                    table_id = re.search(reg, href).group(1)
                    print(table_id)
                    answers, ofoghi, amoodi = self.crawl_crossword_data(table_id)
                    if answers and ofoghi and amoodi:
                        self.save_crossword_data(table_id, answers, ofoghi, amoodi)
            page += 1
            if not find_link:
                break

    def crawl_crossword_data(self, table_id: str):
        url = f'{self.base_url}/{table_id}'
        r = requests.get(url)
        bs = bs4.BeautifulSoup(r.text, 'html.parser')
        scripts = bs.find_all('script')
        for s in scripts:
            if 'let classic' in s.text:
                answers = re.search(r'let classic = JSON.parse\(`(.*?)`\);', s.text).group(1)
                answers = json.loads(answers)
                print(answers)
                ofoghi = re.search(r'let ofoghi = JSON.parse\(`(.*?)`\);', s.text).group(1)
                ofoghi = json.loads(ofoghi)
                print(ofoghi)
                amoodi = re.search(r'let amoodi = JSON.parse\(`(.*?)`\);', s.text).group(1)
                amoodi = json.loads(amoodi)
                print(amoodi)
                return answers, ofoghi, amoodi
        return None, None, None

    def save_crossword_data(self, table_id, answers, ofoghi, amoodi):
        with open(f'../data/crossword_{table_id}.txt', 'w', encoding='utf-8') as f:
            rows, cols = len(ofoghi), len(amoodi)
            f.write(f'{rows} {cols}\n')
            for ans in answers:
                for ch in ans:
                    if ch == '#':
                        f.write('1')
                    else:
                        f.write('0')
            f.write('\n')
            f.write('&')
            for qo in ofoghi:
                questions = qo.split('-')
                for i in range(len(questions)):
                    if i == 0:
                        f.write(questions[i].strip())
                    else:
                        f.write(f'#{questions[i].strip()}')
                f.write('@')
            for j in range(len(amoodi)):
                questions = amoodi[j].split('-')
                if j != 0:
                    f.write('@')
                for i in range(len(questions)):
                    if i == 0:
                        f.write(questions[i].strip())
                    else:
                        f.write(f'#{questions[i].strip()}')
            f.write('&\n&')
            for a in answers:
                split_answers = a.split('#')
                first = True
                for ans in split_answers:
                    if len(ans) > 1:
                        if first:
                            f.write(ans)
                            first = False
                        else:
                            f.write(f'#{ans}')
                f.write('@')
            for j in range(cols):
                i = 0
                first = True
                if j != 0:
                    f.write('@')
                while i < rows:
                    value = ''
                    while i < rows and answers[i][j] != '#':
                        value += answers[i][j]
                        i += 1
                    i += 1
                    if len(value) > 1:
                        if first:
                            f.write(value)
                            first = False
                        else:
                            f.write(f'#{value}')
            f.write('&')


if __name__ == '__main__':
    crawler = JadvalyabCrawler([1397, 1398, 1399, 1400, 1401])
    crawler.crawl()
