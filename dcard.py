import time
import os.path

import chardet
import requests
import pyquery
import munch
import json
import re
import urllib.parse as UP


#https://ithelp.ithome.com.tw/articles/10203216

def getDcard(found,cookic):
    response = requests.get(
        #最新
        # url=f'https://www.dcard.tw/f/{found}?latest=true',
        #熱門
        url=f'https://www.dcard.tw/f/{found}',
        headers = { "Referer": "https://www.dcard.tw/f/{found}/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie": cookic},
    )
    if response.status_code != 200:
        print(f'status is not 200 ({response.status_code})')
        return
    p = requests.Session()
    dom = pyquery.PyQuery(response.text)
    codes = dom('div.PostList_entry_1rq5Lf a.PostEntry_root_V6g0rd').items()
    a = []
    for code in codes:
        a.append(code.attr('href').replace("\n",""))
    for k in range(0,5):
        post_data={
            #旅遊
            # "before":a[-1][12:21],
            #西施
            "before":a[-1][9:18],
            "limit":"30",
            #最新
            # "popular":"false",
            #熱門
            "popular":"true"
        }
        r = p.get(f"https://www.dcard.tw/_api/forums/{found}/posts",params=post_data, headers = { "Referer": "https://www.dcard.tw/f/{found}/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie":cookic},)
        if r.status_code != 200:
            print(f'Lazy Loading error')
            return
        data2 = json.loads(r.text)
        for u in range(len(data2)):
            dcardurl = f"/f/{found}/p/{data2[u]['id']}-{data2[u]['title']}"
            a.append(dcardurl)
        print(len(a))
        time.sleep(1)
    for i in a[2:]:
        print(f'文章{(a.index(i))+1}開始下載')
        url = "https://www.dcard.tw" + i
        # url = "https://www.dcard.tw/f/sex/p/" + UP.quote(i[9:])
        # print(url)
        url = requests.get(url,
        headers = { "Referer": "https://www.dcard.tw/f/{found}/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie":cookic},
        )
        if url.status_code != 200:
            print(f'選擇文章錯誤 https://www.dcard.tw{i}')
            # return
        for page in range(0,3000):
            id = i[9:18]
            r1= requests.get(
                url=f'https://www.dcard.tw/_api/posts/{id}/comments?after={(50+page*30)}',
                # url=f'https://www.dcard.tw/_api/posts/p/232670/comments?after=0',
                headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie": cookic},
            )
            # print(f'https://www.dcard.tw/_api/posts/{id}/comments?after={50+(page*30)}')
            if r1.status_code not in [200,304]:
                print(f'文章Lazy Loading error https://www.dcard.tw/_api/posts{id}/comments?after={(50+page*30)} ({r1.status_code})')
                break
                # return
            # if r1.status_code == 404:
            #     print(f'{r1.status_code}')
            #     continue
            data3 = json.loads(r1.text)
            if len(data3) ==0:
                break
                # print(f'data3{type(data3)}')
                # print(f'r1{r1.text}')
            for u1 in data3:
                if  'mediaMeta' in u1:
                    medias = u1['mediaMeta']
                    if len(medias) != 0:
                        # imageurl.append(medias[0]['url'])
                        media = medias[0]['url']
                        # media = media.lower()
                        pattern = re.compile(r'http\S+')
                        media = pattern.findall(media)
                        # print(medias)
                        getimages3 = requests.get(media[0],
                        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookic":cookic},)
                        if getimages3.status_code not in [200,304]:
                            print('圖片下載失敗3')
                            # return
                            print(media[0])
                        with open(f'dcardimages/dcard{found}/{os.path.basename(media[0])}', 'wb') as f3:
                            f3.write(getimages3.content)
        time.sleep(1)
            # with open(f'dcard/dcard{page}.json', 'wb') as f:
            #             f.write(r1.content)

        # with open(f'dcard/dcard{id}.html', 'wb') as fa:
        #     fa.write(url.content)
        dom2 = pyquery.PyQuery(url.text)
        images = dom2('div.Post_content_NKEl9d div div div img.GalleryImage_image_3lGzO5').items()
        images2 = dom2('div.CommentEntry_content_1ATrw1 div div div img.GalleryImage_image_3lGzO5').items()

        for image in images:
            # imageurl.append(image.attr('src'))
            imageurl = image.attr('src')
            print(imageurl)
            # imageurl = str(imageurl.lower())
            pattern = re.compile(r'http\S+')
            imageurl = pattern.findall(imageurl)
            getimages = requests.get(imageurl[0],
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie":cookic},
            )
            if getimages.status_code not in [200,304]:
                print(f'圖片下載失敗 ({getimages.status_code})')
                print(imageurl[0])
                # return
            with open(f'dcardimages/dcard{found}/{os.path.basename(imageurl[0])}', 'wb') as f2:
                f2.write(getimages.content)
        print(f'文章{(a.index(i))+1}下載成功')
        # for image in images2:
        #     imageurl = image.attr('src')
        #     getimages = requests.get(imageurl,
        #     headers = { "Referer": "https://www.dcard.tw/f/{found}/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36","cookie":cookic},)
        #     if getimages.status_code != 200:
        #         print('圖片下載失敗2')
        #         # return
        #     with open(f'dcardimages/dcard{found}/{os.path.basename(imageurl)}', 'wb') as f2:
        #         f2.write(getimages.content)
        #1153


if __name__ == '__main__':
    getDcard('sex','__cfduid=d50899817f27dd2710e8b8cc55d73351f1573903418; __auc=df3aa17016e73f44cde1bd4ac6b; _fbp=fb.1.1573903422545.840917452; G_ENABLED_IDPS=google; intercom-id-nd88a3n4=b572f487-55f4-4a17-8018-d21d9b59a4c4; _gid=GA1.2.1063667095.1577286388; __asc=2c929a9916f3d984adb6af1242a; _gat=1; dcsrd=7MZ_Lha6V3xM6dtVRusmAKdx; dcsrd.sig=F883G5sQ0GgzP0jJai5cywsOIq0; country=TW; amplitude_id_bfb03c251442ee56c07f655053aba20fdcard.tw=eyJkZXZpY2VJZCI6IjBiNGE0NGZkLTVmOTQtNDJiYy05NWIxLTgyNGNkYTg3MjQ4OFIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTU3NzI4NjM5MDE0MCwibGFzdEV2ZW50VGltZSI6MTU3NzI4NjM5NzY3NiwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9; _ga=GA1.1.1533891659.1573903421; _ga_C3J49QFLW7=GS1.1.1577286398.11.0.1577286398.0')

