from pprint import pprint
from pymongo import MongoClient
from os import system, name

import json

try:
    uri = "mongodb://localhost:27017/"
    client = MongoClient(uri, serverSelectionTimeoutMS=1000)
    client.admin.command("ping")
    database = client["Economed"]
    collection = database["Economed"]
except Exception as e:
    print("Erro ao conectar ao banco de dados, ligue o MongoDB e tente novamente.")
    exit(1)


with open("config.json") as file:
    config = json.load(file)


def clear():
    if name == "nt":
        _ = system("cls")
    else:
        _ = system("clear")


def exibir_submenu(texto):
    width = 34  # Width of the border
    lines = texto.split("\n")
    centered_lines = []
    for line in lines:
        padding = (width - 2 - len(line)) // 2
        centered_line = " " * padding + line + " " * padding
        if len(centered_line) < width - 2:
            centered_line += " "  # Add an extra space if the line length is odd
        centered_lines.append(centered_line)
    centered_text = "\n".join(centered_lines)
    print(
        f"==================================\n{centered_text}\n==================================\n"
    )


# check if beneficary exists
def check_beneficiary(beneficiary_id):
    beneficiary = collection.find_one({"beneficiario_id": beneficiary_id})
    if beneficiary is None:
        print("Beneficiário não encontrado.\n")
        return False
    return True


def criar_beneficiario():
    clear()
    exibir_submenu("CADASTRO DE BENEFICIÁRIO")
    beneficiario = {
        "beneficiario_id": input("ID do Beneficiário: "),
        "nome": input("Nome: "),
        "idade": int(input("Idade: ")),
        "localizacao": input("Localização (Cidade, Estado): "),
        "historico_saude": [
            {
                "ano": int(input("Ano do diagnóstico: ")),
                "diagnostico": input("Diagnóstico: "),
                "tratamento": input("Tratamento: "),
            }
        ],
        "CID": input("Código CID: "),
        "condicoes_atendimento": input(
            "Condições de atendimento (separadas por vírgula): "
        ).split(","),
        "preferencias": {
            "tipo_atendimento": input("Tipo de atendimento: "),
            "proximidade": input("Proximidade (True/False): ") == "True",
            "custo": input("Custo (baixo/medio/alto): "),
        },
        "provedores_proximos": [
            {
                "nome": input("Nome do provedor próximo: "),
                "especialidade": input("Especialidade: "),
                "custo_estimado": float(input("Custo estimado: ")),
            }
        ],
        "data_ultima_consulta": input("Data da última consulta (YYYY-MM-DD): "),
        "custo_estimado": float(input("Custo estimado: ")),
    }
    collection.insert_one(beneficiario)
    print("Beneficiário inserido com sucesso.\n")


def ler_beneficiarios():
    clear()
    exibir_submenu("LISTA DE BENEFICIÁRIOS")
    if collection.count_documents({}) == 0:
        print("Nenhum beneficiário encontrado.\n")
        return
    while True:
        filtro = input(
            "Filtrar por algum campo? (deixe vazio para listar todos | 'help' para ver todos os campos): "
        )
        if filtro == "help":
            for key in collection.find_one().keys():
                print(key, end=", ")
            print("\n")
        elif filtro in collection.find_one().keys():
            break
        elif filtro == "":
            break
        else:
            print("Campo inválido. Tente novamente.\n")

    if filtro:
        chave = filtro
        valor = input(f"Digite o valor para o campo '{chave}': ")
        beneficiarios = collection.find({chave: valor})
        item_count = collection.count_documents({chave: valor})
    else:
        beneficiarios = collection.find()
        item_count = collection.count_documents({})

    print()

    if item_count == 0:
        print("Nenhum beneficiário encontrado.\n")
        return

    for beneficiario in beneficiarios:
        pprint(beneficiario, compact=config["compact"])
        print()


def atualizar_beneficiario():
    clear()
    exibir_submenu("ATUALIZAÇÃO DE BENEFICIÁRIO")
    beneficiario_id = input("ID do Beneficiário a ser atualizado: ")
    if not check_beneficiary(beneficiario_id):
        return
    campo = input("Campo a atualizar: ")
    valor = input(
        f"Novo valor para o campo '{campo}' (Atual: {collection.find_one({'beneficiario_id': beneficiario_id})[campo]}): "
    )
    collection.update_one(
        {"beneficiario_id": beneficiario_id}, {"$set": {campo: valor}}
    )
    print("Beneficiário atualizado com sucesso.\n")


def deletar_beneficiario():
    clear()
    exibir_submenu("EXCLUSÃO DE BENEFICIÁRIO")
    beneficiario_id = input("ID do Beneficiário a ser excluído: ")
    if not check_beneficiary(beneficiario_id):
        return
    collection.delete_one({"beneficiario_id": beneficiario_id})
    print("Beneficiário excluído com sucesso.\n")


def exportar_dataset():
    clear()
    exibir_submenu("EXPORTAR DATASET")
    nome_arquivo = input("Nome do arquivo para exportar (exemplo: dataset.json): ")
    dados = list(collection.find())
    for doc in dados:
        doc["_id"] = str(doc["_id"])
    with open(nome_arquivo, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4)
    print(f"Dataset exportado para {nome_arquivo}.\n")


def configuracoes():
    clear()
    exibir_submenu("CONFIGURAÇÕES")
    # show all configurations
    print("Configurações atuais:")
    for key, value in config.items():
        print(f"{key}: {value}")
    print()
    while True:
        chave = input(
            "Digite o nome da configuração a ser alterada (ou '0' para sair): "
        )
        if chave == "0":
            print("Saindo das configurações.\n")
            return
        elif chave not in config:
            print("Configuração inválida. Tente novamente.\n")
        else:
            break
    if config[chave] == True or config[chave] == False:
        config[chave] = not config[chave]
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4)
        print("Configuração alterada com sucesso.\n")
        return

    valor = input(f"Digite o novo valor para a configuração '{chave}': ")
    config[chave] = valor
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)
    print("Configuração alterada com sucesso.\n")


def exibir_menu():
    print(
        """==================================
         MENU PRINCIPAL         
==================================
 1. Criar Beneficiário
 2. Ler Beneficiários
 3. Atualizar Beneficiário
 4. Deletar Beneficiário
 5. Exportar Dataset
 6. Configurações
 0. Sair
=================================="""
    )


def menu():
    while True:
        exibir_menu()
        opcao = input("Opção: ")

        if opcao == "1":
            criar_beneficiario()
        elif opcao == "2":
            ler_beneficiarios()
        elif opcao == "3":
            atualizar_beneficiario()
        elif opcao == "4":
            deletar_beneficiario()
        elif opcao == "5":
            exportar_dataset()
        elif opcao == "6":
            configuracoes()
        elif opcao == "0":
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Tente novamente.\n")


# Executar o menu
if __name__ == "__main__":
    clear()
    menu()
