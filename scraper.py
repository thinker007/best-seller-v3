import requests
from bs4 import BeautifulSoup as bs
import scraperwiki
from datetime import datetime
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import grequests

start_urls = ['http://www.amazon.com/Best-Sellers-Books-Arts-Photography/zgbs/books/1/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Business-Money/zgbs/books/3/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Computers-Technology/zgbs/books/5/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Education-Teaching/zgbs/books/8975347011/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Engineering-Transportation/zgbs/books/173507/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-History/zgbs/books/9/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Law/zgbs/books/10777/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Medical/zgbs/books/173514/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Politics-Social-Sciences/zgbs/books/3377866011/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Reference/zgbs/books/21/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Science-Math/zgbs/books/75/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Test-Preparation/zgbs/books/5267710011/ref=zg_bs_nav_b_1_b', 
'http://www.amazon.com/Best-Sellers-Books-Textbooks/zgbs/books/465600/ref=zg_bs_nav_b_1_b']
pool = Pool(cpu_count() * 20)

def scrape(response, **kwargs):
        listing_soup = bs(response.text, 'lxml')
        asin_nums = listing_soup.find_all('div', 'zg_itemImageImmersion')
        for asin_num in asin_nums:
            asin = ''
            try:
                asin = asin_num.a['href'].split('dp/')[-1].strip()
            except:
                pass
            today_date = str(datetime.now())
            scraperwiki.sqlite.save(unique_keys=['Date'], data={'ASIN': asin, 'Date': today_date})


def multiparse(links):
         l = links.find('a')['href'].encode('utf-8')
         if l:
             return l


def parse(url):
    if url in start_urls:
        async_list = []
        for i in xrange(1, 6):
            print (url+'?&pg={}'.format(i))
            rs = (grequests.get(url+'?&pg={}'.format(i), hooks = {'response' : scrape}))
            async_list.append(rs)
        grequests.map(async_list)
    page = requests.get(url)
    soup = bs(page.text, 'lxml')
    try:
        active_sel = soup.find('span', 'zg_selected').find_next()
        if active_sel.name == 'ul':
            links_lists= active_sel.find_all('li')
            asins = pool.map(multiparse, links_lists)
            for asin in asins:
                async_list = []
                for i in xrange(1, 6):
                    print (asin+'?&pg={}'.format(i))
                    rs = (grequests.get(asin+'?&pg={}'.format(i), hooks = {'response' : scrape}))
                    async_list.append(rs)
                parse(asin)
                grequests.map(async_list)


    except:
        parse(url)


if __name__ == '__main__':

   for start_url in start_urls:
       parse( start_url)
