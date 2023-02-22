# import hashlib
import json
import os
# import re
# from random import choice
# import pyaes
# import requests
# import six
from bs4 import BeautifulSoup
import sys
# from lk21 import Bypass
# from js2py import EvalJs
# import lk21
# from abc import ABC, abstractmethod
# from typing import List, Dict, Union
# import base64
# from hashlib import md5
# from requests.utils import requote_uri
# import external as helpers
# from Crypto.Cipher import AES

# import xbmc_client as xbmc

sys.path.append(r"C:\Users\shash\Desktop\programing\Project\RE\sourcePy")
from config import page_process as p, anime_folder, gogo_url, stream_sb_aliases, fembed_aliases, dodostream_aliases, \
    mp4upload_aliases, fK_gogo, gogo_recent_base, gogo_ajax_help, dt_format, stream_sb_dld_base, merge

sys.path.append(r"C:\Users\shash\Desktop\programing\Project\RE")
from basic_funcs import optionsX, check_one, eRX, check, Int


# LOGDEBUG = xbmc.LOGDEBUG
# LOGERROR = xbmc.LOGERROR
# LOGWARNING = xbmc.LOGWARNING
# LOGINFO = xbmc.LOGINFO if six.PY3 else xbmc.LOGNOTICE
#
# addonsmr = xbmcaddon.Addon('script.module.resolveurl')


"""def execute_jsonrpc(command):
    if not isinstance(command, six.string_types):
        command = json.dumps(command)
        print(command)
    # response = xbmc.executeJSONRPC(command)
    # return json.loads(response)
    return {}


def _is_debugging():
    command = {'jsonrpc': '2.0', 'id': 1, 'method': 'Settings.getSettings', 'params': {'filter': {'section': 'system',
               'category': 'logging'}}}
    js_data = execute_jsonrpc(command)
    try:
        for item in js_data.get('result', {}).get('settings', {}):
            if item['id'] == 'debug.showloginfo':
                return item['value']
    except Exception as e:
        eRX(e)
    return False


class Logger(object):
    __loggers = {}
    # __name = addonsmr.getAddonInfo('name')
    # __addon_debug = addonsmr.getSetting('addon_debug') == 'true'
    __addon_debug = False
    __debug_on = False
    __disabled = set()

    @staticmethod
    def get_logger(name=None):
        if name not in Logger.__loggers:
            Logger.__loggers[name] = Logger()

        return Logger.__loggers[name]

    def disable(self):
        if self not in Logger.__disabled:
            Logger.__disabled.add(self)

    def enable(self):
        if self in Logger.__disabled:
            Logger.__disabled.remove(self)

    def log(self, msg, level="LOGDEBUG"):
        # if debug isn't on, skip disabled loggers unless addon_debug is on
        if not self.__debug_on:
            if self in self.__disabled:
                return
            elif level == "LOGDEBUG":
                if self.__addon_debug:
                    level = "LOGINFO"
                else:
                    return

        try:
            if isinstance(msg, six.text_type) and six.PY2:
                msg = '%s (ENCODED)' % (msg.encode('utf-8'))

            # xbmc.log('%s: %s' % (self.__name, msg), level)

        except Exception as e:
            pass

    def log_debug(self, msg):
        self.log(msg, level="LOGDEBUG")

    def log_notice(self, msg):
        self.log(msg, level="LOGINFO")

    def log_warning(self, msg):
        self.log(msg, level="LOGWARNING")

    def log_error(self, msg):
        self.log(msg, level="LOGERROR")


# logger = Logger.get_logger()


class VideoServer:
    def __init__(self, name: str, embed: str) -> None:
        self.name: str = name
        self.embed: str = embed


class Video:
    def __init__(self, quality: str, is_m3u8: bool, url: str) -> None:
        self.quality: str = quality
        self.is_m3u8: bool = is_m3u8
        self.url: str = url


class Subtitle:
    subtitle_type: str = "vtt"

    def __init__(self, language: str, url: str) -> None:
        self.language: str = language
        self.url: str = url


class VideoContainer:

    def __init__(self, videos: List[Video], subtitles: List[Subtitle]) -> None:
        self.videos: List[Video] = videos
        self.subtitles: List[Subtitle] = subtitles


class VideoExtractor(ABC):
    def __init__(self, server: VideoServer) -> None:
        self.server: VideoServer = server
        self.videos: List[Video] = []
        self.subtitles: List[Subtitle] = []

    @abstractmethod
    def extract(self) -> VideoContainer:
        pass


def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data = bytes(data, "utf-8") + salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]


def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


def decrypt_export(url, key, escape=False):
    decrypt_ed = decrypt(url, key).decode('utf-8', 'ignore').lstrip(' ')
    escap_ed = requote_uri(decrypt_ed) if escape else decrypt_ed
    return escap_ed


def decrypt(encrypted, passphrase):
    # assert encrypted[0:8] == b"Salted__"
    encrypted = base64.b64decode(encrypted)
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))


class UpCloud(VideoExtractor):
    sources_base_url = "https://dokicloud.one/ajax/embed-4/getSources?id="
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    dokicloud_url = "https://raw.githubusercontent.com/consumet/rapidclown/dokicloud/key.txt"
    rabbitstream_url = "https://raw.githubusercontent.com/consumet/rapidclown/rabbitstream/key.txt"

    def extract(self) -> list[Union[dict, VideoContainer]]:
        s = requests.Session()
        embed = self.server.embed.rsplit("/", 1)[-1].rstrip("?z=")
        # print(embed)
        r: requests.Response = s.get(self.server.embed, headers=self.headers)
        r: requests.Response = s.get(self.sources_base_url + embed, headers=self.headers)
        # print(r.text)
        video_info: Dict = r.json()
        # print(video_info)
        m3u8_vid = ""
        if isinstance(video_info.get("sources"), str):
            key: str = s.get(self.rabbitstream_url).text
            # print(key)
            # decrypted_urls = decrypt_export(decrypt(video_info["sources"], key), key)
            decrypted_urls = decrypt_export(video_info["sources"], key)
            m3u8_vid = eval(decrypted_urls)[0]["file"]
            video_sources: List[Dict] = json.loads(decrypted_urls)
        else:
            video_sources: List[Dict] = video_info["sources"]

        video_tracks: List[Dict] = video_info["tracks"]
        for video_source in video_sources:
            self.videos.append(Video("", True, video_source["file"]))
        for track in video_tracks:
            if track["kind"] == "thumbnails":
                continue
            self.subtitles.append(Subtitle(track["label"], track["file"]))
        # print()
        # print(self.videos)
        # print(self.subtitles)
        return [{"file": m3u8_vid, "subs": video_info["tracks"]}, VideoContainer(self.videos, self.subtitles)]


def edit():
    pass


def get_download_link(url):
    bypasser = lk21.Bypass()
    bypasser.bypass_url(url)"""


def dlX(file, url, continueX="no"):
    argX = f"ffmpeg -i {url} -c copy -bsf:a aac_adtstoasc \"{file}\""
    print(argX)
    os.system(argX)
    # os.rename(fileX, file)


def dlM(file, url, continueX="no"):
    query = f"ffmpeg -i \"{url}\" -c copy \"{file}\""
    print(query)
    os.system(query)


def download(url, file_details, ep_no):
    folder = anime_folder + file_details['status'] + '/' + file_details["title"].replace("-", " ").strip(" ")
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
        else:
            if ".m3u8" in url:
                dlX(file, url)
            elif ".mp4" in url:
                dlM(file, url)


def fetch(obj):
    try:
        folder = anime_folder + obj['status'] + '/' + obj["title"].replace("-", " ").strip(" ")
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
    obj = obj[list(obj.keys())[0]]
    obj_ = {}
    folder = anime_folder + obj['status'] + '/' + obj["title"].replace("-", " ").strip(" ")
    try:
        os.makedirs(folder)
    except OSError:
        pass
    file = folder + "/file_data.json"
    try:
        with open(file, 'r') as fl:
            prev = json.load(fl)
        prev = prev[obj["title"]]
        obj_ = merge(obj, prev, ["last downloaded", "last loaded", "total episodes", "gogo_m3u8", "gogoEmbed", "similar animes fk gogo"])
        # print(obj_)
        with open(file, 'w') as fl:
            json.dump({obj_["title"]: obj_}, fl, indent=4)
    except Exception as e:
        eRX(e)
        with open(file, 'w') as fl:
            json.dump({obj["title"]: obj}, fl, indent=4)


def replaces(text):
    x = [": </span>", ":</span>", "</span>", "</a>", "</p>", " </p", ": </span", ":</span", "</span", "</a", "<a href=",
         "<p class=\"type\"", "<span", '<p class="type"', "<script>", "</script>", "<script", "</script"]
    for i in x:
        text.replace(i, "")
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


def search_(term):
    """
search gogoanime for term
    :param term:
    :return: {anime_name: {title: str, image cover: UrlImg, anime details page: url,
                              release date: int}}
    """
    url = gogo_url + f"search.html?keyword={term}".replace(" ", "%20")
    # page_process(url).findAll('div', {'class': 'main_body'})
    search = p(url)
    # print(search)
    # print(len(search))
    search = search.findAll('ul', {'class': 'items'})
    # print(search)
    animes = {}
    search = str(search).split("</li>")
    for anime in search:
        try:
            # print(anime)
            anime = (anime.split("<div class=\"img\">"))
            # print(anime)
            anime = anime[1].split("\n")
            # print(anime)
            anime.pop(3)
            anime.pop()
            anime_details = []
            anime_name = None
            for ani in anime:
                # print(anime_details)
                if ani == anime[1]:
                    if "category" in ani:
                        # print(ani)
                        # animes[anime_name] = ani.split("\"")[1].replace("/category/", "")
                        ani = ani.split("\"")[1].replace("/category/", "")
                    # print(ani)
                    # ani = ani.replace("<a href=\"/category/", "").split("\"")[0]
                    anime[1] = ani
                    anime_name = ani

                if ani == anime[2]:
                    ani = ani.split("=")[2]
                    ani = ani.replace("\"", "")
                    # ani = ani.replace("/", "")
                    ani = ani.replace(">", "")
                    ani = ani[0:-1]
                    anime[2] = ani
                    # print(ani)
                if "<p class=\"name\"><a href=\"" in ani:
                    ani = ani.replace("<p class=\"name\"><a href=\"", "")
                    ani = ani.split("\"")[0]
                    ani = gogo_url + ani
                if " Released:" in ani:
                    ani = ani.replace(" ", "")
                    ani = ani.split(":")[1]
                    ani = ani.replace("</p>", "")
                if "</div>" in ani:
                    pass
                elif "<p class=\"released\">" == ani:
                    pass
                else:
                    if ani:
                        anime_details.append(ani)
                    # print(ani)
                    if anime_name is not None:
                        # print(anime_details)
                        animes[anime_name] = anime_details
        except Exception as e:
            print(e)

    for AnimeNames in animes:
        details = animes.get(AnimeNames)
        animes[AnimeNames] = {
            "title": details[0], "image cover": details[1],
            "anime details page": gogo_url + "category/" + details[0],
            "release date": details[-1].replace("\t", "").replace(" Released: ", "").replace("</p>", "").replace(" ",
                                                                                                                 ""),
        }
    # print(animes)
    for anime_names in animes:
        # print(anime_names, end=" ")
        # print(_search_.get(anime_names).get("release date"))
        if animes.get(anime_names).get("release date") == "                                                      " \
                                                          "     " \
                                                          "                          ":
            animes[anime_names]["release date"] = "upcoming"
        # print(animes.get(anime_names).get("release date"))
    anime_number = 1
    key_ = list(animes.keys())
    for anime in key_:
        print(anime_number, end=" ")
        anime_number += 1
        details_anime = (animes.get(anime))
        print(details_anime.get("title") + "   " + details_anime.get("release date"))
    select_number = input("please select : ")
    quality = select_number.split("-")
    select_number = int(quality[0])
    select_number -= 1
    anime_selected = {key_[select_number]: animes.get(key_[select_number])}
    data = anime_selected
    folder_name = list(data.keys())[0].replace("-", " ")
    folder_name = folder_name.replace("-", " ")
    folder_name = folder_name.replace("\\", " ")
    folder_name = folder_name.replace("/", " ")
    folder_name = folder_name.replace("?", " ")
    folder_name = folder_name.replace("*", " ")
    folder_name = folder_name.replace("<", " ")
    folder_name = folder_name.replace("<", " ")
    folder_name = folder_name.replace("|", " ")
    folder_name = folder_name.replace("\"", " ")
    folder_name.strip(" ")
    folder_name.strip("\n")
    files_check = []
    for MainFolder, SubFolder, files in os.walk(anime_folder):
        for Sub in SubFolder:
            # print([MainFolder, SubFolder, Sub])
            # if inp.replace("-", " ").lower() in Sub.replace("-", " ").lower():
            # print(SubFolder)
            Sub_orignal = Sub
            Sub = Sub.replace("-", " ")
            if Sub == folder_name:
                files_check.append(fr"{MainFolder}\{Sub_orignal}")
    a = 1
    print("existing folders are :")
    for file in files_check:
        print(a, ". ", file)
        a += 1
    inp = input("press enter to continue...(type exit to stop)")
    if inp == "exit":
        os.kill(os.getpid(), 9)
    # print(anime_selected)
    # print(animes)
    if len(quality) == 2:
        anime_selected[list(anime_selected.keys())[0]]["quality"] = "normal"
        print("low/normal quantity downloading")
    return anime_selected


def create_file_details(url, det=None):
    """
    file_details format {ext_pg_tit: {tit:ext_pg_tit, image cover:img, anime details page:cat_pg, release date:dt,
                        release time:sen yr ani, status:status, other_nms: nms, ttl_eps:int, lst_dld:int, quality:normal
                        , genres:[], ep_urls:{ep_url:ep_pg, gogoload:download_gogo, sbplay: SB_stream...}}}
    :return:
    """
    # details = ""
    url = url.replace("//", "/")
    url = url.replace("https:/", "http://")
    # print(url)
    fl_mn = url.split("/")[-1].replace("/category/", "")
    # print(fl_mn)
    file_details = {fl_mn: {"title": fl_mn, "image cover": ""}}
    pg: BeautifulSoup = p(url)
    # print(pg)
    x = pg.find_all(class_="type")
    y = []
    zy = []
    imgs = []
    z = pg.find_all("img", src=True)
    for zx in z:
        # print(zx['src'])
        if ".png" in zx['src']:
            imgs.append(zx['src'])
        elif ".jpg" in zx['src']:
            imgs.append(zx['src'])
        elif ".jpeg" in zx['src']:
            imgs.append(zx['src'])
    to_remove = []
    for i in range(len(imgs)):
        if "cover" in imgs[i]:
            continue
        elif "images/anime" in imgs[1]:
            continue
        else:
            to_remove.append(i - len(to_remove))
    for i in to_remove:
        imgs.remove(imgs[i])

    for i in x:
        if "Plot Summary:" in i.find_all("span")[0].get_text():
            details = replaces(str(i.get_text()).replace("Plot Summary:", ""))
        z = i.find_all("a", href=True)
        for zx in z:
            y.append(zx.get_text().replace(", ", ""))
            # print(zx.get_text())
            if "https:" in zx['href']:
                zy.append(zx['href'])
            else:
                zy.append(gogo_url + zx['href'])
    # print(y)
    # print(zy)
    # print(x)
    genres = []
    for i in range(1, len(y) - 1):
        genres.append(y[i])
    # print(genres)
    # for i in x:
    #     i = str(i).replace("\n", "")
    # print(i)
    # print("")
    # print("--------------------------------" * 5)
    other_names = []
    for i in x:
        ic = 0
        i = str(i).replace("\n", " ").split(">")
        # print(replaces(i))
        for j in i:
            ic += 1
            if "Other name:" in j:
                i[ic] = replaces(i[ic])
                other_names = i[ic].replace(" </p", "").replace("</p", "").split(";")
            # j = replaces(j)
            # print(replaces(j + "\n" + "-" * 20))
        # print(replaces(i.split(">")[2]))
        # print("\n" * 3 + "-" * 50)
    # print(imgs)
    q = pg.findAll("a", class_="active")
    ep_end = q[0]["ep_end"]
    start = q[0]["ep_start"]
    file_details[fl_mn]["image cover"] = imgs[0]
    # print(det)
    # print(file_details)
    file_details[fl_mn]["last downloaded"] = 0
    file_details[fl_mn]["last loaded"] = 0
    file_details[fl_mn]["anime details page"] = det[fl_mn]["anime details page"]
    file_details[fl_mn]["release date"] = det[fl_mn]["release date"]
    file_details[fl_mn]["release time"] = y[0]
    file_details[fl_mn]["description"] = details
    file_details[fl_mn]["status"] = y[-1]
    file_details[fl_mn]["other names"] = other_names
    file_details[fl_mn]["total episodes"] = int(ep_end)
    fetched_ = fetch(file_details[fl_mn])[fl_mn]
    file_details[fl_mn]["last downloaded"] =  fetched_["last downloaded"] # TODO: get last downloaded episode
    file_details[fl_mn]["last loaded"] = fetched_["last loaded"]  # TODO: get last loaded episode
    file_details[fl_mn]["Starting ep"] = start
    file_details[fl_mn]["quality"] = "normal"
    file_details[fl_mn]["genres"] = genres
    # print(file_details)
    # print("\n"*3)
    # print(fetched_)
    file_details[fl_mn]["episode urls"] = {}
    x = pg.find_all("input", class_="movie_id")
    xyx = pg.find_all("input", class_="default_ep")[0]['value']
    xzx = pg.find_all("input", class_="alias_anime")[0]['value']
    x = x[0]['value']
    file_details[fl_mn]["movie_id"] = x
    file_details[fl_mn]["default_ep"] = xyx
    file_details[fl_mn]["alias_anime"] = xzx
    xx = "https://ajax.gogo-load.com/ajax/load-list-episode?ep_start={}&ep_end={}&id={}&default_ep={}&alias={}"
    # print(fetch(file_details))
    # print(list(file_details.keys()))
    # print(fetch(file_details)[list(file_details.keys())[0]])
    print("total: ", file_details[fl_mn]["total episodes"])
    print("last: ", file_details[fl_mn]["last downloaded"])
    stt = Int(input("start: "))
    # file_details[fl_mn]["last downloaded"] = stt
    edd = Int(input("end: "))
    if edd == "n":
        stt = Int(input("start: "))
        edd = Int(input("end: "))
    file_details[fl_mn]["last downloaded"], file_details[fl_mn]["last loaded"] = stt, edd
    ulr = xx.format(stt, edd, x, xyx, xzx)
    # print(ulr)
    x = p(ulr)
    # print(x)
    x = x.find_all("li")
    # print(x)
    # print(x)
    eps = {}
    for i in x:
        xy = gogo_url + i.find_all("a")[0]['href']
        xy = xy.replace("/ /", "/")
        xz = i.find_all("div", class_="name")[0].get_text().replace("<span>EP</span> ", "")
        eps[xz] = xy
    # print(eps)
    ks = list(eps.keys())
    ks.sort()
    for i in ks:
        file_details[fl_mn]["episode urls"][i] = {"episode url": eps[i], }
    dX = []
    for i in ks:
        x = p(eps[i])
        d = x.find_all(class_="dowloads")[0].find_all("a")[0]['href']
        dm = [i['data-video'] for i in x.find_all(class_="anime_muti_link")[0].find_all("a")]
        # print(dm)
        dX.append(d)
        file_details[fl_mn]["episode urls"][i]["gogoloadDownload"] = d
        file_details[fl_mn]["episode urls"][i]["gogo_id"] = d.split("id=")[1].split("&")[0]
        unknown = []
        for q in dm:
            try:
                if "streaming.php" in q:
                    file_details[fl_mn]["episode urls"][i]["gogoStream"] = q
                elif "embedplus" in q:
                    file_details[fl_mn]["episode urls"][i]["gogoEmbed"] = q
                elif q.split("/")[2] in stream_sb_aliases:
                    file_details[fl_mn]["episode urls"][i]["streamsb"] = q
                elif q.split("/")[2] in fembed_aliases:
                    file_details[fl_mn]["episode urls"][i]["fembed"] = q
                elif q.split("/")[2] in dodostream_aliases:
                    file_details[fl_mn]["episode urls"][i]["dodostream"] = q
                elif q.split("/")[2] in mp4upload_aliases:
                    file_details[fl_mn]["episode urls"][i]["mp4upload"] = q
                else:
                    unknown.append(q)
                    file_details[fl_mn]["episode urls"][i]["unknown"] = unknown.copy()
            except Exception as e:
                if e:
                    pass
        # print(d)
    p_sim = file_details[fl_mn]["anime details page"].split("/category/")[-1]
    p_sim = "https://gogoanime.la/anime/" + p_sim
    try:
        p_sim_p: BeautifulSoup = p(p_sim, 15)
        xyxS = p_sim_p.find_all(class_="fs-md fw-400 c-aba")
        similar = [xsxS.get_text() for xsxS in xyxS]
    except Exception as e:
        eRX(e)
        similar = [""]
    file_details[fl_mn]["similar animes fk gogo"] = similar
    #      pgX = p(d)
    # print("storing.....")
    store(file_details)
    xyxG = [int(str(epx).lower().replace("ep ", "")) for epx in ks]
    # print(xyxG)
    xyxG.sort()

    if len(xyxG) != 0:
        for i in xyxG:
            xx1 = "https://gogoanime.la/stream/main.php?id={}".format(
                file_details[fl_mn]["episode urls"]["EP " + str(i)]["gogo_id"])
            # print("\n"*5, xx1, "\n"*5)
            m3u8_file = ""
            # print(xx1)
            pgy = p(xx1, 15)
            # print(pgy)
            # print(pgy.find_all("script"))
            for iy in pgy.find_all("script"):
                if "file" in iy.get_text():
                    iy = replaces(str(iy.get_text())).split("\n")
                    for iyx in iy:
                        lxs = [".m3u8", "file", ]
                        lxs2 = [".m3u8", "cdn", "go"]
                        lxs3 = [".mp4", "file"]
                        lxs4 = [".m3u8", "file"]
                        if check(lxs, iyx):
                            # print(iyx)
                            # print(replaces(iyx.split("\"")[1]))
                            m3u8_file = replaces(iyx.split("\"")[1])
                            break
                            # print(m3u8_file)
                        elif check(lxs2, iyx):
                            print(iyx)
                            input("please setup this section")
                        elif check(lxs3, iyx):
                            iyx = iyx.split("\"")[1]
                            if "hd" in iyx.lower():
                                print(iyx)
                                m3u8_file = iyx
                            elif m3u8_file == "":
                                print(iyx)
                                m3u8_file = iyx
                            # m3u8_file = iyx
                            break
                        elif check(lxs4, iyx):
                            print(iyx)
                            input("please setup this section")
            file_details[fl_mn]["episode urls"]["EP " + str(i)]["gogo_m3u8"] = m3u8_file
            # store(file_details)
            if m3u8_file != "":
                print("downloading episode: ", i)
                store(file_details)
                download(m3u8_file, file_details[fl_mn], str(i))
                file_details[fl_mn]["last downloaded"] = int(i)
                store(file_details)
                os.system("cls")
            elif m3u8_file == "":
                print("no download Found")
            #     print("bypassing")
            #     uxr = file_details[fl_mn]["episode urls"]["EP " + str(i)]["streamsb"].replace("/e/", "/d/").replace(
            #         "streamsss.net", "streamsb.net")
            #     print(uxr)
            #     m3u8_file = streamSb(uxr)
            #     print(m3u8_file)
            #     if not m3u8_file:
            #         gogo(file_details[fl_mn]["episode urls"]["EP " + str(i)])
                # break

    # x = pg.find_all("div", id="load_ep")
    # for episode in range(file_details[fl_mn]["last loaded"]+1, file_details[fl_mn]["total episodes"]):
    #     pass
    # print(det)
    store(file_details)
    print(file_details)


def f(t):
    srch = search_(t)
    create_file_details(srch[list(srch.keys())[0]]["anime details page"], srch)


'''class DirectDownloadLinkException(Exception):
    """No method found for extracting direct download link from the http link"""
    pass
'''

'''def gogo(url):
    pgx = p(url)
    for i in pgx.find_all("script"):
        if i["data-name"] == "episode":
            x = decrypt_export(i["data-value"], 0)
            print(x)'''
            # y = 'https://{0}/encrypt-ajax.php?id={1}&alias={2}'.format("gogohd.pro", encrypt(media_id), params)

'''
def streamSb(url):
    pgx = p(url)
    dl_page = pgx.find_all("a")
    avb = []
    best = None
    for a in dl_page:
        if check_one(["1080", "720", "480"], a.get_text()):
            avb.append(a)
            if "1080" in a.get_text():
                best = "1080"
            elif "720" in a.get_text():
                if not check_one(["1080"], best):
                    best = "720"
            elif "480" in a.get_text():
                if not check_one(["1080", "720"], best):
                    best = "480"
            elif "360" in a.get_text():
                if not check_one(["1080", "720", "480"], best):
                    best = "360"
    for i in avb:
        if best in i.get_text():
            vrbXs = i["onclick"].split("(")[-1].split(")")[0].replace("'", "").split(",")
            ulrX = stream_sb_dld_base.format(vrbXs[0], vrbXs[1], vrbXs[2])
            print(ulrX)
            pgx = p(ulrX)
    dl_link = [i["href"] for i in pgx.find_all("a") if check(["download", "video"], i.get_text().lower())]
    print(dl_link)
    return dl_link'''


'''class common:
    IE_USER_AGENT = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
    OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 OPR/67.0.3575.97'
    IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Safari/604.1'
    ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 9; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36'
    EDGE_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
    CHROME_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4136.7 Safari/537.36'
    SAFARI_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15'
    # SMR_USER_AGENT = 'ResolveURL for Kodi/%s' % (addon_version)

    # Quick hack till I decide how to handle this
    _USER_AGENTS = [FF_USER_AGENT, OPERA_USER_AGENT, EDGE_USER_AGENT, CHROME_USER_AGENT, SAFARI_USER_AGENT]
    RAND_UA = choice(_USER_AGENTS)

    @staticmethod
    def log_file_hash(path):
        try:
            with open(path, 'r') as f:
                py_data = f.read()
        except:
            py_data = ''

        logger.log('%s hash: %s' % (os.path.basename(path), hashlib.md5(py_data).hexdigest()))

    @staticmethod
    def file_length(py_path, key=''):
        try:
            with open(py_path, 'r') as f:
                old_py = f.read()
            if key:
                old_py = common.encrypt_py(old_py, key)
            old_len = len(old_py)
        except:
            old_len = -1

        return old_len

    @staticmethod
    def decrypt_py(cipher_text, key):
        if cipher_text:
            try:
                scraper_key = hashlib.sha256(key).digest()
                IV = '\0' * 16
                decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
                plain_text = decrypter.feed(cipher_text)
                plain_text += decrypter.feed()
                if 'import' not in plain_text:
                    plain_text = ''
            except Exception as e:
                logger.log_warning('Exception during Py Decrypt: %s' % (e))
                plain_text = ''
        else:
            plain_text = ''

        return plain_text

    @staticmethod
    def encrypt_py(plain_text, key):
        if plain_text:
            try:
                scraper_key = hashlib.sha256(key).digest()
                IV = '\0' * 16
                decrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(scraper_key, IV))
                cipher_text = decrypter.feed(plain_text)
                cipher_text += decrypter.feed()
            except Exception as e:
                logger.log_warning('Exception during Py Encrypt: %s' % (e))
                cipher_text = ''
        else:
            cipher_text = ''

        return cipher_text


# class helpers:


def fembed9(self, host, media_id):
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA}
        r = self.net.http_GET(web_url, headers=headers)
        if 'this video is unavailable' not in r.content:
            if r.get_url() != web_url:
                host = re.findall(r'(?://|\.)([^/]+)', r.get_url())[0]
                web_url = self.get_url(host, media_id)
            headers.update({'Referer': web_url})
            api_url = 'https://{0}/api/source/{1}'.format(host, media_id)
            r = self.net.http_POST(api_url, form_data={'r': '', 'd': host}, headers=headers)
            if r.get_url() != api_url:
                api_url = 'https://www.{0}/api/source/{1}'.format(host, media_id)
                r = self.net.http_POST(api_url, form_data={'r': '', 'd': host}, headers=headers)
            js_result = r.content

            if js_result:
                js_data = json.loads(js_result)
                if js_data.get('success'):
                    sources = [(i.get('label'), i.get('file')) for i in js_data.get('data') if i.get('type') == 'mp4']
                    sources = helpers.sort_sources_list(sources)
                    rurl = helpers.pick_source(sources)
                    str_url = helpers.get_redirect_url(rurl, headers=headers)
                    headers.update({'verifypeer': 'false'})
                    return str_url + helpers.append_headers(headers)

        return ('Video not found')


def fembed(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*fembed\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No Fembed links found`\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_fembed(text_url)
    lst_link = []
    count = len(dl_url)
    for i in dl_url:
        lst_link.append(dl_url[i])
    return lst_link[count - 1]


def mxplayer(url: str) -> str:
    """ mxplayer direct links generator """
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*mxplayer\.in\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No mxplayer links found`\n")
    page = BeautifulSoup(requests.get(text_url).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    return dl_url


def streamsb_2(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*streamsb\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No streamsb links found`\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_sbembed(text_url)
    lst_link = []
    count = len(dl_url)
    for i in dl_url:
        lst_link.append(dl_url[i])
    print(lst_link)
    return lst_link[count - 1]


def fembed720(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*layarkacaxxi\.icu\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No Fembed links found`\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_url(text_url)
    return dl_url["720p/mp4"]


def hxfile(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*hxfile\.co\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No HXFile links found`\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_url(text_url)
    return dl_url


def anon(url: str) -> str:
    dl_url = ''
    try:
        text_url = re.findall(r'\bhttps?://.*anonfiles\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No anonfiles links found`\n")
    bypasser = lk21.Bypass()
    dl_url = bypasser.bypass_url(text_url)
    return dl_url


def zippy_share(url: str) -> str:
    link = re.findall("https:/.(.*?).zippyshare", url)[0]
    response_content = (requests.get(url)).content
    bs_obj = BeautifulSoup(response_content, "lxml")

    try:
        js_script = bs_obj.find("div", {"class": "center", }).find_all(
            "script"
        )[1]
    except Exception as e:
        eRX(e)
        js_script = bs_obj.find("div", {"class": "right", }).find_all(
            "script"
        )[0]

    js_content = re.findall(r'\.href.=."/(.*?)";', str(js_script))
    js_content = 'var x = "/' + js_content[0] + '"'

    evaljs = EvalJs()
    setattr(evaljs, "x", None)
    evaljs.execute(js_content)
    js_content = getattr(evaljs, "x")

    return f"https://{link}.zippyshare.com{js_content}"


def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        text_url = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No MediaFire links found`\n")
    page = BeautifulSoup(requests.get(text_url).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    return dl_url


def get_m3u8_rabbitstream(id_):
    url = "https://rabbitstream.net/embed-5/{}".format(id_)
    print(url)
    headers = {
        "referer": "https://www.2embed.to/",
    }
    params = {
        'id': id_.split("?")[0],
        '_number': '1',
        'sId': 'tMK9W5pbb5PYDSCEuuMt',
    }
    resp = requests.get("https://rabbitstream.net/ajax/embed-5/getSources", headers=headers, params=params).json()
    print(resp)


def get_vidcloud_stream(id_, m3u8=False):
    try:
        media_server = (
            BeautifulSoup(
                requests.get(
                    "https://www.2embed.to/embed/imdb/movie?id={}".format(id_),
                    headers={"user-agent": "Mozilla/5.0"},
                ).text,
                "html.parser",
            )
                .find("div", class_="media-servers dropdown")
                .find("a")["data-id"]
        )
        recaptcha_resp = requests.get(
            "https://recaptcha.harp.workers.dev/?anchor=https%3A%2F%2Fwww.google.com%2Frecaptcha%2Fapi2%2Fanchor%3Far%3D1%26k%3D6Lf2aYsgAAAAAFvU3-ybajmezOYy87U4fcEpWS4C%26co%3DaHR0cHM6Ly93d3cuMmVtYmVkLnRvOjQ0Mw..%26hl%3Den%26v%3DPRMRaAwB3KlylGQR57Dyk-pF%26size%3Dinvisible%26cb%3D7rsdercrealf&reload=https%3A%2F%2Fwww.google.com%2Frecaptcha%2Fapi2%2Freload%3Fk%3D6Lf2aYsgAAAAAFvU3-ybajmezOYy87U4fcEpWS4C"
        ).json()["rresp"]
        vidcloudresp = requests.get(
            "https://www.2embed.to/ajax/embed/play",
            params={"id": media_server, "_token": recaptcha_resp},
        )
        vid_id = vidcloudresp.json()["link"].split("/")[-1]
        rbstream = "https://rabbitstream.net/embed/m-download/{}".format(
            vid_id)
        soup = BeautifulSoup(requests.get(rbstream).text, "html.parser")
        return [
            a["href"] for a in soup.find("div", class_="download-list").find_all("a")
        ] if not m3u8 else vid_id
    except:
        return None'''

# xnx = UpCloud(VideoServer("dokicloud", "https://dokicloud.one/embed-4/0YKEOvgSy4YH")).extract()
# print(xnx)
