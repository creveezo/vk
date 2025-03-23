import requests
from datetime import datetime
import pandas as pd
import json
from decouple import config


TOKEN = config('TOKEN')
extra_total = '''bdate, can_post, city, followers_count, has_photo, sex, games, interests, movies, music, occupation, online, personal, relation, universities, is_verified'''
CURR = extra_total
VERSION = '5.199'


# Примеры ввода:
# https://vk.com/dodo
# dodo
# -53484080
# 53484080
def groupname_fix(user_input):
    if "/" in user_input:
        user_input = input[user_input.rfind('/') + 1:]
    if int(user_input) < 0:
        return int(user_input) * (-1)
    return user_input


def basic_info(user_input):
    info = 'https://api.vk.com/method/groups.getById'

    data = requests.get(
        info,
        params={
            'group_id': user_input,
            'access_token': TOKEN,
            'v': VERSION,
            'fields': 'name, photo_100, members_count'
        }
    ).json()

    return data


def execute(comm_name, offset):
    ex = 'https://api.vk.com/method/execute'

    data = requests.post(ex,
                         {
                             "code": f"var pub = \"{comm_name}\";"
                                     f"var off = {offset};"
                                     "var offset = 0;"
                                     "var allIds = [];"
                                     "while (offset < 2000 + off) {;"
                                     "var members = (API.groups.getMembers({\"group_id\": pub, \"v\": \"5.130\", "
                                     "\"sort\": \"id_asc\", \"count\": \"500\", \"offset\": offset + off}).items);"
                                     f'var a = API.users.get({{"user_ids": members, "fields": \"{CURR}\", "v": \"{VERSION}\"}});'
                                     "allIds = allIds + a;"
                                     "offset = offset + 500;"
                                     "};"
                                     "return allIds;",
                             "access_token": TOKEN,
                             "v": VERSION,
                         }).json()
    return data


# Выгрузить список пользователь в сообществе
def list_of_members(comm_name):
    data = execute(comm_name, 0)
    try:
        if data['error']:  # обрабатываем несуществующие сообщества
            print(data)
            return -1
        if data['execute_errors']:
            return -2
    except KeyError:
        return data


# преобразование колонки с интересами в общий словарь.
# учитываются общие интересы 3х и более людей
def column_to_interest_list(column):
    interests = column.str.lower().value_counts().to_dict()
    res = {}
    for i in interests:
        for hobby in i.split(', '):
            if len(hobby.strip("!.,)=: ")) > 1:
                res.setdefault(hobby.strip("!.,)=: "), 0)
                res[hobby.strip("!.,)=: ")] += 1
    final = {key: value for key, value in res.items() if value > 2}
    if not len(final):
        return -1
    return final


def bdate_preprocess(column):
    current_date = datetime.now()
    res_age = {}
    res_month = {}
    has_bithdate = 0
    bdate = column.str.lower().value_counts().to_dict()
    for i in bdate:
        if i.count('.') == 2:
            birth_date = datetime.strptime(i, "%d.%m.%Y")
            age = current_date.year - birth_date.year
            if current_date.month < birth_date.month or (
                    current_date.month == birth_date.month and current_date.day < birth_date.day):
                age -= 1
            if age < 100:
                res_age.setdefault(age, 0)
                res_age[age] += bdate[i]
        m_num = i.split('.')[1]
        res_month.setdefault(int(m_num), 0)
        res_month[int(m_num)] += bdate[i]
        has_bithdate += bdate[i]
    res_res_age = {}
    for i in range(min(res_age.keys()), min(100, max(res_age.keys()))):
        try: res_res_age[i] = res_age[i]
        except: res_res_age[i] = 0
    return {'age': res_res_age, 'bdate_months': res_month, 'has_bdate': has_bithdate}


def rounding(number):
    # Определяем порядок величины числа (сколько раз делим на 10)
    power_of_ten = 10 ** (len(str(number)) - 1)
    # Округляем число до старшего разряда
    rounded_number = (number // power_of_ten) * power_of_ten
    return rounded_number


def transform_follower_count(count):
    if count >= 50000:
        return 50000
    elif count == -1:
        return -1
    elif count < 100:
        return 10
    else:
        return rounding(count)


def perfect_dict():
    res = {10: 0}
    for i in range(100, 901, 100):
        res[i] = 0
    for j in range(1000, 9001, 1000):
        res[j] = 0
    for k in range(10000, 50001, 10000):
        res[k] = 0
    return res


def followers(column):
    column = column.fillna(-1)
    column = column.astype(int)

    d = column.apply(transform_follower_count).value_counts().to_dict()
    d = dict(sorted(d.items()))
    p_dict = perfect_dict()
    fin = {key: d[key] if key in d else p_dict[key] for key in p_dict}
    new_dict = {}
    followers = 0
    for key, value in fin.items():
        if key == 10:
            new_key = "<100"
        else:
            # Преобразуем float в int, затем в str и добавляем "+"
            new_key = str(key) + "+"
        new_dict[new_key] = value
        followers += value
    return {'followers_count': new_dict, 'has_followers_info': followers}


# категория personal
political = {1: 'коммунистические', 2: 'социалистические', 3: 'умеренные',
             4: 'либеральные', 5: 'консервативные', 6: 'монархические',
             7: 'ультраконсервативные', 8: 'индифферентные',
             9: 'либертарианские'}

smoking = {1: 'резко негативное', 2: 'негативное', 3: 'компромиссное',
           4: 'нейтральное', 5: 'положительное'}

people_main = {1: 'ум и креативность', 2: 'доброта и честность',
               3: 'красота и здоровье', 4: 'власть и богатство',
               5: 'смелость и упорство', 6: 'юмор и жизнелюбие'}

life_main = {1: 'семья и дети', 2: 'карьера и деньги',
             3: 'развлечения и отдых', 4: 'наука и исследования',
             5: 'совершенствование мира', 6: 'саморазвитие',
             7: 'красота и искусство', 8: 'слава и влияние'}

transcript = {'political': political, 'smoking': smoking, 'alcohol': smoking,
              'people_main': people_main, 'life_main': life_main}


def personal_pre(column):
    a = column.to_list()
    res = {}
    for i in a:
        if isinstance(i, type({})):
            for j in i:
                if j in ["langs_full", 'inspired_by', 'religion', 'religion_id']:
                    pass
                else:
                    res.setdefault(j, {})
                    if isinstance(i[j], type([])):
                        for k in i[j]:
                            res[j].setdefault(k, 0)
                            res[j][k] += 1
                    else:
                        res[j].setdefault(i[j], 0)
                        res[j][i[j]] += 1

    res_fin = {}
    for cat in transcript:
        res_fin[cat] = {}
        for num, tr in transcript[cat].items():
            if cat in res:
                if num in res[cat]:
                    res_fin[cat][tr] = res[cat][num]
                else:
                    res_fin[cat][tr] = 0
            else:
                res_fin[cat][tr] = 0
    res_fin['langs'] = res['langs']

    return res_fin


def city_pre(column):
    a = column.dropna().to_list()
    res = {}

    for i in a:
        if isinstance(i, type({})):
            res.setdefault(i['title'], 0)
            res[i['title']] += 1

    return dict(sorted(res.items(), key=lambda item: item[1], reverse=True)[:20])


# категория university
def other_count(d):
    count_ones = sum(1 for v in d.values() if v == 1)
    d = {k: v for k, v in d.items() if v > 1}
    d["другое"] = count_ones
    d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
    return first_20(d)


def first_20(d):
    n = 1
    res = {}
    for k, v in d.items():
        if n <= 16:
            res[k] = v
            n += 1
        else:
            res["другое"] += v
    return res


def uni_pre(column):
    a = column.fillna(0).to_list()
    faculty = {}
    name = {}
    grad = {2000: 0}
    for uni in a:
        if isinstance(uni, type([])):
            for i in uni:
                try:
                    faculty.setdefault(i['faculty_name'].strip(), 0)
                    name.setdefault(i['name'].strip(), 0)
                    grad.setdefault(i['graduation'], 0)
                    faculty[i['faculty_name'].strip()] += 1
                    name[i['name'].strip()] += 1
                    grad[i['graduation']] += 1
                except KeyError:
                    pass
    faculty = other_count(faculty)
    name = other_count(name)
    earliest_year = min(grad, key=grad.get)
    latest_year = max(grad, key=grad.get)
    curr_year = datetime.now().year
    graduation_year = {i: 0 for i in range(earliest_year, max(curr_year, latest_year) + 1)}
    for year in graduation_year:
        if year in grad:
            graduation_year[year] = grad[year]

    return {'faculty': faculty, 'name': name, 'graduation_year': graduation_year}


def occ_pre(column):
    a = column.to_list()
    res = {}
    for i in a:
        if isinstance(i, type({})):
            res.setdefault(i['type'], 0)
            res[i['type']] += 1
    return res


def preprocess_dataframe(df):
    statistics = {'total': len(df), 'online_rn': len(df.loc[df.online == 1]),
                  'no_photo': len(df.loc[df.has_photo == 0]),
                  'verified': len(df.loc[df.is_verified == True]),
                  'closed': len(df.loc[df.is_closed == True]),
                  'can_post': len(df.loc[df.can_post == True]),
                  'deleted_accs': len(df.loc[pd.notna(df['deactivated'])]),
                  'sex': {'male': len(df.loc[df.sex == 2]), 'female': len(df.loc[df.sex == 1])},
                  'relationship': {},
                  'age_info': bdate_preprocess(df.bdate),
                  'user_popularity': followers(df.followers_count),
                  'personal': personal_pre(df.personal),
                  'universities': uni_pre(df.universities),
                  'occupation': occ_pre(df.occupation),
                  'city': city_pre(df.city)}
    num = 1
    rel = ['no_marriage', 'has_friend', 'has_fiance', 'marriage', 'its_difficult',
           'searching', 'in_love', 'civil_marr']

    for status in rel:
        statistics['relationship'][status] = len(df.loc[df.relation == num])
        num += 1

    preference = ['games', 'movies', 'music', 'interests']
    for pref in preference:
        if column_to_interest_list(df[pref]) == -1:
            statistics[pref] = 'no_common'
        else:
            statistics[pref] = column_to_interest_list(df[pref])

    return statistics


def fin(public):
    a = list_of_members(public)
    try:
        if a['execute_errors']:
            return -2, -2
    except KeyError:
        df = pd.DataFrame(a['response'])
        final = preprocess_dataframe(df)
        json_data = json.dumps(final)
        return json_data, final
