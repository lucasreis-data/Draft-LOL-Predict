import os
import sys
import joblib

pasta_treino = os.path.dirname(os.path.abspath(__file__))
pasta_python = os.path.dirname(pasta_treino)

sys.path.append(pasta_python)
os.chdir(pasta_python)

import cblol

ligas = ["CBLOL", "LCK", "LPL", "LEC", "LCS", "LCP", None]

for l in ligas:
    print(f"\nTreinamento liga: {l if l else 'Geral (Sem bônus)'}")

    modelo = cblol.treinar_modelo(l)
    nome_arquivo = f"modelo_{l.upper()}.joblib" if l else "modelo_GERAL.joblib"

    saida = os.path.join(pasta_treino, nome_arquivo)
    joblib.dump(modelo, saida)

carregar_encoders = {
    "cod_camp" : cblol.cod_camp,
    "cod_time" : cblol.cod_time,
    "cod_pos" : cblol.cod_pos,
    "colunas_treino" : getattr(cblol, "colunas_treino", None)
}

caminho_encoders = os.path.join(pasta_treino, "encoders.joblib")
joblib.dump(carregar_encoders, caminho_encoders)
print(f"Encoders Salvos em: {caminho_encoders}")

print(f"\n\033[32mTreinamento de todas as ligas concluido.\033[m")