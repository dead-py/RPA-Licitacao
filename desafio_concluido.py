import os
import rpa as r
import pyautogui as p
import zipfile as z
import pandas as pd


def baixa_csv_licitacoes(
        url='http://dados.tce.rs.gov.br/organization/tribunal-de-contas-do-estado-do-rio-grande-do-sul'):
    r.init()
    r.url(url)
    janela = p.getActiveWindow()
    janela.maximize()

    r.click('//*[@id="content"]/div[3]/div/article/div/ul/li[2]/div/h3/a')
    r.wait(2.0)
    r.click('//*[@id="dataset-resources"]/ul/li/div/button')
    r.click('//*[@id="dataset-resources"]/ul/li/div/ul/li[2]/a')  # Baixa o .zip
    r.wait(45)

    with z.ZipFile("2022.csv.zip", 'r') as zip_ref:  # Extrai o .zip
        zip_ref.extractall("C:\\Users\\jayme\\PycharmProjects\\Wind")
    r.close()


def remove_temp(diretorio='C:\\Users\\jayme\\PycharmProjects\\Wind'):
    for file in os.listdir(diretorio):
        if file.endswith('.csv') and file not in ('item.csv', 'licitacao.csv'):
            os.remove(diretorio + '\\' + file)


def filtra_csv(arquivo='licitacao.csv',
               nome_temp_csv='licitacoes_temp_2022.csv'):
    licitacao = pd.read_csv(arquivo,
                            parse_dates=['DT_ABERTURA'])
    dados_listados = licitacao[(licitacao["DT_ABERTURA"] > '2022-05-01')].head(30)
    dados_listados.to_csv(nome_temp_csv, index=False)


def cria_diretorios(dir="C:\\Users\\jayme\\PycharmProjects\\Wind\\LICITACAO_2022"):
    diretorio_pai = dir

    try:
        os.mkdir(diretorio_pai)

    except FileExistsError:
        pass

    df_licitacao_temp = pd.read_csv('licitacoes_temp_2022.csv',
                                    parse_dates=['DT_ABERTURA'],
                                    usecols=['CD_ORGAO',
                                             'NM_ORGAO',
                                             'CD_TIPO_MODALIDADE',
                                             'NR_LICITACAO',
                                             'ANO_LICITACAO',
                                             'DT_ABERTURA',
                                             'LINK_LICITACON_CIDADAO'])

    for index, row in df_licitacao_temp.iterrows():
        codigo_orgao = row['CD_ORGAO']
        codigo_tipo_mod = row['CD_TIPO_MODALIDADE']
        numero_licitacao = int(row['NR_LICITACAO'])
        ano_licitacao = row['ANO_LICITACAO']
        link_licitacao = row['LINK_LICITACON_CIDADAO']

        diretorio = f"{codigo_orgao} - {codigo_tipo_mod} - {numero_licitacao} - {ano_licitacao}"
        diretorio_licitacao = os.path.join(diretorio_pai, diretorio)

        try:
            if os.path.isdir(diretorio_licitacao):
                print(f"Diretório já existe. {diretorio}")

            else:
                os.mkdir(diretorio_licitacao)
                print(f"Diretório criado: {diretorio}")

            filtra_item('item.csv',
                        codigo_orgao,
                        numero_licitacao,
                        ano_licitacao,
                        codigo_tipo_mod,
                        diretorio_licitacao)

        except Exception as e:
            print(e)

        else:
            cria_txt_link(diretorio_licitacao, link_licitacao)


def cria_txt_link(path=r'C:\Users\jayme\PycharmProjects\Wind\LICITACAO_2022', url='www.google.com'):
    path = path + r'\link.txt'
    with open(path, 'a') as file:
        file.write(url)


def filtra_item(arquivo='item.csv',
                cd_orgao='1',
                nr_licitacao=1,
                ano_licitacao=2000,
                cd_tipo_modalidade='A',
                diretorio='C:\\Users\\jayme\\PycharmProjects\\Wind\\LICITACAO_2022'):
    itens = pd.read_csv(arquivo, low_memory=False)

    dados_listados = itens[(itens["CD_ORGAO"] == cd_orgao) &
                           (itens["NR_LICITACAO"] == nr_licitacao) &
                           (itens["ANO_LICITACAO"] == ano_licitacao) &
                           (itens["CD_TIPO_MODALIDADE"] == cd_tipo_modalidade)]

    dados_listados.to_csv(diretorio + '\\itens-licitacao.csv', index=False)


baixa_csv_licitacoes()  # 1
remove_temp()           # 2
filtra_csv()            # 3
cria_diretorios()       # 4

