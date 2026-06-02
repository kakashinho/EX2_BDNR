from datetime import datetime
from conexao import db
from utils import (
    hash_senha, exibir_lista, selecionar_item, 
    montar_query, coletar_lista_strings, coletar_enderecos
)

def read(collection_name, query):
    return list(db[collection_name].find(query))

def create_usuario():
    print("\n[Criar Usuário]")
    usuario = {
        "nome": input("Nome: "),
        "sobrenome": input("Sobrenome: "),
        "email": input("Email: "),
        "cpf": input("CPF: "),
        "enderecos": "",
        "senha": hash_senha(input("Senha: ")),
        "favoritos": [],
        "compras": []
    }
    enderecos = coletar_enderecos()
    usuario["enderecos"] = enderecos

    result = db.usuarios.insert_one(usuario)
    if result.acknowledged:
        print(f"Usuário criado com sucesso! _id: {result.inserted_id}")

def create_vendedor():
    print("\n[Criar Vendedor]")
    vendedor = {
        "nome": input("Nome: "),
        "sobrenome": input("Sobrenome: "),
        "email": input("Email: "),
        "enderecos": "",
        "senha": hash_senha(input("Senha: ")),
        "cnpj": input("CNPJ: "),
        "produtos": []
    }
    enderecos = coletar_enderecos()
    vendedor["enderecos"] = enderecos

    result = db.vendedores.insert_one(vendedor)
    if result.acknowledged:
        print(f"Vendedor criado com sucesso! _id: {result.inserted_id}")

def create_produto():
    print("\n[Criar Produto]")
    print("Antes de criar o produto, precisamos selecionar o vendedor.")
    vendedores = read("vendedores", montar_query(["nome", "sobrenome", "cnpj"]))
    vendedor = selecionar_item(vendedores)
    
    if not vendedor:
        print("Vendedor não selecionado. Cancelando cadastro de produto.")
        return

    produto = {
        "nome": input("Nome do Produto: "),
        "descricao": input("Descrição: "),
        "valor": 0.0,
        "fotos": coletar_lista_strings("fotos"),
        "estoque": 0,
        "id_vendedor": vendedor["_id"]
    }

    try:
        valor = float(input("Valor do Produto (R$): "))
        estoque = int(input("Estoque: "))
    except ValueError:
        print("Valor numérico inválido. Cancelando.")
        return

    produto["valor"] = valor
    produto["estoque"] = estoque

    result = db.produtos.insert_one(produto)
    if result.acknowledged:
        print(f"Produto criado com sucesso! _id: {result.inserted_id}")
    
    embed_vendedor = {
        "_id": result.inserted_id,
        "nome": produto["nome"],
        "descricao": produto["descricao"],
        "valor": produto["valor"],
        "fotos": produto["fotos"],
        "estoque": produto["estoque"]
    }
    result = db.vendedores.update_one({"_id": vendedor["_id"]}, {"$push": {"produtos": embed_vendedor}})
    
    if result.modified_count == 0:
        print("O Produto não foi vínculado ao Vendedor.")

    else:
        print(f"Produto criado e vinculado ao vendedor! _id: {embed_vendedor['_id']}")

def adicionar_favorito():
    print("\n[Adicionar Favorito]")
    usuario = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
    if not usuario: return

    print("\n[Adicionar Produto]")
    produto = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
    if not produto: return

    if any(fav["_id"] == produto["_id"] for fav in usuario.get("favoritos", [])):
        print("Produto já está nos favoritos!")
        return

    embed_favorito = {
        "_id": produto["_id"],
        "nome": produto["nome"],
        "descricao": produto["descricao"],
        "fotos": produto.get("fotos", []),
        "id_vendedor": produto["id_vendedor"]
    }
    result = db.usuarios.update_one({"_id": usuario["_id"]}, {"$push": {"favoritos": embed_favorito}})
    print("Favorito adicionado com sucesso!")

    if result.modified_count == 0:
        print("O Produto não foi vínculado ao Favoritos.")

    else:
        print(f"Produto criado e vinculado ao favoritos! _id: {embed_favorito['_id']}")

def create_compra():
    print("\n[Realizar Compra]")
    usuario = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
    if not usuario: return

    if not usuario.get("enderecos"):
        print("Usuário não possui endereço cadastrado. Compra bloqueada.")
        return

    produtos_selecionados = []
    valor_produtos = 0.0

    while True:
        print("\nSelecione um Produto para o Carrinho:")
        produto = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
        if produto:
            produtos_selecionados.append({
                "id_produto": produto["_id"],
                "id_vendedor": produto["id_vendedor"]
            })
            valor_produtos += float(produto["valor"])
            print(f"{produto['nome']} adicionado ao carrinho.")
        
        if input("Deseja adicionar mais itens? (S/N): ").upper() != 'S':
            break

    if not produtos_selecionados:
        print("Carrinho vazio. Compra cancelada.")
        return

    try:
        frete = float(input("Valor do frete (R$): "))
    except ValueError:
        frete = 0.0
        
    valor_total = valor_produtos + frete

    compra = {
        "id_usuario": usuario["_id"],
        "status_pedido": "Pendente",
        "data_compra": datetime.now().isoformat(),
        "frete": frete,
        "valor_total": valor_total,
        "produtos": produtos_selecionados
    }

    result = db.compras.insert_one(compra)
    if result.acknowledged:
        print(f"Compra registrada com sucesso! _id: {result.inserted_id}")

    result = db.usuarios.update_one(
        {"_id": usuario["_id"]},
        {"$push": {"compras": {"_id": result.inserted_id, "data_compra": compra["data_compra"]}}}
    )

    if result.modified_count == 0:
        print("A Compra não foi vínculada ao Usuário.")

    else:
        print(f"Compra registrada e vinculado ao Usuário! Total: R$ {valor_total:.2f}")

def update_geral(colecao, registro, campos_editaveis):
    print(f"\n[Atualizando {colecao}]")
    alteracoes = {}
    for campo in campos_editaveis:
        if campo == "enderecos":
            if input("Deseja atualizar endereços? (S/N): ").upper() == 'S':
                alteracoes[campo] = coletar_enderecos()
            continue
        atual = registro.get(campo, "")
        if campo == "senha":
            nova_senha = input("Nova senha (vazio para manter): ").strip()
            if nova_senha: alteracoes[campo] = hash_senha(nova_senha)
        else:
            novo = input(f"Alterar {campo} (Atual: {atual}): ").strip()
            if novo:
                if campo == "valor": novo = float(novo)
                if campo == "estoque": novo = int(novo)
                alteracoes[campo] = novo
    if alteracoes:
        result = db[colecao].update_one({"_id": registro["_id"]}, {"$set": alteracoes})
        if result.modified_count == 0:
            print(f"A tabela {colecao} não foi atualizado(a).")

        else:
            print(f"A tabela {colecao} foi atualizado(a) com sucesso!")
    return alteracoes

def update_produto(produto_atual):
    alteracoes = update_geral("produtos", produto_atual, ["nome", "descricao", "valor", "fotos", "estoque"])
    if alteracoes:
        # Cascade aplicado em vendedor
        set_v = {f"produtos.$[elem].{k}": v for k, v in alteracoes.items() if k in ["nome", "descricao", "valor", "fotos", "estoque"]}
        if set_v: 
            result = db.vendedores.update_one({"_id": produto_atual["id_vendedor"]}, {"$set": set_v},
            array_filters=[ {"elem._id": produto_atual["_id"]} ])
            if result.modified_count == 0:
                print("O produto não foi atualizado no dicionário de produtos do Vendedor.")

            else:
                print("O produto foi atualizado no dicionário de produtos do Vendedor.")

        # Cascade aplicado em usuario
        set_f = {f"favoritos.$[elem].{k}": v for k, v in alteracoes.items() if k in ["nome", "descricao", "fotos"]}
        if set_f: 
            result = db.usuarios.update_many({"favoritos._id": produto_atual["_id"]}, {"$set": set_f}, array_filters=[ {"elem._id": produto_atual["_id"]} ])
            if result.modified_count == 0:
                print("O produto não foi atualizado no dicionário de produtos de Favoritos.")

            else:
                print("O produto foi atualizado no dicionário de produtos de Favoritos.")

def delete_produto(id_prod, id_vend):
    compras_com_produto = list(db.compras.find({"produtos.id_produto": id_prod}))
    if compras_com_produto:
        print("Erro: Produto possui compras vinculadas:")
        exibir_lista(compras_com_produto)
        return False
    db.produtos.delete_one({"_id": id_prod})
    db.vendedores.update_one({"_id": id_vend}, {"$pull": {"produtos": {"_id": id_prod}}})
    db.usuarios.update_many({}, {"$pull": {"favoritos": {"_id": id_prod}}})
    print("Deletado com sucesso!")
    return True

def remover_favorito(id_prod, id_usuar):
    db.usuarios.update_one({"_id": id_usuar}, {"$pull": {"favoritos": {"_id": id_prod}}})
    print("Removido com sucesso!")

def delete_vendedor(id_vend):
    for prod in read("produtos", {"id_vendedor": id_vend}):
        if not delete_produto(prod["_id"], id_vend): return
    db.vendedores.delete_one({"_id": id_vend})
    print("Vendedor deletado!")

def listar_vendas(compras, vendedor):
    vendas_vendedor = []
    produtos_vendedor = vendedor.get("produtos", [])

    for compra in compras:
        usuario = db.usuarios.find_one({"_id": compra["id_usuario"]})
        if not usuario:
            continue
        
        produtos_vendidos = compra.get("produtos", []) 

        produtos_filtrados = []
        for pv in produtos_vendidos:
            if pv.get("id_vendedor") != vendedor["_id"]:
                continue

            produto_info = next((p for p in produtos_vendedor if p["_id"] == pv["id_produto"]), None)

            if produto_info:
                produtos_filtrados.append({
                    "id_produto": pv["id_produto"],
                    "nome": produto_info.get("nome"),
                    "descricao": produto_info.get("descricao"),
                    "valor": produto_info.get("valor")
                })

        if not produtos_filtrados:
            continue

        vendas_vendedor.append({
            "compra_id": compra["_id"],
            "status": compra.get("status_pedido"),
            "data": compra.get("data_compra"),
            "frete": compra.get("frete", 0),
            "usuario": {
                "nome": f"{usuario.get('nome', '')} {usuario.get('sobrenome', '')}",
                "email": usuario.get("email", "")
            },
            "produtos": produtos_filtrados
        })

    if not vendas_vendedor:
        print("Nenhuma venda encontrada para este vendedor.")

    return vendas_vendedor

def update_compra(compra):
    campos = ["status_pedido", "frete"]
    alteracoes = {}
    for campo in campos:
        atual = compra.get(campo, "")
        novo = input(f"Alterar {campo} (Atual: {atual}): ").strip()
        if novo:
            if campo == "frete":
                try:
                    novo = float(novo)
                except ValueError:
                    print("Valor inválido para frete. Mantendo atual.")
                    continue
            alteracoes[campo] = novo
    if alteracoes:
        result = db.compras.update_one({"_id": compra["_id"]}, {"$set": alteracoes})
        if result.modified_count == 0:
            print("A compra não foi atualizada.")
        else:
            print("Compra atualizada com sucesso!")

def delete_compra(compra):
    db.compras.delete_one({"_id": compra["_id"]})
    db.usuarios.update_one(
        {"_id": compra["id_usuario"]},
        {"$pull": {"compras": {"_id": compra["_id"]}}}
    )
    print("Compra deletada com sucesso!")


def menu_usuario():
    while True:
        print("\n--- Menu do Usuário ---")
        print("1- Create \n2- Read \n3- Update \n4- Delete \n5- Adicionar Favoritos \n6- Remover Favoritos \n7- Listar Favoritos \n8- Listar Compras \nV- Voltar")
        op = input("Opção: ").upper()
        if op == '1': create_usuario()
        elif op == '2': exibir_lista(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
        elif op == '3':
            u = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
            if u: update_geral("usuarios", u, ["nome", "sobrenome", "email", "cpf", "enderecos", "senha"])
        elif op == '4':
            u = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
            if u: db.usuarios.delete_one({"_id": u["_id"]}); print("Deletado!")
        elif op == '5': adicionar_favorito()
        elif op == '6': 
            u = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
            if u:
                fav = selecionar_item(exibir_lista(u.get("favoritos", [])))
                remover_favorito(u["_id"],fav["_id"])
        elif op == '7':
            u = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
            if u: exibir_lista(u.get("favoritos", []))
        elif op == '8':
            u = selecionar_item(read("usuarios", montar_query(["nome", "sobrenome", "cpf"])))
            if u: exibir_lista(u.get("compras", []))
        elif op == 'V': break

def menu_vendedor():
    while True:
        print("\n--- Menu do Vendedor ---")
        print("1- Create \n2- Read \n3- Update \n4- Delete \n5- Listar Produtos \n6- Listar Vendas \nV- Voltar")
        op = input("Opção: ").upper()
        if op == '1': create_vendedor()
        elif op == '2': exibir_lista(read("vendedores", montar_query(["nome", "sobrenome", "cnpj"])))
        elif op == '3':
            v = selecionar_item(read("vendedores", montar_query(["nome", "sobrenome", "cnpj"])))
            if v: update_geral("vendedores", v, ["nome", "sobrenome", "email", "enderecos", "cnpj", "senha"])
        elif op == '4':
            v = selecionar_item(read("vendedores", montar_query(["nome", "sobrenome", "cnpj"])))
            if v: delete_vendedor(v["_id"])
        elif op == '5':
            v = selecionar_item(read("vendedores", montar_query(["nome", "sobrenome", "cnpj"])))
            if v: exibir_lista(v.get("produtos", []))
        elif op == '6':
            v = selecionar_item(read("vendedores", montar_query(["nome", "sobrenome", "cnpj"])))
            if v:
                compras = read("compras", {"produtos.id_vendedor": v["_id"]})
                vendas = listar_vendas(compras, v)
                exibir_lista(vendas)

        elif op == 'V': break

def menu_produto():
    while True:
        print("\n--- Menu do Produto ---")
        print("1- Create \n2- Read \n3- Update \n4- Delete \nV- Voltar")
        op = input("Opção: ").upper()
        if op == '1': create_produto()
        elif op == '2': exibir_lista(read("produtos", montar_query(["nome", "descricao"])))
        elif op == '3':
            p = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
            if p: update_produto(p)
        elif op == '4':
            p = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
            if p: delete_produto(p["_id"], p["id_vendedor"])
        elif op == 'V': break

def selecionar_compra_por_produto():
    produto = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
    if not produto:
        return None
    compras = read("compras", {"produtos.id_produto": produto["_id"]})
    if not compras:
        print("Nenhuma compra encontrada para esse produto.")
        return None
    return selecionar_item(compras)

def menu_compra():
    while True:
        print("\n--- Menu da Compra ---")
        print("1- Realizar Compra \n2- Listar Compras \n3- Update \n4- Delete \n5- Itens Compra \n6- Vendedores Compra \nV- Voltar")
        op = input("Opção: ").upper()
        if op == '1': create_compra()
        elif op == '2':
            p = selecionar_item(read("produtos", montar_query(["nome", "descricao"])))
            if p: exibir_lista(read("compras", {"produtos.id_produto": p["_id"]}))
        elif op == '3':
            c = selecionar_compra_por_produto()
            if c: update_compra(c)
        elif op == '4':
            c = selecionar_compra_por_produto()
            if c: delete_compra(c)
        elif op == '5':
            c = selecionar_compra_por_produto()
            if c: exibir_lista(c.get("produtos", []))
        elif op == '6':
            c = selecionar_compra_por_produto()
            if c:
                ids = {p["id_vendedor"] for p in c.get("produtos", [])}
                for vid in ids:
                    v = db.vendedores.find_one({"_id": vid})
                    print(f"- {v['nome'] if v else 'Desconhecido'}")
        elif op == 'V': break


def main():
    while True:
        print("\n=== SISTEMA MERCADO LIVRE ===")
        print("1- Usuários \n2- Vendedores \n3- Produtos \n4- Compras \nS- Sair")
        opcao = input("Opção: ").upper()
        if   opcao == '1': menu_usuario()
        elif opcao == '2': menu_vendedor()
        elif opcao == '3': menu_produto()
        elif opcao == '4': menu_compra()
        elif opcao == 'S': break

if __name__ == "__main__":
    main()