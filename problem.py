import pulp
import pandas as pd

class MenuProblem:

    def __init__(self, place, max_price, target, allergy, wish_list, unwanted_list):
        self.place = place
        self.max_price = max_price
        self.target = target
        self.allergy = allergy
        self.wish = wish_list
        self.unwanted = unwanted_list

        self.f_df = pd.read_csv("./data/foods.csv", encoding="utf-8_sig")
        self.c_df = pd.read_csv("./data/categories.csv", encoding="utf-8_sig")
        self.a_df = pd.read_csv("./data/allergy.csv", encoding="utf-8_sig")
        self.t_df = pd.read_csv("./data/target.csv", encoding="utf-8_sig")

        self.f_p_df = self.f_df[self.f_df.place==self.place]

        self.prob = self._formulate()

    def _formulate(self):
        INF = 1e9

        # データを設定
        C = self.c_df['c'].to_list()
        Max_c = {row.c:row.max for row in self.c_df.itertuples()}

        F = self.f_p_df['f'].to_list()
        E_f = {row.f:row.energy for row in self.f_df.itertuples()}

        T = self.t_df['t'].to_list()

        A = self.a_df.columns.tolist()
        A.pop(0)

        W = self.f_p_df[self.f_p_df['name'].isin(self.wish)]['f'].to_list()
        UW = self.f_p_df[self.f_p_df['name'].isin(self.unwanted)]['f'].to_list()

        for f in F:
            if E_f[f] == -1:
                E_f[f] = INF

        F_c = {c: self.f_p_df[self.f_p_df.category==c]['f'] for c in C}

        C_main = self.c_df[self.c_df.flag_main==1]['c'].to_list()
        C_with_rice = self.c_df[self.c_df.flag_with_rice==1]['c'].to_list()[0]
        C_rice = self.c_df[self.c_df.flag_rice==1]['c'].to_list()[0]

        F_main = []

        for c in C_main:
            for f in F_c[c]:
                F_main.append(f)

        # 問題定義
        prob = pulp.LpProblem('menu', pulp.LpMinimize)

        x = pulp.LpVariable.dicts('x', F, cat='Binary')
        y = pulp.LpVariable.dicts('y', T, cat='Continunous')
        z = pulp.LpVariable('z', cat='Continunous')

        under = pulp.LpVariable.dicts("under", T, lowBound=0, cat="Continuous")
        over = pulp.LpVariable.dicts("over", T, lowBound=0, cat="Continuous")

        # 制約
        for c in C:
            prob += pulp.lpSum(x[f] for f in F_c[c]) <= Max_c[c]
            
        prob += pulp.lpSum(x[f] for f in F_main) >= 1
        prob += pulp.lpSum(x[f] for f in F_main) <= 2

        prob += pulp.lpSum(x[f] for f in F_c[C_rice]) <= pulp.lpSum(x[f2] for f2 in F_c[C_with_rice])

        for a in A:
            if self.allergy[a] == 0: continue
            prob += pulp.lpSum(x[f]*self.a_df[self.a_df.f==f][a].to_list()[0] for f in F) == 0

        for w in W:
            prob += x[w] == 1

        for uw in UW:
            prob += x[uw] == 0

        for t in self.t_df.itertuples():
            ma = t.max
            mi = t.min
            ta = t.target
            if ma == -1: ma = INF
            if t.cal_percent_flag == 1: # タンパク質・脂質・炭水化物
                prob += pulp.lpSum(x[f]*self.f_p_df[self.f_p_df.f==f][t.alias].to_list()[0] for f in F)*t.cal_per_g >= self.target*mi - under[t.t]
                prob += pulp.lpSum(x[f]*self.f_p_df[self.f_p_df.f==f][t.alias].to_list()[0] for f in F)*t.cal_per_g <= self.target*ma + over[t.t]
                prob += y[t.t]*self.target*ta == under[t.t]+over[t.t]
            else: # それ以外
                prob += pulp.lpSum(x[f]*self.f_p_df[self.f_p_df.f==f][t.alias].to_list()[0] for f in F) <= ma + over[t.t]
                if mi == 0: 
                    prob += under[t.t] == 0
                else: 
                    prob += pulp.lpSum(x[f]*self.f_p_df[self.f_p_df.f==f][t.alias].to_list()[0] for f in F) >= mi - under[t.t]
                prob += y[t.t]*ta == under[t.t]+over[t.t]

        prob += self.max_price >= pulp.lpSum(x[f]*self.f_p_df[self.f_p_df.f==f]['price'].to_list()[0] for f in F)

        prob += self.target - pulp.lpSum(x[f]*E_f[f] for f in F) >= -z
        prob += self.target - pulp.lpSum(x[f]*E_f[f] for f in F) <= z
        prob += z >= 0

        # 目的関数
        prob += z + self.target * pulp.lpSum(y[t.t] for t in self.t_df.itertuples())

        return {'prob': prob, 'variable': {'x': x, 'y': y, 'z': z}, 'list': {'F': F}}


    def solve(self):

        # 最適化問題を解く
        solver = pulp.PULP_CBC_CMD()
        status = self.prob['prob'].solve(solver)
        print('Status:', pulp.LpStatus[status])

        # 結果を出力
        mask = []

        x = self.prob['variable']['x']
        F = self.prob['list']['F']
        
        score = {}

        score['energy'] = {
            'name': "エネルギー",
            'score': self.prob['variable']['z'].value() / self.target,
            'val': 0
        }

        for t in self.t_df.itertuples():
            score[t.alias] = {
                'name': t.name,
                'score': self.prob['variable']['y'][t.t].value(),
                'val': 0,
                'target': t.target,
                'min': t.min,
                'max': t.max,
                'delta': 0
            }

        for f in F:
            if x[f].value() == 1:
                mask.append(True)
                d = self.f_p_df[self.f_p_df.f==f]
                score['energy']['val'] += d['energy'].to_list()[0]
                for t in self.t_df.itertuples():
                    score[t.alias]['val'] += d[t.alias].to_list()[0]
            else:
                mask.append(False)

        score['energy']['delta'] = score['energy']['val'] - self.target

        for t in self.t_df.itertuples() :
            a = 1
            if t.cal_percent_flag == 1 : a = t.cal_per_g/self.target

            score[t.alias]['val'] = score[t.alias]['val'] * a

            if score[t.alias]['max'] < score[t.alias]['val'] and score[t.alias]['max'] != -1 :
                score[t.alias]['delta'] = (score[t.alias]['val'] - score[t.alias]['max']) / a
            elif score[t.alias]['val'] < score[t.alias]['min'] :
                score[t.alias]['delta'] = (score[t.alias]['val'] - score[t.alias]['min']) /  a
            


        result_df = self.f_p_df[mask]

        return status, result_df, score