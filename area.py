import requests
import re
from ast import literal_eval

PROVINCE_URL = "https://misc.360buyimg.com/jdf/1.0.0/ui/area/1.0.0/area.js"
SEARCH_URL = "https://fts.jd.com/area/get"

def get_province():
    data = {}
    html = requests.get(PROVINCE_URL).text

    find_str = re.search(r'a\.each\(\"(.*?)\"', html)
    find_str = find_str.group(1)

    for i in find_str.split(","):
        province_slice = i.split("|")
        id = int(province_slice[1])
        name = province_slice[0].encode('utf-8').decode('unicode_escape')

        data[id] = name
    return data

def get_city(province_id):
    data = {}
    html = requests.get(PROVINCE_URL).text

    find_str = re.search(r'a\.each\(\{(.*?)\}\,', html)
    find_str = "{"+find_str.group(1)+"}"

    for key, value in literal_eval(find_str).items():
        sub_dict = {}
        for pair in value.split(','):
            if "|" in pair:
                area, num = pair.split('|')
                sub_dict[num] = area
        data[key] = sub_dict
    if province_id:
        return data[province_id]
    return data
    
def search(id):
    params = {
        "fid": id
    }
    resp = requests.get(url=SEARCH_URL, params=params)
    transform = lambda x: {item['id']: item['name'] for item in x}
    return transform(resp.json())
