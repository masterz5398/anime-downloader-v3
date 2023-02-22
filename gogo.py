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

from config import page_process as p, anime_folder, gogo_url, stream_sb_aliases, fembed_aliases, dodostream_aliases, \
    mp4upload_aliases, fK_gogo, gogo_recent_base, gogo_ajax_help, dt_format, stream_sb_dld_base, merge
from basic_funcs import optionsX, check_one, eRX, check, Int


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
                input("no download Found")
    store(file_details)
    print(file_details)


def f(t):
    srch = search_(t)
    create_file_details(srch[list(srch.keys())[0]]["anime details page"], srch)
