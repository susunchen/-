import numpy as np
import copy
import pandas as pd
import pymysql
from sklearn.metrics.pairwise import cosine_similarity
from config.local_setting import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine

def get_array(data, array_name):  # 得到相似度矩阵
    word = data[['food_name', 'food_tag']]
    word_dict = word.to_dict()
    all_name_list = list(word_dict[array_name].values())
    name_array_all = get_cos(all_name_list, array_name)

    return name_array_all


def get_cos(all_name_list, array_name):
    if array_name == 'food_name':
        name_feature = []
        for name in all_name_list:
            for word in name:
                name_feature.append(word)
        name_feature = list(set(name_feature))
    else:
        names_all = ""
        name_feature = list(set(names_all.join(all_name_list)))  # 全拆
    name_array_all = pd.DataFrame(np.zeros(len(name_feature)))
    for a_name in all_name_list:
        if array_name == 'food_name':
            every_name = list(set(a_name))
        else:
            every_name = list(set(a_name))
        name_array = np.zeros(len(name_feature))
        for name_word in every_name:
            name_array[name_feature.index(name_word)] = 1
        name_array_all = pd.concat([name_array_all, pd.DataFrame(name_array)], axis=1)
    name_array_all = name_array_all.T
    name_array_all = np.delete(name_array_all.values, 0, axis=0)
    cos = cosine_similarity(name_array_all)
    cos_frame = pd.DataFrame(cos)
    return cos_frame


def get_data(data, food_id):  # 规范化
    food_index = data.loc[data.loc[:, "food_id"] == food_id, :].index.values[0]
    name_array = get_array(data, 'food_name')  # 名字相似度
    tag_array = get_array(data, 'food_tag')  # 标签相似度
    tag = tag_array[[food_index]]
    tag.columns = ["tag_cos"]
    name = name_array[[food_index]]
    name.columns = ["name_cos"]
    data = data.join(tag)
    data = data.join(name)
    return data


def get_res(data, food_id, hall_id):  # 得到单个食品中推荐的前三位
    new_data = get_data(data, food_id)
    food_index = data.loc[data.loc[:, "food_id"] == food_id, :].index.values[0]

    food_data = new_data[['food_name', 'food_id', 'food_price', 'cat_id', 'tag_cos', 'name_cos', 'hall_id', 'hot']]
    knn_data = food_data.drop(food_index, axis=0)
    knn_data['cosA'] = 0
    knn_data = copy.deepcopy(knn_data.query('hall_id==%d' % hall_id))
    cat_id = data.iloc[[food_index]]["cat_id"].values[0]

    cat_food = knn_data.loc[knn_data.loc[:, "cat_id"] == cat_id, :]
    cat_food.eval("cosA=0.8", inplace=True)
    if len(cat_food) < 3:
        cat_food = copy.deepcopy(knn_data)
        cat_food.loc[knn_data.loc[:, "cat_id"] == cat_id, ['cosA']] = 0.8
    price = np.array(cat_food['food_price'])
    price_rel = abs(price - np.mean(price)) / np.std(price)  # 标准化
    price_cos = price_rel / np.sum(price_rel)  # 归一化
    price_cos = pd.DataFrame(price_cos, columns=["price_cos"])
    price_cos = price_cos.set_index(cat_food.index)

    cos_alldata = pd.concat([cat_food, price_cos], axis=1)
    cos_data = cos_alldata[['food_name', 'food_id', 'tag_cos', 'name_cos', 'price_cos', 'hot', 'cosA']]
    hot_data = cos_data.query('hot==1')
    no_hot_data = cos_data.query('hot==0')

    hot_data = copy.deepcopy(hot_data.eval("Fcos = tag_cos*0.6+name_cos*0.2+price_cos*0.1+0.5+cosA", inplace=False))
    no_hot_data = copy.deepcopy(no_hot_data.eval("Fcos = tag_cos*0.6+name_cos*0.2+price_cos*0.1+cosA", inplace=False))
    food_havecos = copy.deepcopy(pd.concat([hot_data, no_hot_data], axis=0))
    food_havecos = food_havecos.sort_values(by='Fcos', ascending=False)
    food_havecos = food_havecos.reset_index()  # 最终表

    # 返回值
    res_food_id = food_havecos.iloc[0:3]['food_id'].values
    res_food_id_list = list(res_food_id)
    res_id_str = str(res_food_id_list)

    res_food_name_table = food_havecos.query('food_id == %s' % res_id_str)[['food_name', 'food_id', 'Fcos']]
    res_food_name_table = res_food_name_table.sort_values(by='Fcos', ascending=False)
    res_food_name = res_food_name_table['food_name']
    res_food_name_list = list(res_food_name)

    res_food_cos = food_havecos.iloc[0:3]['Fcos'].values
    res_food_cos_list = list(res_food_cos)

    return res_food_id_list, res_food_name_list, res_food_cos_list


def do(data, food_id, hall_id):
    try:
        return get_res(data, food_id, hall_id)
    except:
        return ("所输入的食品号不存在")


def read_sql(host, username, password, member_id):  # 从sql读取食物数据和用户购买过的食品id
    con = pymysql.Connect(host=host, user=username, password=password, database="food_db", charset='utf8',
                          use_unicode=True)
    member_A_food_data = pd.read_sql("select * from pay_order_item", con)

    food_old_data = pd.read_sql("SELECT id,NAME,price,tags,cat_id,total_count,hall_id FROM food", con)
    food_old_data.columns = ['food_id', 'food_name', 'food_price', 'food_tag', 'cat_id', 'num', 'hall_id']

    food_dt = copy.deepcopy(food_old_data.sort_values('num', ascending=False))
    food_dt['hot'] = np.array([1] * 5 + [0] * (len(food_old_data) - 5))
    food_data = copy.deepcopy(food_dt.sort_values("food_id"))  # 输入数据

    member_food_id = list(set(member_A_food_data.query("member_id==%d" % member_id)['food_id'].values))  # 用户购买过的食物的id
    return food_data, member_food_id


def get_res_data(food_data, member_food_id, do, hall_id):  # 得到所有食品中推荐的前三位
    res_all_id = []
    res_all_name = []
    res_all_cos = []
    for food_id in member_food_id:
        res_e_id, res_e_name, res_e_cos = (do(food_data, food_id, hall_id))
        res_all_id += res_e_id
        res_all_name += res_e_name
        res_all_cos += res_e_cos
    res_data = pd.DataFrame([res_all_id, res_all_name, res_all_cos])
    res_data = res_data.T
    res_data.columns = ['food_id', 'food_name', 'food_cos']
    res_data = res_data.drop_duplicates()
    result_data = res_data.groupby(by=['food_id', 'food_name'])['food_cos'].sum()
    result_data = result_data.to_frame()
    result_data_asc = copy.deepcopy(result_data.sort_values('food_cos', ascending=False))

    res = result_data_asc.iloc[0:3]
    res = res.reset_index()
    return res

def Recommend(member_id,hall_id):
    url = SQLALCHEMY_DATABASE_URI.split("/")[2]
    url_list = url.split("@")
    host = url_list[1]    #数据库ip地址
    li = url_list[0]
    username = li.split(":")[0] #用户名
    password = li.split(":")[1] #密码
    food_data, member_food_id = read_sql(host, username, password, member_id)
    res = get_res_data(food_data, member_food_id, do, hall_id)  # 推荐结果

    if len(res) == 0:  # 新用户
        no_res_data = food_data.sort_values('num', ascending=False).iloc[0:3]
        no_res = copy.deepcopy(no_res_data[['food_id', 'food_name']])
        no_res['food_cos'] = 0
        res = copy.deepcopy(no_res) #推荐结果
    res_id = list(res['food_id'])   #推荐id
    #res_name = list(res['food_name']) #推荐名称
    #res_cos = list(res['food_cos']) #推荐相似度
    return res_id


def Nutrition_Recommendation(food):
    np.set_printoptions(suppress=True)  # 取消科学计数法

    engine = create_engine(
        "mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'Szu.123456', '139.159.161.41:3306', 'food_db', 'gbk'))
    con = engine.connect()  # 创建连接

    every_values = [2000, 79.44, 60, 1.4, 1.6, 18, 10, 300, 15, 300]  # 每日营养值
    every_values = np.array(every_values) / 3
    yinyang = pd.read_sql_table('yingyang', con)  # 营养表
    yinyang_data = yinyang.groupby('food_id').sum()

    hall_id = yinyang_data.query("food_id==%d" % food[0][0])['hall_id'].values[0]

    every_values_Frame = pd.DataFrame(every_values).T
    every_values_Frame.columns = [r'能量/卡路里', '蛋白质', '脂肪', 'VB1', 'VB2', 'VPP', '维生素E', '钙', '铁', '胆固醇']

    all_array = np.zeros(len(every_values))
    for every_food in food:
        a_food = (yinyang_data.query('food_id=={}'.format(every_food[0])) * every_food[1])[
            [r'能量/卡路里', '蛋白质', '脂肪', 'VB1', 'VB2', 'VPP', '维生素E', '钙', '铁', '胆固醇']]
        a_array = a_food.values[0]
        a_array = copy.deepcopy(a_array.astype('float64'))
        all_array += a_array

    del_array = all_array - every_values
    cent_array = del_array / every_values
    all_array_Frame = pd.DataFrame(cent_array).T  # 百分比
    all_array_Frame.columns = [r'能量/卡路里', '蛋白质', '脂肪', 'VB1', 'VB2', 'VPP', '维生素E', '钙', '铁', '胆固醇']

    all_array_Frame1 = pd.DataFrame(del_array).T  # 真值
    all_array_Frame1.columns = [r'能量/卡路里', '蛋白质', '脂肪', 'VB1', 'VB2', 'VPP', '维生素E', '钙', '铁', '胆固醇']

    Frame = copy.deepcopy(all_array_Frame.T)
    Frame.columns = ['val']
    min_array = pd.DataFrame(Frame.reset_index())
    min_array = min_array.groupby('val').min().head(1)
    min_array = copy.deepcopy(min_array.reset_index().set_index('index'))  # 最缺的元素Frame

    if min_array.values[0][0] < 0:
        min_dict = min_array.to_dict()['val']
        min_keys = list(min_dict.keys())[0]  # 最缺的元素名称
        min_values = all_array_Frame1[[min_keys]].values[0][0]  # 最缺的元素数值
        min_dict[min_keys] = min_values
        res_food_id = list((yinyang_data.query("hall_id==%d"%hall_id)).sort_values(by=list(min_dict.keys())[0],ascending=False)[0:2].index)#推荐的菜品id
    else:
        min_dict = {}
        min_keys = ""  # 最缺的元素名称
        min_values = 0  # 最缺的元素数值
        res_food_id = []  # 推荐的菜品id

    a = {'min_keys': min_keys, "min_values": min_values, "res_food_id": res_food_id}
    return a