import os
import rpa as r
import pyautogui as p
import zipfile as z
import pandas as pd


# Baixa e descompacta o arquivo zip, este sendo excluído após a ação.
def baixa_csv_licitacoes(script_dir=os.path.dirname(__file__),
                         url='http://dados.tce.rs.gov.br/organization/tribunal-de-contas-do-estado-do-rio-grande-do-sul'):
    print("Baixando .zip da licitação...")
    r.init(visual_automation=True)
    r.url(url)
    janela = p.getActiveWindow()
    janela.maximize()

    r.click('//*[@id="content"]/div[3]/div/article/div/ul/li[2]/div/h3/a')
    r.wait(2.0)

    # Baixa o .zip
    link = r.read('//*[@id="dataset-resources"]/ul/li/div/ul/li[2]/a/@href')
    r.download(link, script_dir + '\\2022.csv.zip')
    r.wait(15.0)
    r.close()

    with z.ZipFile(script_dir + "\\2022.csv.zip", 'r') as zip_ref:
        zip_ref.extractall(script_dir + '\\zip_ref')

    os.remove(script_dir + "\\2022.csv.zip")


# Remove arquivos desnecessários à geração da filtragem de licitação.
def remove_temp(diretorio=os.path.dirname(__file__) + '\\zip_ref'):
    print("Removendo arquivos temporários...")
    for file in os.listdir(diretorio):
        if file.endswith('.csv') and file not in ('item.csv', 'licitacao.csv'):
            os.remove(diretorio + '\\' + file)


# Filtra o arquivo de licitações baseado na data e na quantidade de licitações desejada.
def filtra_csv(arquivo=os.path.dirname(__file__) + '\\zip_ref\\licitacao.csv',
               nome_temp_csv=os.path.dirname(__file__) + '\\zip_ref\\licitacoes_temp_2022.csv',
               data_filtro='2022-05-01',
               quantidade_licitacoes=30):
    print("Filtrando .csv")
    licitacao = pd.read_csv(arquivo,
                            parse_dates=['DT_ABERTURA'])
    dados_listados = licitacao[(licitacao["DT_ABERTURA"] > data_filtro)].head(quantidade_licitacoes)
    dados_listados.to_csv(nome_temp_csv, index=False)


# Cria os diretórios onde serão armazenados os arquivos de cada licitação.
def cria_diretorios(diretorio=os.path.dirname(__file__)):
    diretorio_pai = diretorio + '\\LICITACAO_2022\\'

    try:
        os.mkdir(diretorio_pai)

    except FileExistsError:
        pass

    df_licitacao_temp = pd.read_csv(diretorio + '\\zip_ref\\licitacoes_temp_2022.csv',
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

            filtra_item(cd_orgao=codigo_orgao,
                        nr_licitacao=numero_licitacao,
                        ano_licitacao=ano_licitacao,
                        cd_tipo_modalidade=codigo_tipo_mod,
                        diretorio=diretorio_licitacao)

        except Exception as e:
            print(e)

        else:
            cria_txt_link(diretorio_licitacao, link_licitacao)


# Gera o txt com o link da licitação.
def cria_txt_link(path=os.path.dirname(__file__) + '\\LICITACAO_2022', url='www.google.com'):
    path_link = path + r'\link.txt'
    with open(path_link, 'a') as file:
        file.write(url)


# Filtra a planilha de itens baseado na planilha de licitações previamente filtrada.
def filtra_item(arquivo=os.path.dirname(__file__) + '\\zip_ref\\item.csv',
                cd_orgao='1',
                nr_licitacao=1,
                ano_licitacao=2000,
                cd_tipo_modalidade='A',
                diretorio=os.getcwd() + '\\LICITACAO_2022'):
    print("Filtrando itens da licitação...")

    itens = pd.read_csv(arquivo, low_memory=False)

    dados_listados = itens[(itens["CD_ORGAO"] == cd_orgao) &
                           (itens["NR_LICITACAO"] == nr_licitacao) &
                           (itens["ANO_LICITACAO"] == ano_licitacao) &
                           (itens["CD_TIPO_MODALIDADE"] == cd_tipo_modalidade)]

    dados_listados.to_csv(diretorio + '\\itens-licitacao.csv', index=False)


# Execução principal da aplicação.
if __name__ == "__main__":
    baixa_csv_licitacoes(os.path.dirname(__file__),
                         url='http://dados.tce.rs.gov.br/organization/tribunal-de-contas-do-estado-do-rio-grande-do-sul')
    remove_temp()
    filtra_csv(data_filtro='2022-05-01', quantidade_licitacoes=30)
    cria_diretorios()
