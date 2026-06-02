# Sistema Mercado Livre - MongoDB com Python (EX2_BDNR)

Este projeto implementa um sistema de manipulação de um Banco de Dados Não Relacional (MongoDB) em Python, simulando as operações do Mercado Livre. O sistema realiza as operações de CRUD (Create, Read, Update, Delete) para as coleções de Usuários, Vendedores, Produtos e Compras.

## Como Rodar o projeto

Siga os passos abaixo para configurar o ambiente e executar o script na sua máquina.

### 1. Criar o Ambiente Virtual (venv)
O ambiente virtual isola as dependências do projeto para que não entrem em conflito com outras bibliotecas instaladas no seu computador.

Abra o terminal na pasta raiz do projeto e execute:

**No Windows:**
```bash
python -m venv venv
```
**No Linux/macOS:**
```bash
python3 -m venv venv
```

### 2. Ativar o Ambiente Virtual
Sempre que for trabalhar no projeto ou rodá-lo, o ambiente virtual precisa estar ativado.

**No Windows:**
```bash
venv\Scripts\activate
```
**No Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente (.env)
Este projeto utiliza o MongoDB Atlas (nuvem). Para proteger suas credenciais de acesso, usamos variáveis de ambiente.
```bash
USER=seu_usuario_do_mongodb
PASSWORD=sua_senha_do_mongodb
```
(Nota: Substitua seu_usuario_do_mongodb e sua_senha_do_mongodb pelas credenciais reais configuradas no MongoDB Atlas. Não use aspas nos valores).

### 5. Executar a Aplicação
Com tudo configurado e o ambiente virtual ativado, basta rodar o arquivo principal para interagir com o menu do sistema:
```bash
python app.py
```
