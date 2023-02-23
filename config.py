from bs4 import BeautifulSoup
import urllib.request
import sys
import urllib

from basic_funcs import optionsX, check_one, eRX, check, Int, unDuplicate

anime_folder = r"C:\Users\USER/" # downloads to anime_folder + anime-name
series_folder = r"C:\Users\USER/" # the downloader has not been put
gogo_url = r"https://www1.gogoanime.bid/"
khor_url = r"https://animekhor.xyz/"
khor_query_url = r"https://animekhor.xyz/wp-admin/admin-ajax.php"
daily_motion_meta_url = r"https://www.dailymotion.com/player/metadata/video/{}"
stream_sb_aliases = ["streamsss.net", ]
fembed_aliases = ["fembed9hd.com", ]
dodostream_aliases = ["dood.wf", ]
mp4upload_aliases = ["www.mp4upload.com", ]
fK_gogo = "https://gogoanime.la/"
gitX_file = anime_folder + "universal_animes.json"
gitX_url = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json"
gogo_recent_base = "https://ajax.gogo-load.com/ajax/page-recent-release.html?page={}&type={}"
gogo_analytics_base = "https://ajax.gogo-load.com/anclytic-ajax.html?id={}"
sflix_base = "https://sflix.se/"
sflix_episodes_alternate = "https://bingewatch.to/ajax/movie/episode/servers/{}"
rapidStreamDownloadLink_base = "https://rabbitstream.net/embed/m-download/{}"  # .format(id)
sflix_movie_vids = sflix_base + "ajax/movie/episodes/{}"  # .format(data-episode_for series, data-id_for movie)returns video servers *//
sflix_episode_vids = sflix_base + "ajax/v2/tv/seasons/{}"  # .format(data-id)  returns seasons list
sflix_season_vids = "https://bingewatch.to/ajax/movie/season/episodes/{}"
get_source_for_ep_id = "https://bingewatch.to/ajax/movie/episode/server/sources/{}"
stream_sb_dld_base = "https://streamsb.net/dl?op=download_orig&id={}&mode={}&hash={}"
requirements_list = ["aiohttp", "aria2p", "python-dotenv", "hachoir", "Pillow", "pyrogram", "tgcrypto", "youtube_dl",
                     "hurry.filesize", "beautifulsoup4", "bs4", "lxml", "requests", "js2py", "lk21", "pybase64",
                     "cfscrape",
                     ] # some have not been used in the added files and some are missing as i didnt update this part

gogo_ajax_help = {"type": {1: "sub", 2: "dub", 3: "chinese"}, "id": {1: "today", 2: "this week", 3: "this month"}}
# print(gogo_recent_base.format(2, 1))
dt_format = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = False # dosent matter


def page_process(url: str, parseX=True, strXf=True, timeout=35, method="GET", addnl=None, rem=None, data=None): # very important
    """
    :return soup data html parser
    :var url url of the page to be loaded
load page and return the beautiful soup processed data
    """
    print(url)
    user_agent = 'Chrome/92.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)'
    headers = {'User-Agent': user_agent,
                # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                # 'Accept-Encoding': 'gzip, deflate, br',
                # 'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                }
    # if addnl is not None:
    #     for i in addnl:
    #         headers[i] = addnl[i]
    # if addnl is not None:
    #     for i in rem:
    #         headers.pop(i)
    request = urllib.request.Request(url=url, headers=headers, method=method)
    response = ""
    try_ = 0
    while (response == "") and (try_ < 3):
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except ConnectionResetError:
            pass
        except KeyboardInterrupt:
            break
        except urllib.error.URLError:
            pass
        except Exception as e:
            print(try_)
            eRX(e)
            print(e)
            try_ += 1
    data = response.read()
    if parseX:
        soup = BeautifulSoup(data, "html.parser")
    else:
        soup = data
        if strXf:
            soup = soup.decode('utf-8')
    # print(data)
    open("test.html", "w", encoding="utf-8").write(str(data))
    return soup


def ks(obj):
    return list(obj.keys())


def merge(obj1, obj2, first_prior=[None, ], second_prior=[None, ]):
    if type(obj1) == type(obj2) == dict:
        # print("Merging dict")
        # input(obj1)
        # input(obj2)
        keys = merge(ks(obj1), ks(obj2))
        # input(merge(ks(obj1), ks(obj2)))
        for key in keys:
            if key in ks(obj1) and key not in ks(obj2):
                obj1[key] = obj1[key]
                continue
            elif key in ks(obj2) and key not in ks(obj1):
                obj1[key] = obj2[key]
                continue
            else:
                if (type(obj1[key]) == type(obj2[key]) == list) or (type(obj1[key]) == type(obj2[key]) == dict):
                    obj1[key] = merge(obj1[key], obj2[key], first_prior)
                    continue
                else:
                    if key in first_prior:
                        obj1[key] = obj1[key]
                    elif key in second_prior:
                        obj1[key] = obj2[key]
                    elif obj1[key] != obj2[key]:
                        print("Warning Data Changed/Wrong")
                        print("object : ", key)
                        obj1[key] = optionsX(["1", "2"], [obj1[key], obj2[key]])
                    continue
        return obj1
    elif type(obj1) == type(obj2) == list:
        for i in obj2:
            obj1.append(i)
        return unDuplicate(obj1)
