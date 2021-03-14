from datetime import date, time
from functools import wraps
from routes import flash, session, redirect, url_for
from conect import *
from pygal import StackedBar


conexao = ConectMongo()


#retorna a data atual formatada
def date_format():
    data_atual = date.today()
    data_str = data_atual.strftime('%d/%m/%Y')
    return data_str


#faz o controle de sessão do usuário'''
def login_required(run):
	@wraps(run)
	def wrap(*args, **kwargs):
		if 'usuario' in session:
			return run(*args, **kwargs)
		else:
			flash('Por favor! Efetue o login primeiro!')
			return redirect(url_for('login'))
	return wrap


#faz o controle das permissoes do menu
def valida_permissao():
    permissao = conexao.search('usuarios', {'usuario': session['usuario']})
    return permissao['permissao']


#lista os setores cadastrados no banco
def lista_setores():
	setores = conexao.list('setores')
	aux = []

	for i in setores:
		aux.append(i['setor'])

	return aux


#lista as impressoras cadastradas no banco
def lista_impressoras():
	impressoras = conexao.list('impressoras')
	aux = []

	for i in impressoras:
		aux.append(i['impressora'])

	return aux


#lista o nome do usuario que esta na sessão para salvar na abertura e encerramento do chamado
def nome_usuario():
    return conexao.search('usuarios', {'usuario': session['usuario']})['nome']


#faz a conversão dos meses escritos para números
def coverte_mes(mes):
	if mes == 'Janeiro':
		return 1

	elif mes == 'Fevereiro':
		return 2

	elif mes == 'Março':
		return 3

	elif mes == 'Abril':
		return 4

	elif mes == 'Maio':
		return 5

	elif mes == 'Junho':
		return 6

	elif mes == 'Julho':
		return 7

	elif mes == 'Agosto':
		return 8

	elif mes == 'Setembro':
		return 9

	elif mes == 'Outubro':
		return 10

	elif mes == 'Novembro':
		return 11

	else:
		return 12


#faz o filtro para gerar um novo relatório
def gera_relatorio(mes, ano, tipo):
	mes_num = coverte_mes(mes)
	list_chamados = conexao.list('chamados')
	lita_setores = conexao.list('setores')
	relatorio = []
	aux = []

	for i in lita_setores:  #cria uma lista de listas onde cada setor recebe um número inicial da quantidade de atendimentos
		aux.append(i['setor'])
		aux.append(0)
		relatorio.append(aux[:])
		aux = []

	for i in list_chamados:
		for y in range(1, 32, 1):
			data = '{:02d}/{:02d}/{}'.format(y, mes_num, ano)
			if i['data_abertura'] == data and i['tipo'] == tipo:
				for w in relatorio:
					if w[0] == i['setor']:
						w[1] = w[1] + 1

	return relatorio


def num_chamados(mes, ano):
	list_chamados = conexao.list('chamados')
	num = [0, 0, 0]

	for i in list_chamados:
		for y in range(1, 32, 1):
			data = '{:02d}/{:02d}/{}'.format(y, mes, ano)
			if i['data_abertura'] == data and i['tipo'] == 'TI':
				num[0] += 1

			elif i['data_abertura'] == data and i['tipo'] == 'Manutenção':
				num[1] += 1

			elif i['data_abertura'] == data and i['tipo'] == 'Impressoras':
				num[2] += 1

	if num[0] == 0:
		num[0] = None

	if num[1] == 0:
		num[1] = None

	if num[2] == 0:
		num[2] = None

	return num


def grafico():
	a = date.today()
	ano = a.year

	janeiro = num_chamados(1, ano)
	fevereiro = num_chamados(2, ano)
	marco = num_chamados(3, ano)
	abril = num_chamados(4, ano)
	maio = num_chamados(5, ano)
	junho = num_chamados(6, ano)
	julho = num_chamados(7, ano)
	agosto = num_chamados(8, ano)
	setembro = num_chamados(9, ano)
	outubro = num_chamados(10, ano)
	novembro = num_chamados(11, ano)
	dezembro = num_chamados(12, ano)

	new_grafic = StackedBar()
	new_grafic.title = 'Chamados ano: {}'.format(ano)
	new_grafic.x_labels = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
						   'Outubro', 'Novembro', 'Dezembro')
	new_grafic.add('TI', [janeiro[0], fevereiro[0], marco[0], abril[0], maio[0], junho[0], julho[0],
						  agosto[0], setembro[0], outubro[0], novembro[0], dezembro[0]])
	new_grafic.add('Manutenção', [janeiro[1], fevereiro[1], marco[1], abril[1], maio[1], junho[1], julho[1],
					agosto[1], setembro[1], outubro[1], novembro[1], dezembro[1]])
	new_grafic.add('Impressora', [janeiro[2], fevereiro[2], marco[2], abril[2], maio[2], junho[2], julho[2],
					agosto[2], setembro[2], outubro[2], novembro[2], dezembro[2]])

	new_grafic.render_to_file('static/imagens/new_grafic.svg')
	img_url = 'static/imagens/new_grafic.svg?cache=' + str(time())
	return img_url
