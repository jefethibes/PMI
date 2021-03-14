from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, Response
from flask_wtf import CSRFProtect
from bson.objectid import ObjectId
from utility import *
from forms import *
from conect import *
from reportlab.pdfgen import canvas
from xlwt import Workbook
from io import BytesIO


conexao = ConectMongo()

app = Flask(__name__)
app.secret_key = 'não_me_hackeia_plz'
csrf = CSRFProtect(app)


@app.route('/', methods=['GET', 'POST'])
def login():  #verifica login do usuário
    field = Login(request.form)  #valida o formulario de login

    if request.method == 'POST' and field.validate():  #so executa se for validado
        usuario = request.form['usuario']
        senha = request.form['senha']
        json = {'usuario': usuario, 'senha': senha}
        validacao = conexao.search('usuarios', json)  #verifica se usuario existe no banco

        if validacao is None: #se retorno do banco for igual a None retorna a menssagem
            flash('Usuário ou senha inválido!')
            return redirect(url_for('login'))

        elif validacao['status'] == 'Bloqueado':  #se o usuario tiver bloqueado retornara a menssagem
            flash('Usuário bloqueado! Favor entrar em contato com o administrador!')
            return redirect(url_for('login'))

        else:  #se usuário tiver correto o sistema apresentara o index
            session['usuario'] = field.usuario.data
            flash('Bem vindo {}!'.format(validacao['nome']))
            return redirect(url_for('index'))

    return render_template('login.html', field=field)  #se o metodo chamado for GET vai apresentar a tela de login


@app.route('/logout')
@login_required
def logout():  #encerra sessão do usuário
    if 'usuario' in session:
        session.pop('usuario')
    return redirect(url_for('login'))


@app.route('/index', methods=['GET'])
@login_required
def index():  #home do sistema
    return render_template('index.html', permissao=valida_permissao())


@app.route('/ti', methods=['GET', 'POST'])
@login_required
def chamados_ti(): #abertura de chamados de ti
    field = Chamados(request.form)  #valida os campos de abertura de chamado de ti

    if request.method == 'POST' and field.validate():  #se todos os campos estiverem corretos o sistema adiciona o chamado
        setor = request.form['setor']
        titulo = request.form['titulo']
        urgencia = request.form['urgencia']
        comentario = request.form['comentario']
        json = {'status': 'Aberto', 'tipo': 'TI', 'setor': setor, 'urgencia': urgencia,
                'titulo': titulo, 'comentario': comentario, 'data_abertura': date_format(), 'usuario': nome_usuario()}
        conexao.add('chamados', json)  #passa um dicionario para a classe conect inserir os dados no banco
        flash('Chamado cadastrado com sucesso!')
        return redirect(url_for('meus_chamados'))  #redireciona para a pagina de meus chamados

    return render_template('chamados.html', field=field, title='Chamado TI!', setores=lista_setores(),
                           permissao=valida_permissao(), tipo_chamado='ti')


@app.route('/manutencao', methods=['GET', 'POST'])
@login_required
def chamados_manutencao():  #abertura de chamado de manutenção
    field = Chamados(request.form)  #valida os campos de cadastro de chamado de manutenção

    if request.method == 'POST' and field.validate():  #se todos os campos estiverem corretos o sistema adiciona o chamado
        setor = request.form['setor']
        titulo = request.form['titulo']
        urgencia = request.form['urgencia']
        comentario = request.form['comentario']
        json = {'status': 'Aberto', 'tipo': 'Manutenção', 'setor': setor, 'urgencia': urgencia,
                'titulo': titulo, 'comentario': comentario, 'data_abertura': date_format(), 'usuario': nome_usuario()}
        conexao.add('chamados', json)  #passa um dicionario para a classe conect inserir os dados no banco
        flash('Chamado cadastrado com sucesso!')
        return redirect(url_for('meus_chamados'))  #redireciona para a pagina de meus chamados

    return render_template('chamados.html', field=field, title='Chamado Manutenção!', setores=lista_setores(),
                           permissao=valida_permissao(), tipo_chamado='manutenção')


@app.route('/impressoras', methods=['GET', 'POST'])
@login_required
def chamados_impressoras(): #abertura de chamado de impressoras
    field = Chamados(request.form)  #valida os campos de cadastro de chamado de impressoras

    if request.method == 'POST' and field.validate(): #se todos os campos estiverem corretos o sistema adiciona o chamado
        titulo = request.form['titulo']
        setor = request.form['setor']
        modelo = request.form['modelo']
        comentario = request.form['comentario']
        json = {'status': 'Aberto', 'tipo': 'Impressoras', 'setor': setor, 'modelo': modelo,
                'titulo': titulo, 'comentario': comentario, 'data_abertura': date_format(), 'usuario': nome_usuario()}
        conexao.add('chamados', json)  #passa um dicionario para a classe conect inserir os dados no banco
        flash('Chamado cadastrado com sucesso!')
        return redirect(url_for('meus_chamados'))  #redireciona para a pagina de meus chamados

    return render_template('chamados.html', field=field, setores=lista_setores(), modelos=lista_impressoras(),
                           permissao=valida_permissao(), tipo_chamado='impressoras', title='Chamado Impressora!')


@app.route('/meus_chamados/', methods=['GET', 'POST'])
@login_required
def meus_chamados():  #lista os chamados aberto pelo usuário logado
    chamados = conexao.list('chamados')  #traz todos os chamados que estão no banco
    itens = []

    for i in chamados:
        if i['usuario'] == nome_usuario() and i['status'] == 'Aberto':  #seleciona os chamados do usuario que esta logado e adiciona na lista
            itens.append(i)

    return render_template('lista_chamados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/meus_chamados_encerrados/', methods=['GET', 'POST'])
@login_required
def meus_chamados_encerrados():  #lista os chamados aberto pelo usuário logado
    chamados = conexao.list('chamados')  #traz todos os chamados que estão no banco
    itens = []

    for i in chamados:
        if i['usuario'] == nome_usuario() and i['status'] == 'Encerrado':  #seleciona os chamados do usuario que esta logado e adiciona na lista
            itens.append(i)

    return render_template('lista_chamados_encerrados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/chamados_ti/', methods=['GET', 'POST'])
@login_required
def suporte_ti():  #lista os chamados de ti
    chamados = conexao.list('chamados')  #traz todos os chamados que estão no banco
    itens = []

    for i in chamados:
        if i['tipo'] == 'Impressoras' or i['tipo'] == 'TI':  #seleciona apenas os chamados de TI e de Impressoras e adiciona a lista
            if i['status'] == 'Aberto':
                itens.append(i)

    return render_template('lista_chamados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/chamados_ti_encerrados/', methods=['GET', 'POST'])
@login_required
def suporte_ti_encerrados():  #lista os chamados de ti
    chamados = conexao.list('chamados')  #traz todos os chamados que estão no banco
    itens = []

    for i in chamados:
        if (i['tipo'] == 'Impressoras' or i['tipo'] == 'TI') and (i['status'] == 'Encerrado'):  #seleciona apenas os chamados de TI e de Impressoras e adiciona a lista
            itens.append(i)

    return render_template('lista_chamados_encerrados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/chamados_manutencao/', methods=['GET', 'POST'])
@login_required
def suporte_manutencao():  #lista os chamados de manutenção
    chamados = conexao.list('chamados')  #traz toos os chamado que estão no banco
    itens = []

    for i in chamados:
        if i['tipo'] == 'Manutenção' and i['status'] == 'Aberto':  #seleciona apenas os chamado de manutenção e adiciona a lista
            itens.append(i)

    return render_template('lista_chamados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/chamados_manutencao_encerrados/', methods=['GET', 'POST'])
@login_required
def suporte_manutencao_encerrados():  #lista os chamados de manutenção
    chamados = conexao.list('chamados')  #traz toos os chamado que estão no banco
    itens = []

    for i in chamados:
        if i['tipo'] == 'Manutenção' and i['status'] == 'Encerrado':  #seleciona apenas os chamado de manutenção e adiciona a lista
            itens.append(i)

    return render_template('lista_chamados_encerrados.html', itens=itens, permissao=valida_permissao(), tamanho=len(itens))


@app.route('/encerrar/<_id>', methods=['GET', 'POST'])
@login_required
def encerrar(_id):  #encerra chamado
    field = Encerramento(request.form)  #valida os campos do encerramento de chamado
    itens = conexao.search('chamados', ObjectId(_id))  #busca o chamado que deve ser encerrado pelo id

    if request.method == 'POST' and field.validate():  #se os campos estiverem corretos ele acrecenta os outros campos ao chamado encerrado
        itens['data_encerramento'] = date_format()
        itens['resolucao'] = request.form['comentario']
        itens['responsavel'] = nome_usuario()
        itens['status'] = 'Encerrado'
        conexao.update('chamados', {'_id': ObjectId(_id)}, itens)

        if valida_permissao() == 'Suporte TI':  #se usuario que encerrou for do suporte TI redireciona para os chamado ti
            flash('Chamado encerrado com sucesso!')
            return redirect(url_for('suporte_ti'))

        elif valida_permissao() == 'Suporte Manutenção':  #se usuario que encerrou for suporte manutenção redireciona para os chamado de manutenção
            flash('Chamado encerrado com sucesso!')
            return redirect(url_for('suporte_manutencao'))

        else:  #se não for nenhum redireciona para o meus chamados
            flash('Chamado encerrado com sucesso!')
            return redirect(url_for('meus_chamados'))

    return render_template('encerrar_chamado.html', itens=itens, field=field, permissao=valida_permissao())


@app.route('/visualizar_chamado/<_id>', methods=['GET'])
@login_required
def visualizar_chamado(_id):
    itens = conexao.search('chamados', ObjectId(_id))

    return render_template('visualizar_chamado.html', itens=itens, permissao=valida_permissao())


@app.route('/gerenciar_usuarios', methods=['GET'])
@login_required
def gerenciar_usuarios():  #gerencia usuarios
    itens = conexao.list('usuarios')

    return render_template('usuarios.html', itens=itens, permissao=valida_permissao())


@app.route('/criar_usuario', methods=['GET', 'POST'])
@login_required
def criar_usuario():  #cria usuario
    field = CriarUsuario(request.form)  #valida os campos do formulario

    if request.method == 'POST' and field.validate():  #se os campos forem validados ele procegue
        usuario = request.form['usuario']

        if conexao.search('usuarios', {'usuario': usuario}) is None:  #valida se o usuario ja existe
            senha = request.form['senha']
            setor = request.form['setor']
            nome = request.form['nome']
            sobrenome = request.form['sobrenome']
            email = request.form['email']
            status = request.form['status']
            permissao = request.form['permissao']
            json = {'usuario': usuario, 'senha': senha, 'setor': setor, 'nome': nome, 'sobrenome': sobrenome,
                    'email': email, 'status': status, 'permissao': permissao}
            conexao.add('usuarios', json)  #adiciona um novo usuario ao banco
            flash('Cadastro efetuado com sucesso!')
            return redirect(url_for('gerenciar_usuarios'))

        else:
            flash('Usuário já existe!')

    return render_template('criar_usuario.html', field=field, permissao=valida_permissao(), setores=lista_setores())


@app.route('/alterar_usuario/<_id>', methods=['GET', 'POST'])
@login_required
def alterar_usuario(_id):  #altera um usuário pelo id
    field = AlteraUsuario(request.form)  # valida os campos do formulario
    itens = conexao.search('usuarios', ObjectId(_id))  #procura o usuario no banco para listar

    if request.method == 'POST' and field.validate():  #depois de todos os campos estarem validados procegue com o update
        usuario = request.form['usuario']

        if (conexao.search('usuarios', {'usuario': usuario}) is None) or (usuario == itens['usuario']):  # valida se o usuario ja existe
            senha = request.form['senha']
            setor = request.form['setor']
            nome = request.form['nome']
            sobrenome = request.form['sobrenome']
            email = request.form['email']
            status = request.form['status']
            permissao = request.form['permissao']
            json = {'usuario': usuario, 'senha': senha, 'setor': setor, 'nome': nome, 'sobrenome': sobrenome,
                    'email': email, 'status': status, 'permissao': permissao}
            conexao.update('usuarios', {'_id': ObjectId(_id)}, json)  #altera o usuario no banco
            flash('Usuário alterado com sucesso!')
            return redirect(url_for('gerenciar_usuarios'))

        else:
            flash('Usuário já existe!')

    return render_template('alterar_usuario.html', itens=itens, permissao=valida_permissao(),
                           setores=lista_setores(), field=field)


@app.route('/alterar_status/<_id>', methods=['GET', 'PUT'])
@login_required
def alterar_status(_id):  #altera o status do usuario bloqueado ou ativo
    itens = conexao.search('usuarios', ObjectId(_id))  #busca o usuario no banco

    if itens['status'] == 'Bloqueado':  #se ele tiver bloqueado ele altera para ativo
        itens['status'] = 'Ativo'
        conexao.update('usuarios', {'_id': ObjectId(_id)}, itens)
        return redirect(url_for('gerenciar_usuarios'))

    else:
        itens['status'] = 'Bloqueado'  #se ele tiver ativo ele altera para bloqueado
        conexao.update('usuarios', {'_id': ObjectId(_id)}, itens)
        return redirect(url_for('gerenciar_usuarios'))


@app.route('/configuracoes', methods=['GET', 'DELETE'])
@login_required
def configuracoes():  #lista as impressoras e os setores para gerenciamento
    impressoras = conexao.list('impressoras')
    setores = conexao.list('setores')

    return render_template('configuracoes.html', permissao=valida_permissao(), setores=setores,
                           impressoras=impressoras)


@app.route('/deletar_impressora/<_id>', methods=['GET', 'DELETE'])
@login_required
def deletar_impressora(_id):  #deleta impressora do banco
    conexao.delete('impressoras', {'_id': ObjectId(_id)})
    flash('Impressora removida com sucesso!')

    return redirect(url_for('configuracoes'))


@app.route('/deletar_setor/<setor>', methods=['GET', 'DELETE'])
@login_required
def deletar_setor(setor):  #deleta setor pelo id
    if conexao.search('usuarios', {'setor': setor}) is None:  #busca no cadastro de usuarios se tem algum usuario cadastrado no setor, se não tiver o setor e removido
        conexao.delete('setores', {'setor': setor})
        flash('Setor removido com sucesso!')

        return redirect(url_for('configuracoes'))

    else:
        flash('Setor não pode ser deletado, há usuários cadastrados nesse setor!')

        return redirect(url_for('configuracoes'))


@app.route('/add_setor', methods=['GET', 'POST'])
@login_required
def add_setor():  #adiciona um novo setor
    if (request.method == 'POST') and (conexao.search('setores', {'setor': request.form['setor']}) is None):  #se ele não existor no banco ele adiciona
        conexao.add('setores', {'setor': request.form['setor']})
        flash('Setor adicionado com sucesso!')

        return redirect(url_for('configuracoes'))

    else:  #se existir retorna a mensgame
        flash('Setor já cadastrado!')

        return redirect(url_for('configuracoes'))


@app.route('/add_impressora', methods=['GET', 'POST'])
@login_required
def add_impressora():  #adiciona uma nova impressora
    if (request.method == 'POST') and (conexao.search('impressoras', {'impressora': request.form['impressora']}) is None):  #se ele não existor no banco ele adiciona
        conexao.add('impressoras', {'impressora': request.form['impressora']})
        flash('Impressora adicionada com sucesso!')

        return redirect(url_for('configuracoes'))

    else:  #se existir retorna a mensgame
        flash('Impressora já cadastrada!')

        return redirect(url_for('configuracoes'))


@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():  #gera relatorios na página html
    if request.method == 'POST':
        mes = request.form['mes']
        ano = request.form['ano']
        tipo = request.form['tipo']
        lista_relatorios = gera_relatorio(mes, ano, tipo)
        rel = request.form['rel']
        print(lista_relatorios)

        if rel == 'Excel':
            output = BytesIO()
            relatorio = Workbook()
            tabela = relatorio.add_sheet('Relatorio')
            tabela.write(0, 0, 'Filtro:')
            tabela.write(0, 1, '{}/{}'.format(mes, ano))
            tabela.write(2, 0, 'Setor')
            tabela.write(2, 1, 'Quantidade de chamados')

            linha = 3

            if len(lista_relatorios) > 0:
                for iten in lista_relatorios:
                    tabela.write(linha, 0, iten[0])
                    tabela.write(linha, 1, iten[1])
                    linha += 1

            relatorio.save(output)
            output.seek(0)

            return Response(output, mimetype="application/ms-excel",
                            headers={'Content-Disposition': 'attachment;filename=relatorio.xls'})

        else:
            pdf = canvas.Canvas('Relatorio.pdf')
            x = 650
            for iten in lista_relatorios:
                x -= 20
                pdf.drawString(75, x, '{} : {}'.format(iten[0], iten[1]))
            pdf.setFont('Helvetica-Oblique', 15)
            pdf.drawString(250, 750, 'Relatório {}'.format(tipo))
            pdf.setFont('Helvetica-Oblique', 12)
            pdf.drawString(75, 700, 'filtro: {}/{}'.format(mes, ano))
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(75, 670, 'Setor e Número chamados')
            pdf.save()
            return send_file('C:\Workspace\PMI\Relatorio.pdf', attachment_filename='Relatorio.pdf')

    return render_template('relatorios.html', permissao=valida_permissao(), grafico=grafico())
