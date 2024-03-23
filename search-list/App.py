import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

class App:

    home_url = "https://artisans.quelleenergie.fr/"

    def get_cates(self, url):
        ret = []
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")
            search_domain = soup.find('select', id='search-domaine-activite')
            options = search_domain.find_all('option')
            for option in options:
                ret.append(option['value'])
        else:
            print("Failed to retrieve page:", response.status_code)

        return ret

    def get_page(self, cate):
        page = 0
        url = self.home_url + cate
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            pagination = soup.find('nav', class_='pagination')
            # print(pagination)
            if pagination == None:
                print("None pagination")
            else:
                pagination.find('span', class_='page')
                # print(pagination)
                last = pagination.find('span', class_="last")
                last_href = last.find('a')
                if last_href:
                    href_value = last_href['href']
                    query = href_value.split("?")
                    page = query[1].split("=")[1]
        else:
            print("Failed to retrieve page:", response.status_code)          

        print("cate page", cate, page)
        if page == 0: 
            return None

        return range(1, int(page)+1)

    def company(self, cate, page):
        ret = []
        url = self.home_url + cate + '?page=' + str(page)
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            companies = soup.find(
            'div', class_='artisans-container'
            ).find_all('a', class_='artisan-item')
        
            for company in companies:
                href = company['href']
                # print(href, "\n")
                ret.append(self.info(cate, href))

        else:
            print("Failed to retrieve page:", response.status_code)

        return ret

    def info(self, cate, href):
        url = self.home_url + href.lstrip('/')
        print("info url : ", url)
        ret = {
            'Company':'',
            'Job_category': cate,
            'Siret': '',
            'Address': '',
            'Postcode': '',
            'City': '',
            'Website': '',
        }
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            company = soup.find('h1', class_='artisan-societe').text.strip()
            ret['Company'] = company
            infos = soup.find('div', class_='informations-societe')
            rows = infos.find_all('div', 'informations-societe-row')
            for row in rows:
                label = row.find('span', class_='informations-societe-label')
                value = row.find('span', class_='informations-societe-value')
                if label != None:
                    # print(len(label), len(value), value)
                    # print(label.get_text(), value.get_text())
                    label_txt = label.text.strip()
                    ret[label_txt] = value.text.strip()
        else:
            print("Failed to retrieve page:", response.status_code)

        return ret

    def save(self, data):
        df = DataFrame(data)
        df.to_excel("company.xlsx", index=False)
        return

    def run(self):
        print("App start running")
        for cate in self.get_cates(self.home_url):
            companies = []
            pages = self.get_page(cate)
            if pages:
                for p in pages:
                    # print(p)
                    ret = self.company(cate, p)
                    companies.append(ret)
                    # print(ret)

            if companies:
                self.save(companies)
                exit()
        return

