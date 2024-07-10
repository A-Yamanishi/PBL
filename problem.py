import sys
sys.path.append('C:/Users/ajpjdm/AppData/Local/Programs/Python/Python312/Lib/site-packages')

import pulp
import pandas as pd

class MenuProblem:

    def __init__(self, place, target, allergy):
        self.place = place
        self.target = target
        self.allergy = allergy

        self.f_df = pd.read_csv("foods.csv", encoding="utf-8_sig")
        self.c_df = pd.read_csv("categories.csv", encoding="utf-8_sig")
        self.a_df = pd.read_csv("allergy.csv", encoding="utf-8_sig")

        self.f_p_df = self.f_df[self.f_df.place==self.place]

        self.prob = self._formulate()

    def _formulate(self):
        INF = 1e9

        # データ読み込み


        # データを設定
        C = self.c_df['c'].to_list()
        Max_c = {row.c:row.max for row in self.c_df.itertuples()}

        F = self.f_p_df['f'].to_list()
        E_f = {row.f:row.energy for row in self.f_df.itertuples()}

        A = self.a_df.columns.tolist()
        A.pop(0)

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
        z = pulp.LpVariable('z', cat='Continunous')

        # 制約
        for c in C:
            prob += pulp.lpSum(x[f] for f in F_c[c]) <= Max_c[c]
            
        prob += pulp.lpSum(x[f] for f in F_main) >= 1
        prob += pulp.lpSum(x[f] for f in F_main) <= 2

        prob += pulp.lpSum(x[f] for f in F_c[C_rice]) <= pulp.lpSum(x[f2] for f2 in F_c[C_with_rice])

        for a in A:
            if self.allergy[a] == 0: continue
            prob += pulp.lpSum(x[f]*self.a_df[self.a_df.f==f][a].to_list()[0] for f in F) == 0

        prob += self.target - pulp.lpSum(x[f]*E_f[f] for f in F) >= -z
        prob += self.target - pulp.lpSum(x[f]*E_f[f] for f in F) <= z
        prob += z >= 0

        prob += z <= self.target * 0.1

        # 目的関数
        prob += z

        return {'prob': prob, 'variable': {'x': x}, 'list': {'F': F}}


    def solve(self):

        # 最適化問題を解く
        solver = pulp.PULP_CBC_CMD()
        status = self.prob['prob'].solve(solver)
        print('Status:', pulp.LpStatus[status])

        # 結果を出力
        mask = []

        x = self.prob['variable']['x']
        F = self.prob['list']['F']

        for f in F:
            if x[f].value() == 1:
                mask.append(True)
            else:
                mask.append(False)

        result_df = self.f_p_df[mask]

        return status, result_df   