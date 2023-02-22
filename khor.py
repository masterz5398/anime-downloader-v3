import json
import os
from bs4 import BeautifulSoup
import sys
import re
from html import unescape
import base64
import requests
import lxml.html as htmlparser
from tqdm import tqdm
sys.path.append(r"C:\Users\shash\Desktop\programing\Project\RE\sourcePy")
from config import page_process as p, anime_folder, khor_url, stream_sb_aliases, fembed_aliases, dodostream_aliases, \
    mp4upload_aliases, dt_format, stream_sb_dld_base, merge, ks, khor_query_url, daily_motion_meta_url

sys.path.append(r"C:\Users\shash\Desktop\programing\Project\RE")
from basic_funcs import optionsX, check_one, eRX, check, Int


def dlX(file, url, continueX="no"):
    user_agent = 'Chrome/92.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)'
    headers = {'User-Agent': user_agent,
                # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                # 'Accept-Encoding': 'gzip, deflate, br',
                # 'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                'refer': "https://www.dailymotion.com/embed?api=postMessage&apimode=json&app=com.dailymotion.neon&autoplay-mute=true&client_type=website&collections-action=trigger_event&collections-enable=fullscreen_only&endscreen-enable=false&info=false&like-action=trigger_event&like-enable=fullscreen_only&queue-enable=false&sharing-action=trigger_event&sharing-enable=fullscreen_only&ui-logo=false&watchlater-action=trigger_event&watchlater-enable=fullscreen_only"
                }
    s = requests.Session()
    resp = s.get(url, headers=headers)
    resp = str(resp.text).split("\n")
    resp.pop(0)
    respd = {}
    i = 0
    for _ in resp:
        if i % 2 == 0:
            try:
                respd[_] = resp[i+1]
            except Exception as e:
                pass
        i+=1
    print(resp)
    print(respd)
    resp = {"720": None, "480": None, "1080": None, "360": None, "380": None}
    for k in respd:
        k = k.split(":", 1)[-1].replace("\"", "").replace(",avc", "|avc")
        k_ = {}
        for kt in k.split(","):
            kt = kt.split("=")
            print(kt)
            k_[kt[0]] =  kt[1]
        resp[k_["NAME"]] = k_.copy()
    json.dump(respd, open("test.json", "w", encoding="utf-8"), indent=4)
    json.dump(resp, open("test2.json", "w", encoding="utf-8"), indent=4)
    argX = f"ffmpeg -i {url} -c copy -bsf:a aac_adtstoasc \"{file}\""
    for url_det in resp:
        if url_det is not None:
            url = resp[url_det]["PROGRESSIVE-URI"]
            break
    print(argX)
    # os.system(argX)
    # os.rename(fileX, file)


def dlM(file, url, continueX="no"):
    query = f"ffmpeg -i \"{url}\" -c copy \"{file}\""
    print(query)
    os.system(query)


def decodeX(string):
    return BeautifulSoup(base64.b64decode(string).decode("utf-8"), "html.parser")


def download(url, file_details, ep_no):
    folder = anime_folder + file_details['status'] + '/' + clean(file_details["title"].replace("-", " ").strip(" "))
    file = folder + "/" + ep_no + ".mp4"
    dl = True
    continueX = "no"
    if os.path.exists(file):
        inx = optionsX(["y", "n"], ["yes", "no"], query="File already downloaded do you want to download again?")
        if inx == "yes":
            new = 1
            file = file.replace(".mp4", "X{}.mp4".format(new))
            while os.path.exists(file):
                new += 1
                file = file.replace(".mp4", "X{}.mp4".format(new))
        elif inx == "no":
            dl = False
    if dl:
        if continueX == "yes":
            if ".m3u8" in url:
                dlX(file, url, continueX)
            elif ".mp4" in url:
                dlM(file, url, continueX)
            elif "ok" in url and "ru" in url:
                download_2(url, file_details, file)
        else:
            if ".m3u8" in url:
                dlX(file, url)
            elif ".mp4" in url:
                dlM(file, url)
            elif "ok" in url and "ru" in url:
                download_2(url, file_details, file)

def download_2(obj, file_details, ep_no):
    # folder = anime_folder + file_details['status'] + '/' + clean(file_details["title"].replace("-", " ").strip(" "))
    # file = folder + "/" + ep_no + ".mp4"
    file = ep_no
    options = " -o \"" + file + \
        "\" --format mpd-3/mpd-4/mpd-5 --all-subs --embed-subs --recode-video mp4 --add-metadata "
    command = "youtube-dl {}".format(options + obj)
    print(command)
    while True:
        os.system(command)
        try:
            open(file, "rb")
            break
        except Exception as e:
            pass


def fetch(obj):
    try:
        folder = anime_folder + obj['status'] + '/' + clean(obj["title"].replace("-", " ").strip(" "))
        file = folder + "/file_data.json"
        # print(file)
        with open(file, 'r') as fr:
            # print(fr.read())
            # fr.seek(0)
            cid_kun = json.load(fr).copy()
            # print(cid_kun)
            return cid_kun
    except Exception as e:
        # print(e)
        if e:
            pass
        return {obj['title']:obj.copy()}


def store(obj):
    # obj = obj[list(obj.keys())[0]]
    obj_ = {}
    # obj.pop("Session")
    folder = anime_folder + obj['status'] + '/' + clean(obj["title"].replace("-", " ").strip(" "))
    try:
        os.makedirs(folder)
    except OSError:
        pass
    file = folder + "/file_data.json"
    try:
        with open(file, 'r') as fl:
            prev = json.load(fl)
        prev = prev[obj["title"]]
        obj_ = merge(obj, prev, ["last downloaded", "last loaded", "total episodes", "gogo_m3u8",
                     "gogoEmbed", "similar animes fk gogo", "url", "lowest", "hd", "sd", "mobile", "low", "full", "meta_url"])
        with open(file, 'w') as fl:
            json.dump({obj_["title"]: obj_}, fl, indent=4)
    except Exception as e:
        eRX(e)
        with open(file, 'w') as fl:
            json.dump({obj["title"]: obj}, fl, indent=4)


def replaces(text, items2=[], repl=""):
    x = [": </span>", ":</span>", "</span>", "</a>", "</p>", " </p", ": </span", ":</span", "</span", "</a", "<a href=",
         "<p class=\"type\"", "<span", '<p class="type"', "<script>", "</script>", "<script", "</script"]
    for i in x:
        text.replace(i, "")
    for i in items2:
        text.replace(i, repl)
    start = True
    end = True
    while start or end:
        if text != "":
            if text[0] == " ":
                text = text[1:]
            else:
                start = False
            if text != "":
                if text[-1] == " ":
                    text = text[:-1]
                else:
                    end = False
            else:
                start = end = False
        else:
            start = end = False
    return text


def clean(value):
        value = value.replace("-", " ")
        for i in list("(!%@$^&*/\\'\"}[]\'’{:;.,?<>~`=+-*#)"):
            value = value.replace(i, "")
        value = value.strip(" ")
        return value


def load_episodes_main(page):
    """
    main key "episode urls"
    """
    epi = {}
    i = page.find_all("div", {"class": "lastend"})[0].find_all("div", {"class": "inepcx"})
    start = i[0].find_all("span")[1].get_text().replace("Episode ", "").replace("Episodes ", "").replace(" to ", "-").split("-")[0]
    end = i[1].find_all("span")[1].get_text().replace("Episode ", "").replace("Episodes ", "").replace(" to ", "-").split("-")[-1]
    eps_lis = page.find_all("div", {"class":"eplister"})[0].find_all("ul")[0].find_all("li")
    for i in eps_lis:
        ep_d = i.find_all("a")[0]
        ep_url = ep_d['href']
        ep_d = ep_d.find_all("div")
        ep_no = ep_d[0].get_text().replace(" to ", "-")
        release_date = ep_d[2].get_text()
        epi["EP " + ep_no] = {"episode url": ep_url, "release date": release_date}
    return epi, start.split("[")[0].strip(" "), end.split("[")[0].strip(" ")


def load_major(page):
    alt_titles = page.find_all("span", {"class": "alter"})
    print(alt_titles)
    alt_titles = alt_titles[0].get_text().split(",")
    details = page.find_all("div", {"class": "spe"})[0]
    details = details.find_all("span")
    detail = {detail.find_all("b")[0].get_text().replace(":", ""): detail.get_text().replace(detail.find_all("b")[0].get_text() + " ", "") for detail in details}
    detail["other names"] = alt_titles
    try:
        detail["total episodes"] = detail["Episodes"]
        detail.pop("Episodes")
    except KeyError:
        pass
    detail["status"] = detail["Status"]
    detail.pop("Status")
    detail["release date"] = detail["Released on"]
    detail.pop("Released on")
    # detail["total episodes"] = detail["Episodes"]
    # detail.pop("Episodes")
    print(detail)
    return detail

def try_load(file_details, pageTL=""):
    try:
        obj = file_details
        folder = anime_folder + "Details_loaded/"+ clean(obj["title"].replace("-", " "))
        file = folder + ".json"
        try:
            with open(file, 'r') as fl:
                file_details = merge(file_details, json.load(fl), ["status", "Updated on", "total episodes"], [
                                     "release date", "last downloaded", "last loaded"])
                with open(file, "w") as fl:
                    json.dump(file_details, fl, indent=4)
                return file_details
        except Exception as e:
            if pageTL:
                file_details = merge(file_details, load_major(
                    pageTL), [], ["release date"])
            file_details = file_details
            with open(file, "w") as fl:
                json.dump(file_details, fl, indent=4)
            return file_details
    except Exception as e:
        print(e)


def get_sources(page):
    sources = {}
    sourcesX = page.find_all("select", {"class": "mirror"})[0].find_all("option")
    sources_do = {}
    for source in sourcesX:
        # print(source)
        if source.get_text() != "Select Video Server":
            text = source.get_text().lower()
            try:
                source = decodeX(source['value']).find_all("iframe")[0]['src']
            except Exception as e:
                continue
            print(source)
            if "free player" in text:
                sources['hairgen'] = source
            elif "ok.ru" in text:
                sources['ok.ru'] = source
            elif "VidPlayer" in text:
                sources['dailymotion'] = source
            elif "fembed" in text:
                sources['fembed'] = source
            elif "StreamLare" in text:
                sources['streamLare'] = source
            elif "streamsb" in text:
                sources['streamsb'] = source
            elif "doodstream" in text:
                sources['dodostream'] = source
    for source in sources:
        sources_do[source+"_download"] = get_main_source(sources[source], source)
    sources = merge(sources, sources_do, [], ["dailymotion_download", "ok.ru_download"])
    return sources


def get_main_source(url, type_):
    s = requests.Session()
    if type_ == "dailymotion":
        url = url.split("/video/")[-1]
        url = daily_motion_meta_url.format(url)
        response = s.get(url).json()['qualities']['auto'][0]['url']
        return response
    elif type_ == "ok.ru":
        # s = requests.Session()
        # response = s.get(url)
        # response = p(url)
        # metadata = json.loads(unescape(response.find_all("div", {"data-module": "OKVideo"})[0]['data-options']))
        # data_opts = json.loads(json.loads(unescape(metadata[0]))))
        # metadata['flashvars']['metadata'] = json.loads(metadata['flashvars']['metadata'])
        # json.dump(metadata, open("test.json", "w", encoding="utf-8"), indent=4)
        # print(metadata)
        user_agent = 'Chrome/92.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)'
        headers = {'User-Agent': user_agent,
                # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                # 'Accept-Encoding': 'gzip, deflate, br',
                # 'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                }
        url = "https:"+url
        while True:
            try:
                response = s.get(url, headers=headers)
                while response.status_code != 200:
                    response = s.get(url)
                    if response.status_code >= 400:
                        return None
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
        metadata = htmlparser.fromstring(response.text).cssselect('div[data-module="OKVideo"]')
        metadata = json.loads(unescape(metadata[0].get("data-options")))
        metadata['flashvars']['metadata'] = json.loads(metadata['flashvars']['metadata'])
        prior_order = {"hd": None, "sd": None, "full": None, "low": None, "lowest": None,
                       "mobile": None, "meta_url": metadata['flashvars']['metadata']['hlsManifestUrl'], "url": None, "refer": "https://ok.ru/", "major": url}
        for i in metadata['flashvars']['metadata']['videos']:
            prior_order[i['name']] = i['url']
        url_ = [prior_order[i] for i in prior_order if prior_order != None][0]
        prior_order["url"] = url_
        # print(prior_order)
        json.dump(metadata, open("test.json", "w", encoding="utf-8"), indent=4)
        json.dump(prior_order, open("test2.json", "w", encoding="utf-8"), indent=4)
        # prior_order["session"] = s
        return prior_order



    else:
        return None

def search_(term):
    """
    search khor
    """
    url = khor_url + "?s=" + term.replace(" ", "+")
    search = p(url)
    results = search.find_all("article", {"class": "bs"})
    result = {}
    pages_loaded = {}
    for resul in results:
        title = clean(resul.find_all("h2")[0].get_text()).replace(" ", "-")
        page_url = resul.find_all("a")[0]
        khor_id = page_url['rel'][0]
        page_url = page_url['href']
        statuses = resul.find_all("div", {"class": "limit"})[0].find_all("div")
        statuse = statuses[3].find_all("span")
        status = statuse[0].get_text()
        if status == "Hiatus":
            status = "Ongoing"
        type_ = statuse[1].get_text()
        img = resul.find_all("img")[0]['src']
        result[title] = {"title": title, "image cover": img, "anime details page": page_url,
                        "category": type_, "release date": "unknown",
                        "status": status, "khor_url": page_url, "khor_id": khor_id, "last downloaded": 0, "last loaded": 0}
        pages_loaded[title] = p(result[title]["khor_url"])
        # copx = result[title].copy()
        # copx.pop("page_loaded")
        result[title] = try_load(result[title], pages_loaded[title])
        print(result[title])
    selected = optionsX([i for i in range(len(ks(result)))],
                        [i + " $@ " +result[i]["release date"] for i in ks(result)]).split(" $@ ")[0]
    result[selected]["episode urls"], result[selected]["Starting ep"], result[selected]["total episodes"] = load_episodes_main(pages_loaded[selected])
    try_load(result[selected])
    start = optionsX([i for i in range(int(result[selected]["total episodes"])+1)], [i for i in range(int(result[selected]["total episodes"])+1)], print_all=False, print_only="select episode in range 0-" + str(int(result[selected]["total episodes"])))
    end = optionsX([i for i in range(int(start), int(result[selected]["total episodes"])+1)], [i for i in range(int(start), int(result[selected]
                   ["total episodes"])+1)], print_all=False, print_only="select episode in range " + str(start) + "-" +str(int(result[selected]["total episodes"])+1))
    epi_lis = ks(result[selected]["episode urls"])
    epi_lis.sort()
    epi_conv = {i.replace("EP ", "").split("[")[0].strip(" ").split("-")[0]: i for i in epi_lis}
    epi_conv2 = {i.replace("EP ", "").split("[")[0].strip(" ").split("-")[-1]: i for i in epi_lis}
    epi_conv = merge(epi_conv, epi_conv2)
    epi_d = {}
    # for i in range(int(start), int(end)+1):
    for i in ks(epi_conv):
        i_ = i.split("[")[0].strip(" ")
        if int(i_)>=int(start) and int(i_)<=int(end):
            epi_d[epi_conv[str(i)]] = result[selected]["episode urls"][epi_conv[str(i)]]
    for i in ks(epi_d):
        sources = get_sources(p(epi_d[i]["episode url"]))
        result[selected]["episode urls"][i] = merge(result[selected]["episode urls"][i], sources)
        for ki in sources:
            print(ki)
            if "_download" in ki and sources[ki] != None:
                print("\n"+ki + "\n")
                if check_one(["dailymotion"], ki):
                    print("dl daily")
                    download(sources[ki], result[selected], i.replace("EP ", ""))
                    break
                if check(["ok", "ru"], ki):
                    print("downl okru")
                    download(sources[ki]["major"], result[selected], i.replace("EP ", ""))
                    break
        store(result[selected])
    # raise ValueError

# print(download(get_main_source("https://www.dailymotion.com/embed/video/k4HNC9qyYa8H0UyQbRw", "dailymotion"), {}))
search_(input("name : "))
# m3_test = input("url : ")
# dlX("test.mp4", m3_test)
# s = requests.session()
# test1 = {'title': 'Everlasting-God-Of-Sword-2022', 'image cover': 'https://animekhor.xyz/wp-content/uploads/2022/09/Wangu-Jian-Shen-2022-www.AnimeKhor.xyz_.webp', 'anime details page': 'https://animekhor.xyz/anime/everlasting-god-of-sword-2022/',
#             'category': 'Sub', 'release date': 'unknown', 'status': 'Ongoing', 'khor_url': 'https://animekhor.xyz/anime/everlasting-god-of-sword-2022/', 'khor_id': '11756'}
# loaded = p(test1["khor_url"])
# open("test.txt", "w", encoding="utf-8").write(str(loaded))
# print(loaded)
# load_major(loaded)
# print(decodeX("PGlmcmFtZSB3aWR0aD0iNjQwIiBoZWlnaHQ9IjM2MCIgc3JjPSIvL29rLnJ1L3ZpZGVvZW1iZWQvNDIzMzA1NDA2MzIwMCIgZnJhbWVib3JkZXI9IjAiIGFsbG93PSJhdXRvcGxheSIgYWxsb3dmdWxsc2NyZWVuPjwvaWZyYW1lPg=="))
# get_main_source(
#     "https://www.dailymotion.com/player/metadata/video/k6cFtv0nKv6EApyPYwp", "dailymotion")
