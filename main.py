import locale

import bs4
import requests
import tabulate

from modelos import estrategia, fundo_imobiliario

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def tratar_porcentagem(porcentagem_str):
    return locale.atof(porcentagem_str.split('%')[0])


def tratar_decimal(decimal_str):
    return locale.atof(decimal_str)


headers = {'User-Agent': 'Mozilla/5.0'}

# solicita para uma página da Website e a função retorna o código de status.
resposta = requests.get(
    'https://www.fundamentus.com.br/fii_resultado.php', headers=headers)

#
soup = bs4.BeautifulSoup(resposta.text, 'html.parser')

# Navegando e encontrando as instâncias de uma tag. O método find_all()
# encontra de uma vez e find() retorna único objeto.
linhas = soup.find(id='tabelaResultado').find('tbody').find_all('tr')

result = []

strategy = estrategia(
    cotacao_atual_min=110.0,
    dividend_yield_min=6,
    p_vp_min=0.50,
    valor_mercado_min=20000000,
    liquidez_min=60000,
    qt_imoveis_min=7,
    vacancia_media_max=20
)

for linha in linhas:

    dados_fundo = linha.find_all('td')

    # chamar a função para formatar antes de retornar o valor.
    code = dados_fundo[0].text
    segmento = dados_fundo[1].text
    cotacao_atual = tratar_decimal(dados_fundo[2].text)
    ffo_yield = tratar_porcentagem(dados_fundo[3].text)
    dividend_yield = tratar_porcentagem(dados_fundo[4].text)
    p_vp = tratar_decimal(dados_fundo[5].text)
    valor_mercado = tratar_decimal(dados_fundo[6].text)
    liquidez = tratar_decimal(dados_fundo[7].text)
    qt_imoveis = int(dados_fundo[8].text)
    preco_m2 = tratar_decimal(dados_fundo[9].text)
    aluguel_m2 = tratar_decimal(dados_fundo[10].text)
    cap_rate = tratar_porcentagem(dados_fundo[11].text)
    vacancia_media = tratar_porcentagem(dados_fundo[12].text)

    f_imob = fundo_imobiliario(code, segmento, cotacao_atual, ffo_yield,
                               dividend_yield, p_vp, valor_mercado, liquidez,
                               qt_imoveis, preco_m2, aluguel_m2, cap_rate,
                               vacancia_media)

    if strategy.aplicar_estrategia(f_imob):
        result.append(f_imob)

header = ['CÓDIGO', 'SEGMENTO', 'COTAÇÃO ATUAL', 'DIVIDEND YIELD']
table = []

for element in result:
    table.append([element.code, element.segmento,
                  locale.currency(element.cotacao_atual),
                  f'{locale.str(element.dividend_yield)} %'])

print(tabulate.tabulate(table, headers=header,
      tablefmt="fancy_grid", showindex="always", stralign="center"))
