from pymongo import MongoClient


#classe que faz o controle de dados com o mongo'''
class ConectMongo:

    #dados da conexao com o mongo'''
    def __init__(self):
        try:
            self.conect = MongoClient('localhost', 27017)
            self.dataBase = self.conect.suporte
        except Exception as e:
            print(e)

    #função que insere dados no banco, variavel col recebe o nome da coleção e o json os dados que serão inseridos'''
    def add(self, col, json):
        try:
            collection = self.dataBase[col]
            return collection.insert_one(json)
        except Exception as e:
            print(e)

    #faz a busca de um unico arquivo no banco'''
    def search(self, col, json):
        try:
            collection = self.dataBase[col]
            return collection.find_one(json)
        except Exception as e:
            print(e)

    #lista todos os arquivos da collection passada
    def list(self, col):
        try:
            collection = self.dataBase[col]
            return collection.find()
        except Exception as e:
            print(e)

    #faz alterações em um arquivo do banco
    def update(self, col, _id, query):
        try:
            colecao = self.dataBase[col]
            colecao.update(_id, query)
        except Exception as e:
            print(e)

    #deleta um unico arquivo do banco
    def delete(self, col, _id):
        try:
            colecao = self.dataBase[col]
            colecao.delete_one(_id)
        except Exception as e:
            print(e)
