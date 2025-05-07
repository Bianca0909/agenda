from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    contatos = db.relationship('Contato', backref='proprietario', lazy=True)
    mensagens_enviadas = db.relationship('Mensagem', backref='remetente', lazy=True,
                                       foreign_keys='Mensagem.remetente_id')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.email}>'

class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120))
    celular = db.Column(db.String(20))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    mensagens_recebidas = db.relationship('Mensagem', backref='contato', lazy=True,
                                        foreign_keys='Mensagem.contato_id')

    def __repr__(self):
        return f'<Contato {self.nome}>'

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    contato_id = db.Column(db.Integer, db.ForeignKey('contato.id'), nullable=False)

    def __repr__(self):
        return f'<Mensagem {self.id}>'
