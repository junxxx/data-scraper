import requests
from bs4 import BeautifulSoup
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

class App:
    
    max_worker = 10
    home_url = "https://artisans.quelleenergie.fr/"

    def get_cates(self, url):
        ret = []

        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")
            search_domain = soup.find(
                'select',
                id='search-domaine-activite'
            )
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
            if pagination == None:
                print("None pagination")
            else:
                pagination.find('span', class_='page')
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
            return []

        page = 2

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
                ).find_all('a',class_='artisan-item')
        
            with ThreadPoolExecutor(max_workers=self.max_worker) as executor:
                future_rets = {executor.submit(self.info, cate, a['href']): a for a in companies}
                for future in concurrent.futures.as_completed(future_rets):
                    try:
                        # data = future.result()
                        ret.append(future.result())
                        # print("cate data: ", cate, data)
                    except Exception as exc:
                        print('generated an exception: %s' % (exc))
                    else:
                        print('company page %d, cate %s' % (page, cate))

        else:
            print("Failed to retrieve page:", response.status_code)

        return ret

    def info(self, cate, href):
        url = self.home_url + href.lstrip('/')
        print("info url : ", url)
        ret = {
            # 'Company':'',
            'Job_category': cate,
            # 'Siret': '',
            # 'Address': '',
            # 'Postcode': '',
            # 'City': '',
            # 'Website': '',
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
                    label_txt = label.text.replace(':', '').strip()
                    ret[label_txt] = value.text.strip()
        else:
            print("Failed to retrieve page:", response.status_code)

        return ret

    def save(self, data):
        import csv
        # csv header
        fieldnames = ['Job_category', 'Company', 'Siret', 'Adresse', 'Site web']

        with open('company.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return

    def run(self):
        print("App start running")
        companies = []
        for cate in self.get_cates(self.home_url):
            pages = self.get_page(cate)
            with ThreadPoolExecutor(max_workers=self.max_worker) as executor:
                future_rets = {executor.submit(self.company, cate, p): p for p in pages}
                for future in concurrent.futures.as_completed(future_rets):
                    try:
                        data = future.result()
                        companies = companies + data
                        print("cate data: ", cate, data)
                    except Exception as exc:
                        print('generated an exception: %s' % (exc))
                    else:
                        print('%d bytes' % (len(data)))

        if companies:
            self.save(companies)
        return

