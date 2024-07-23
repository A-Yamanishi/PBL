import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from problem import MenuProblem

INF = 1e9
OVER_COLOR = "#F8662D"
UNDER_COLOR = "#71B2E2"
IN_COLOR = "#93BE4D"

categories = {
    'energy': ["エネルギー", "kcal"],
    'protein': ["タンパク質", "g"],
    'fat': ["脂質", "g"],
    'carbo': ["炭水化物", "g"],
    'salt': ["食塩相当量", "g"],
    'calcium': ["カルシウム", "mg"],
    'veg': ["野菜量", "g"],
    'iron': ["鉄", "mg"],
    'va': ["ビタミン A", "μg"],
    'vb1': ["ビタミン B1", "mg"],
    'vb2': ["ビタミン B2", "mg"],
    'vc': ["ビタミン C", "mg"]
}

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

    return d.get(p, 'p0')

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

def show_result(result_df, data) :
    st.success('メニューが見つかりました')
    st.divider()

    menu = {'商品名': [], '値段': []}
    p_sum = 0
    for tuples in result_df.itertuples():
        p_sum += tuples.price
        menu['商品名'].append(tuples.name)
        menu['値段'].append(tuples.price)
        
    st.header('メニュー')
    st.dataframe(pd.DataFrame(menu), hide_index=True)
    st.markdown('**合計金額: ' + str(p_sum) + ' (円)**')
        
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Values", "Score", "Graph"])

    with tab1:

        st.header('摂取量')

        names = result_df['name'].to_list()

        col1, col2 = st.columns(2, gap="large", vertical_alignment="center")

        i = 0

        for k, v in categories.items() :
            fig = go.Figure()
            fig.add_trace(
                go.Pie(
                    labels=names,
                    values=result_df[k].to_list(),
                    hole=0.5,
                    marker_colors=px.colors.sequential.Emrld, 
                    hoverinfo="label+percent+value"
                )
            )
            fig.update_layout(
                title_text=v[0],
                title_font_size=20,
                title_x=0.1,
                annotations=[dict(text=str(round(sum(result_df[k].to_list()), 1))+" "+v[1], x=0.5, y=0.5, font_size=30, showarrow=False)]
            )
            if i % 2 == 0:
                with col1: st.plotly_chart(fig)
            else:
                with col2: st.plotly_chart(fig)
            i+=1

        st.divider()

    with tab2:
        total = 0

        for name in data:
            total += (1-data[name]['score'])*100

        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = total,
            gauge = {'axis': {'range': [0, 1200]}},
            gauge_bar_color=IN_COLOR,
            domain = {'x': [0, 1], 'y': [0, 1]}
        ))

        fig.update_layout(
            autosize=True,
            title_text="総合スコア",
            title_font_size=30,
            title_x=0,
        )

        st.plotly_chart(fig)

        st.divider()

        score = {}
        i = 0
        col1, col2 = st.columns(2, gap="large", vertical_alignment="center")
        for name in data:
            score[data[name]['name']] = (1-data[name]['score'])*100
            fig = go.Figure()

            fig.add_trace(go.Indicator(
                mode = "gauge+number",
                value = score[data[name]['name']],
                gauge = {'axis': {'range': [0, 100]}},
                gauge_bar_color=IN_COLOR,
                domain = {'x': [0, 1], 'y': [0, 1]},
                number_font_size=60
            ))

            fig.update_layout(
                autosize=True,
                title_text=data[name]['name'],
                title_font_size=20,
                title_x=0.1,
                width=560,
                height=360
            )

            if i % 2 == 0 : 
                with col1: st.plotly_chart(fig)
            else:
                with col2: st.plotly_chart(fig)
            i+=1

    with tab3:

        fig3 = go.Figure()

        labels = ['Protein', 'Fat', 'Carbohydrates', 'Salt', 'Calcium', 'Veg', 'Iron', 'Vitamin A', 'Vitamin B1', 'Vitamin B2', 'Vitamin C']

        ma = []
        mi = []
        val = []
        color = []

        right = 0

        for name in data:
            if name == 'energy': continue
            
            if data[name]['max'] == -1: 
                ma.append(INF)
            else: 
                ma.append((data[name]['max']-data[name]['min'])/data[name]['target']*100)
                right = max(right, (data[name]['max']/data[name]['target']-1)*100)
            mi.append(data[name]['min']/data[name]['target']*100)
            val.append(data[name]['val']/data[name]['target']*100)
            right = max(right, (data[name]['val']/data[name]['target']-1)*100+5)

            if data[name]['val'] < data[name]['min']: color.append(UNDER_COLOR)
            elif data[name]['val'] > data[name]['max'] and data[name]['max'] != -1: color.append(OVER_COLOR)
            else: color.append(IN_COLOR)


        ma = [right if i == INF else i for i in ma]

        labels.reverse()
        ma.reverse()
        mi.reverse()
        val.reverse()
        color.reverse()

        fig3.add_trace(
            go.Bar(
                x=ma,
                y=labels,
                base=mi,
                width=0.6,
                opacity=0.7,
                marker_pattern_shape="/",
                marker_pattern_solidity=0.7,
                marker_cornerradius=10,
                orientation='h',
                marker_opacity=0.8,
                marker=dict(color="#93BE4D", line_color="#93BE4D", pattern_fillmode="replace")
            )
        )

        fig3.add_trace(
            go.Bar(
                x=val,
                y=labels,
                width=0.4,
                orientation='h',
                marker_color=color
            )
        )

        fig3.update_layout(barmode="overlay", height=700, bargap=1, title="摂取栄養素グラフ", title_font_size=30)
        st.plotly_chart(fig3)

def get_foods(p) :
    f_df = pd.read_csv("./data/foods.csv", encoding="utf-8_sig")
    f_p_df = f_df[f_df.place==p]
    ret = []
    for f in f_p_df.itertuples():
        ret.append(f.name)

    return ret

st.set_page_config(
    page_title="阪大食堂メニュー推薦ツール",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state=st.session_state.get('sidebar_state', 'expanded')
)

if 'result' not in st.session_state: 
	st.session_state.result = pd.DataFrame()
if 'data' not in st.session_state:
    st.session_state.data = {}

st.session_state.sidebar_state = 'expanded'

st.sidebar.title("食堂メニュー推薦ツール")
st.sidebar.divider()

place_name = st.sidebar.selectbox('食堂を選択してください', ['(未選択)', 'カフェテリアレインボー', '豊中図書館下食堂', '工学部食堂ファミール', 'カフェテリアかさね', '福利会館3階食堂', 'Kitchen BISYOKU', 'カフェテリア匠'])

allergy = st.sidebar.multiselect('アレルギーを選択してください', [
    '卵', '乳', '落花生', 'そば', '小麦', 'えび', 'かに', '牛肉', '鶏肉', '豚肉', 'あわび', 'いか', 'いくら', 'さけ', 'さば', '大豆', 
    'まつたけ', 'やまいも', 'オレンジ', 'もも', 'キウイフルーツ', 'りんご', 'バナナ', 'ゼラチン', 'ゴマ', 'カシューナッツ', 'くるみ', 'アーモンド', '魚介類'
],key='s0')

max_price = st.sidebar.slider(label='予算(円)', min_value=300, max_value=3000, value=650, step=50)

amount = st.sidebar.select_slider("食事の量", options=["少な目", "普通", "多め"], value="普通")

calorie = 700
if amount == "少な目": calorie = 500
if amount == "多め": calorie = 900

st.sidebar.divider()

wish_list = []
unwish_list = []

toggle_on = st.sidebar.toggle("詳細設定")
if toggle_on:
    calorie = st.sidebar.slider(label='目安摂取カロリー(kcal)', min_value=300, max_value=2000, value=calorie, step=10)

    place = get_place(place_name)
    foods = get_foods(place)

    wish_list = st.sidebar.multiselect('食べたい商品を選択してください', foods, key='s1')

    unwish_list = st.sidebar.multiselect('食べたくない商品を選択してください', foods, key='s2')

st.sidebar.divider()

pushed = st.sidebar.button('決定', key=0)

if pushed :
    if place_name == '(未選択)' :
        st.sidebar.error('食堂が選択されていません')
        st.session_state.result = pd.DataFrame()
        st.session_state.data = {}
    else :
        place_id = get_place(place_name)
        allergy_list = get_allergy_list(allergy)
        status, result_df, data = MenuProblem(place_id, max_price, calorie, allergy_list, wish_list, unwish_list).solve()

        if status == -1 :
            st.sidebar.exception(Exception('条件を満たすメニューが見つかりませんでした'))
            st.session_state.result = pd.DataFrame()
            st.session_state.data = {}
        else :
            st.session_state.result = result_df
            st.session_state.data = data
            st.session_state.sidebar_state = 'collapsed'
            st.rerun()

if not st.session_state.result.empty: 
    show_result(st.session_state.result, st.session_state.data)
