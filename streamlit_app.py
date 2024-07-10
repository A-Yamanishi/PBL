import streamlit as st
import numpy as np
import pandas as pd

import const
from problem import MenuProblem

def get_place(p) :
    d = {
        'カフェテリアレインボー' : 'p1', 
        '豊中図書館下食堂' : 'p2', 
        '工学部食堂ファミール' : 'p3', 
        'カフェテリアかさね' : 'p4', 
        '福利会館3階食堂' : 'p5', 
        'Kitchen BISYOKU' : 'p6', 
        'カフェテリア匠' : 'p7'
    }

    return d[p]

def get_allergy_list(a) :
    d = {
        '卵': 'egg',
        '乳': 'milk',
        '落花生': 'peanut',
        'そば': 'buckwheat',
        '小麦': 'wheat',
        'えび': 'shrimp',
        'かに': 'crab',
        '牛肉': 'beef',
        '鶏肉': 'chicken',
        '豚肉': 'pork',
        'あわび': 'abalone',
        'いか': 'squid',
        'いくら': 'salmon_roe',
        'さけ': 'salmon',
        'さば': 'mackerel',
        '大豆': 'soybean',
        'まつたけ': 'matsutake',
        'やまいも': 'yam',
        'オレンジ': 'orange',
        'もも': 'peach',
        'キウイフルーツ': 'kiwi',
        'りんご': 'apple',
        'バナナ': 'banana',
        'ゼラチン': 'gelatin',
        'ゴマ': 'sesame',
        'カシューナッツ': 'nuts',
        'くるみ': 'walnut',
        'アーモンド': 'almond',
        '魚介類': 'seafood'
    }

    a_list = {
        'egg': 0,
        'milk': 0,
        'peanut': 0,
        'buckwheat': 0,
        'wheat': 0,
        'shrimp': 0,
        'crab': 0,
        'beef': 0,
        'chicken': 0,
        'pork': 0,
        'abalone': 0,
        'squid': 0,
        'salmon_roe': 0,
        'salmon': 0,
        'mackerel': 0,
        'soybean': 0,
        'matsutake': 0,
        'yam': 0,
        'orange': 0,
        'peach': 0,
        'kiwi': 0,
        'apple': 0,
        'banana': 0,
        'gelatin': 0,
        'sesame': 0,
        'nuts': 0,
        'walnut': 0,
        'almond': 0,
        'seafood': 0
    }

    for a_name in a:
        a_list[d[a_name]] = 1
    
    return a_list

st.sidebar.title("食堂メニュー推薦ツール")

place_name = st.sidebar.selectbox('食堂を選択してください', ['(未選択)', 'カフェテリアレインボー', '豊中図書館下食堂', '工学部食堂ファミール', 'カフェテリアかさね', '福利会館3階食堂', 'Kitchen BISYOKU', 'カフェテリア匠'])

allergy = st.sidebar.multiselect('アレルギーを選択してください', [
    '卵', '乳', '落花生', 'そば', '小麦', 'えび', 'かに', '牛肉', '鶏肉', '豚肉', 'あわび', 'いか', 'いくら', 'さけ', 'さば', '大豆', 
    'まつたけ', 'やまいも', 'オレンジ', 'もも', 'キウイフルーツ', 'りんご', 'バナナ', 'ゼラチン', 'ゴマ', 'カシューナッツ', 'くるみ', 'アーモンド', '魚介類'
])

calorie = st.sidebar.slider(label='目標カロリー(kcal)', min_value=300, max_value=1000, value=600, step=10)

pushed = st.sidebar.button('決定', key=0)

if pushed :
    if place_name == '(未選択)' :
        st.error('食堂が選択されていません')
    else :
        place_id = get_place(place_name)
        allergy_list = get_allergy_list(allergy)
        status, result_df = MenuProblem(place_id, calorie, allergy_list).solve()

        if status == -1 :
            st.exception(Exception('条件を満たすメニューが見つかりませんでした'))
        else :
            st.success('メニューが見つかりました')
            st.dataframe(result_df)
