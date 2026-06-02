import hashlib

def hash_senha(senha: str):
    return hashlib.sha256(senha.encode()).hexdigest()

def exibir_lista(lista: list):
    if not lista:
        print("Nenhum registro encontrado.")
        return
        
    for i, item in enumerate(lista):
        print(f"[{i}] ", end="")
        for key, value in item.items():
            if key in ["_id", "senha", "produtos", "favoritos", "compras", "fotos"]:
                continue
            
            if key == "enderecos" and isinstance(value, list):
                cidades = [e.get("cidade", "") for e in value]
                value = f"{len(value)} endereço(s) ({', '.join(cidades)})"
             
            print(f"{key}: {value}", end=" | ")
        print()

def selecionar_item(lista: list):
    if not lista:
        print("Nenhum registro encontrado.")
        return None
        
    exibir_lista(lista)
    try:
        idx = int(input("\nDigite o número do index desejado: "))
        if 0 <= idx < len(lista):
            return lista[idx]
        else:
            print("Index fora do alcance.")
    except ValueError:
        print("Entrada inválida.")
    return None

def montar_query(campos_busca: list):
    print("Deixe o campo em branco (Enter) caso não queira filtrar por ele.")
    query = {}
    for campo in campos_busca:
        valor = input(f"Filtrar por [{campo}]: ").strip()
        if valor:
            query[campo] = {"$regex": valor, "$options": "i"}
    return query

def coletar_lista_strings(nome_campo: str):
    itens = []
    print(f"\n--- Cadastrando {nome_campo} ---")
    while True:
        valor = input(f"Digite um valor para {nome_campo} (ou apenas Enter para parar): ").strip()
        if not valor:
            break
        itens.append(valor)
    return itens

def coletar_enderecos():
    enderecos = []
    print("\n--- Cadastro de Endereços (Obrigatório) ---")
    while True:
        print(f"\nEndereço {len(enderecos) + 1}:")
        end = {
            "rua": input("Rua: ").strip(),
            "numero": input("Número: ").strip(),
            "bairro": input("Bairro: ").strip(),
            "cidade": input("Cidade: ").strip(),
            "estado": input("Estado: ").strip(),
            "cep": input("CEP: ").strip(),
            "complemento": input("Complemento (Opcional): ").strip() or " "
        }
        
        if all(end.values()):
            enderecos.append(end)
        else:
            print("Rua, Número, Cidade e Estado são obrigatórios.")
            continue
            
        resp = input("Deseja adicionar outro endereço? (S/N): ").upper()
        if resp != 'S':
            if len(enderecos) > 0:
                break
            print("Cadastre pelo menos 1 endereço válido!")
    return enderecos