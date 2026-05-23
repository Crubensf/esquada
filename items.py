# -*- coding: utf-8 -*-
"""Definição dos 25 itens do questionário ESQUADA e parâmetros brutos do modelo GRM."""

from __future__ import annotations

# Nomes das 25 colunas de resposta esperadas no CSV de entrada
ESQ_COLS = [f"esq_q{i}_sem0" for i in range(1, 26)]

# Definição dos itens: texto da pergunta, opções exibidas e mapeamento opção → categoria de escore
ESQ_ITEMS = [
    {
        "name": "esq_q1_sem0",
        "text": "Você costuma tomar o café da manhã?",
        "options": [
            "Não costumo.",
            "Sim, eu costumo tomar pelo menos em um dia na semana.",
        ],
        "score_map": [0, 1],
    },
    {
        "name": "esq_q2_sem0",
        "text": "Quais alimentos você costuma comer no café da manhã?",
        "options": [
            "Eu não costumo comer no café da manhã.",
            "Eu costumo apenas beber líquidos, como: água, suco, leite, chá, café e/ou outras bebidas.",
            "Eu costumo comer alimentos, como: tapioca, cuscuz, bolos, biscoitos, bolachas, pães e/ou outros que seja necessário mastigar.",
            "Eu costumo comer alimentos como: tapioca, cuscuz, bolos, biscoitos, bolachas, pães e/ou outros que seja necessário mastigar e, também, beber líquidos como: água, suco, leite, chá, café e/ou outras bebidas.",
        ],
        "score_map": [0, 1, 2, 2],
    },
    {
        "name": "esq_q3_sem0",
        "text": "Você costuma almoçar?",
        "options": [
            "Não costumo.",
            "Sim, eu costumo almoçar pelo menos um dia na semana.",
        ],
        "score_map": [0, 1],
    },
    {
        "name": "esq_q4_sem0",
        "text": "Quais alimentos você costuma comer no almoço?",
        "options": [
            "Eu não costumo almoçar.",
            "Eu costumo comer alimentos como: macarrão instantâneo (miojo), salgados e/ou hambúrguer tipo fast-food, por exemplo, coxinha, pizza, Hot Hit®, Hot Pocket®, X-salada, X-ovo, Mc Donald's®, Bob's® ou Subway®.",
            "Eu costumo comer alimentos, como: pães, queijos e/ou sanduíches feitos em casa.",
            "Eu costumo comer alimentos, como: arroz, feijão, carne (boi, porco, frango, peixe ou opção vegetariana) e/ou salada.",
        ],
        "score_map": [0, 0, 0, 1],
    },
    {
        "name": "esq_q5_sem0",
        "text": (
            "Você costuma substituir a refeição do almoço ou jantar por lanches? "
            "(Considere exemplos de lanches: pizza, salgados, Hot Hit®, Hot Pocket®, "
            "X-salada, X-ovo, Mc Donald's®, Bob's®, Subway®, escondidinho industrializado, "
            "estrogonofe industrializado ou lasanha industrializada.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu substituo.",
            "Sim, eu costumo substituir em um ou dois dias na semana.",
            "Sim, eu costumo substituir em três ou mais dias na semana.",
        ],
        "score_map": [3, 2, 1, 0],
    },
    {
        "name": "esq_q6_sem0",
        "text": (
            "Você costuma cozinhar ou ajudar no preparo dos alimentos em refeições como "
            "almoço e jantar? (Considere ajudar no preparo: lavar, picar e/ou cozinhar os alimentos.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, eu costumo em pelo menos um dia na semana.",
        ],
        "score_map": [0, 1],
    },
    {
        "name": "esq_q7_sem0",
        "text": "Onde você ou alguém da sua casa costuma adquirir frutas, legumes e/ou verduras?",
        "options": [
            "Não costumamos adquirir frutas, legumes e/ou verduras.",
            "Em supermercados e/ou hipermercados.",
            "Em quitandas, sacolões, hortifrutis, minimercados, barraquinhas e/ou CEASA.",
            "Em feiras livres, hortas, feiras de alimentos orgânicos, compra direta do produtor ou produção própria e/ou de alguém da família ou vizinho.",
        ],
        "score_map": [0, 1, 2, 2],
    },
    {
        "name": "esq_q8_sem0",
        "text": (
            "\"Por mais R$1,00 leve a porção grande de batata frita\". Em situações como no "
            "exemplo apresentado, você costuma escolher a maior porção dos alimentos pagando "
            "um pouco mais?"
        ),
        "options": ["Sim.", "Não."],
        "score_map": [0, 1],
    },
    {
        "name": "esq_q9_sem0",
        "text": "Você costuma comer arroz integral e/ou macarrão integral?",
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um a quatro dias na semana.",
            "Sim, eu costumo comer em cinco ou mais dias na semana.",
        ],
        "score_map": [0, 1, 2, 3],
    },
    {
        "name": "esq_q10_sem0",
        "text": "Você costuma comer aveia, quinoa e/ou centeio?",
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um a quatro dias na semana.",
            "Sim, eu costumo comer em cinco ou mais dias na semana.",
        ],
        "score_map": [0, 1, 2, 3],
    },
    {
        "name": "esq_q11_sem0",
        "text": (
            "Você costuma comer legumes ou verduras crus e/ou cozidos? "
            "(Não considerar o consumo de mandioca, batata, cará e inhame.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um a quatro dias na semana.",
            "Sim, eu costumo comer em cinco ou mais dias na semana.",
        ],
        "score_map": [0, 1, 2, 3],
    },
    {
        "name": "esq_q12_sem0",
        "text": "Você costuma comer frutas? (Não considerar o consumo de sucos.)",
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um a quatro dias na semana.",
            "Sim, eu costumo comer em cinco ou mais dias na semana.",
        ],
        "score_map": [0, 1, 2, 3],
    },
    {
        "name": "esq_q13_sem0",
        "text": "Você costuma comer castanha do Pará/Brasil, castanha de caju e/ou nozes?",
        "options": [
            "Não costumo.",
            "Sim, eventualmente (como em festas de final de ano).",
            "Sim, eu costumo comer em um a quatro dias na semana.",
            "Sim, eu costumo comer em cinco ou mais dias na semana.",
        ],
        "score_map": [0, 1, 2, 3],
    },
    {
        "name": "esq_q14_sem0",
        "text": "O que você costuma beber quando está com sede?",
        "options": [
            "Água.",
            "Refrigerante, suco de fruta natural ou em pó, de caixinha, lata e/ou garrafa. (Também considerar bebidas como Feel Good®, H2O®, Fresh® e/ou Aquarius®.)",
        ],
        "score_map": [1, 0],
    },
    {
        "name": "esq_q15_sem0",
        "text": (
            "Você costuma comer bolos, bolachas ou biscoitos industrializados "
            "(comprados prontos)? (Considerar também aqueles feitos com massas prontas.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q16_sem0",
        "text": "Você costuma comer ketchup, mostarda e/ou maionese industrializados (comprados prontos)?",
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q17_sem0",
        "text": (
            "Você costuma comer lanches como salgados fritos ou assados, hambúrguer tipo "
            "fast-food, cachorro quente e/ou pizza industrializada (comprada pronta)? "
            "(Considerar como exemplos de hambúrguer tipo fast-food: X-salada, X-ovo, Hot Hit®, Hot Pocket®, Mc Donald's®, Bob's® ou Subway®.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um ou dois dias na semana.",
            "Sim, eu costumo comer em mais do que dois dias na semana.",
        ],
        "score_map": [3, 2, 1, 0],
    },
    {
        "name": "esq_q18_sem0",
        "text": (
            "Você costuma comer cereais matinais e/ou barrinhas de cereais industrializados? "
            "(Considerar como exemplos de cereais matinais: Sucrilhos®, Nescau Cereal®, Corn Flakes®, Crunch® ou All Bran®.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q19_sem0",
        "text": (
            "Você costuma comer salgadinhos de pacote (tipo chips) como: Ruffles®, Cheetos®, "
            "Elma Chips®, Doritos®, Pringles® ou pipoca de micro-ondas?"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um ou dois dias na semana.",
            "Sim, eu costumo comer em mais do que dois dias na semana.",
        ],
        "score_map": [3, 2, 1, 0],
    },
    {
        "name": "esq_q20_sem0",
        "text": (
            "Você costuma beber refrigerantes e/ou sucos em pó, de caixinha, em lata e/ou garrafa? "
            "(Considerar como exemplos: Del Valle®, Maguary®, Tang®, Sufresh®, Mid®, Taeq®, Feel Good®, H2O®, Fresh® ou Aquarius®.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu bebo.",
            "Sim, eu costumo beber em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q21_sem0",
        "text": (
            "Você costuma comer caldas/coberturas industrializadas para sorvete, geleias "
            "industrializadas, doce de leite, creme de avelã como Nutella® e/ou leite condensado?"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q22_sem0",
        "text": "Você costuma beber bebidas achocolatadas como Toddynho®?",
        "options": [
            "Não costumo.",
            "Sim, às vezes eu bebo.",
            "Sim, eu costumo beber em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q23_sem0",
        "text": (
            "Você costuma comer mortadela, salame, patês/pastas industrializados com sabor de "
            "carne, peito de peru/frango, presunto e/ou apresuntado?"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em pelo menos um dia na semana.",
        ],
        "score_map": [2, 1, 0],
    },
    {
        "name": "esq_q24_sem0",
        "text": (
            "Você costuma comer nuggets/steak (frango empanado industrializado), salsicha "
            "e/ou hambúrguer industrializado (comprado pronto)?"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um ou dois dias na semana.",
            "Sim, eu costumo comer em mais do que dois dias na semana.",
        ],
        "score_map": [3, 2, 1, 0],
    },
    {
        "name": "esq_q25_sem0",
        "text": (
            "Quando você está em casa, você costuma comer macarrão instantâneo (miojo), "
            "sopas em pó, alimentos/pratos congelados industrializados e/ou hambúrguer tipo "
            "fast-food? (Considerar como exemplos: Nissin®, Cup Noodles®, Vono®, lasanha industrializada, "
            "estrogonofe industrializado, escondidinho industrializado, Hot Hit®, Hot Pocket®, X-salada, "
            "X-ovo, Mc Donald's®, Bob's® ou Subway®.)"
        ),
        "options": [
            "Não costumo.",
            "Sim, às vezes eu como.",
            "Sim, eu costumo comer em um ou dois dias na semana.",
            "Sim, eu costumo comer em mais do que dois dias na semana.",
        ],
        "score_map": [3, 2, 1, 0],
    },
]

# Parâmetros GRM embutidos (a1, d1, d2, d3) — um item por linha, separador ";"
# Usado como fallback quando data/parTRUE_R.csv não existe no disco
PARTRUE_RAW = """a1;d1;d2;d3
1.288;0.82;;
0.959;1.604;0.103;
1.021;2.806;;
1.309;4.525;;
1.02;3.497;1.976;-0.531
0.868;0.213;;
0.786;-0.239;-1.812;
0.954;-0.436;;
1.011;0.03;-1.292;-2.964
1.624;0.044;-2.096;-4.05
1.429;2.957;1.102;-0.857
1.102;2.891;0.847;-0.979
1.281;0.524;-1.376;-3.945
0.852;2.337;;
1.05;0.906;-1.681;
0.849;1.909;-1.493;
1.476;4.21;1.898;-1.975
0.758;2.833;0.624;
1.535;4.784;3.038;-0.674
1.749;0.752;-1.51;
1.16;2.193;-1.297;
1.682;2.704;0.262;
1.231;1.979;-1.116;
1.912;4.724;2.983;-0.61
2.237;5.127;3.295;-0.3"""
