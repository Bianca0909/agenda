import os
from flask import (Flask, render_template, redirect, url_for, flash, request)
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from models import db, Usuario, Contato, Mensagem

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def carregar_usuario(user_id):
    return Usuario.query.get(int(user_id))

# Criar o banco de dados se não existir
def criar_banco():
    with app.app_context():
        # Cria as tabelas apenas se elas não existirem
        db.create_all()

@app.route('/', methods=['GET'])
@login_required
def inicio():
    return render_template('home.html')

@app.route('/contatos/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar_contato():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        celular = request.form.get('celular')

        if not nome:
            flash('O nome é obrigatório.', 'danger')
            return redirect(url_for('adicionar_contato'))

        novo_contato = Contato(
            nome=nome,
            email=email,
            celular=celular,
            usuario_id=current_user.id
        )

        db.session.add(novo_contato)
        db.session.commit()

        flash('Contato adicionado com sucesso!', 'success')
        return redirect(url_for('listar_contatos'))

    return render_template('cadastro_contato.html', contato=None)

@app.route('/contatos')
@login_required
def listar_contatos():
    contatos = Contato.query.filter_by(usuario_id=current_user.id).order_by(Contato.nome).all()
    return render_template('listagem_contato.html', contatos=contatos)

@app.route('/contatos/<int:contato_id>/excluir')
@login_required
def excluir_contato(contato_id):
    contato = Contato.query.filter_by(id=contato_id, usuario_id=current_user.id).first_or_404()
    db.session.delete(contato)
    db.session.commit()
    flash('Contato excluído com sucesso!', 'success')
    return redirect(url_for('listar_contatos'))

@app.route('/contatos/<int:contato_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_contato(contato_id):
    contato = Contato.query.filter_by(id=contato_id, usuario_id=current_user.id).first_or_404()

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        celular = request.form.get('celular')

        if not nome:
            flash('O nome é obrigatório.', 'danger')
            return redirect(url_for('editar_contato', contato_id=contato_id))

        contato.nome = nome
        contato.email = email
        contato.celular = celular

        db.session.commit()
        flash('Contato atualizado com sucesso!', 'success')
        return redirect(url_for('listar_contatos'))

    return render_template('cadastro_contato.html', contato=contato)

# Rotas de Mensagem
@app.route('/contatos/<int:contato_id>/chat')
@login_required
def chat_contato(contato_id):
    contato = Contato.query.filter_by(id=contato_id, usuario_id=current_user.id).first_or_404()
    mensagens = Mensagem.query.filter_by(contato_id=contato_id).order_by(Mensagem.data_envio).all()
    return render_template('chat_contato.html', contato=contato, mensagens=mensagens)

@app.route('/contatos/<int:contato_id>/enviar', methods=['POST'])
@login_required
def enviar_mensagem(contato_id):
    contato = Contato.query.filter_by(id=contato_id, usuario_id=current_user.id).first_or_404()
    mensagem_texto = request.form.get('mensagem')

    if not mensagem_texto:
        flash('A mensagem não pode estar vazia.', 'danger')
        return redirect(url_for('chat_contato', contato_id=contato_id))

    nova_mensagem = Mensagem(
        conteudo=mensagem_texto,
        remetente_id=current_user.id,
        contato_id=contato_id
    )

    db.session.add(nova_mensagem)
    db.session.commit()

    return redirect(url_for('chat_contato', contato_id=contato_id))

# Rotas de Autenticação
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        # Validar força da senha
        from utils import validar_senha
        senha_valida, erro_senha = validar_senha(senha)
        if not senha_valida:
            flash(erro_senha, 'danger')
            return render_template('cadastro_usuario.html')

        if senha != confirmar_senha:
            flash('As senhas não coincidem', 'danger')
            return render_template('cadastro_usuario.html')

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            flash('Email já cadastrado', 'danger')
            return render_template('cadastro_usuario.html')

        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            proxima_pagina = request.args.get('next')
            return redirect(proxima_pagina or url_for('inicio'))
        else:
            flash('Email ou senha inválidos.', 'danger')

    return render_template('login.html')

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    criar_banco()
    app.run(debug=True)