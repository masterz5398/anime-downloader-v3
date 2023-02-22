from bs4 import BeautifulSoup
import urllib.request
import sys
import urllib
from http.cookiejar import CookieJar

sys.path.append(r"C:\Users\shash\Desktop\programing\Project\RE")
from basic_funcs import optionsX, check_one, eRX, check, Int, unDuplicate

anime_folder = r"C:\Users\shash\Downloads\psyched\anime\downloaders\self\anime-downloader-v2\browser_pages\animes/"
series_folder = r"C:\Users\shash\Downloads\psyched\anime\downloaders\self\anime-downloader-v2\browser_pages\series/Watching/"
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
link_extractors_x_git_url = \
    "https://github.com/Devilboy04/warisleechx/blob/0737192efb00c8ae040dcf478bca8ed33fdc005e/tobrot/helper_funcs/direct_link_generator.py"
requirements_list = ["aiohttp", "aria2p", "python-dotenv", "hachoir", "Pillow", "pyrogram", "tgcrypto", "youtube_dl",
                     "hurry.filesize", "beautifulsoup4", "bs4", "lxml", "requests", "js2py", "lk21", "pybase64",
                     "cfscrape",
                     ]

gogo_ajax_help = {"type": {1: "sub", 2: "dub", 3: "chinese"}, "id": {1: "today", 2: "this week", 3: "this month"}}
date_time_format_help = {
    "%a": "Weekday, short version",
    "%A": "Weekday, full version",
    "%w": "0-6, weekday number, 0=sunday",
    "%d": "Day of month 01-31",
    "%b": "Month name, short version",
    "%B": "Month name, full version",
    "%m": "Month as a number 01-12, January is 01",
    "%y": "Year, short version",
    "%Y": "Year, full version",
    "%H": "Hour 00-23",
    "%I": "Hour 00-12",
    "%p": "AM/PM",
    "%M": "Minute 00-59",
    "%S": "Second 00-59",
    "%f": "Microsecond 000000-999999",
    "%j": "Day number of year 001-366 (366 for leap year, 365 otherwise)",
    "%U": "Week number of year, Sunday as the first day of week, 00-53",
    "%W": "Week number of year, Monday as the first day of week, 00-53",
    "%c": "Tue Dec 10 17:41:00 2019	Local version of date and time",
    "%x": "12/10/19	Local version of date (mm/dd/yy)",
    "%X": "17:41:00	Local version of time (hh:mm:ss)",
}
# print(gogo_recent_base.format(2, 1))
dt_format = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = False


def page_process(url: str, parseX=True, strXf=True, timeout=35, method="GET", addnl=None, rem=None, data=None):
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


# def loader_post():
#     cj = CookieJar()
#     opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))



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
        # print("merging lists")
        for i in obj2:
            obj1.append(i)
        return unDuplicate(obj1)
