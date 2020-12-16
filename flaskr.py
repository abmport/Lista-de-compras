import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing

DATABASE = './tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('CONFIG_FLASKR', silent=True)

def conectar_bd():
    return sqlite3.connect(app.config['DATABASE'])

def criar_bd():
    with closing(conectar_bd()) as bd:
        with app.open_resource('banco.sql') as sql:
            bd.cursor().executescript(sql.read().decode('utf-8'))
        bd.commit()

conectar_bd()
criar_bd()

@app.before_request
def pre_requisecao():
    g.bd = conectar_bd()

@app.teardown_request
def encerrar_requisicao(exception):
    g.bd.close()

@app.route('/')
def principal():
    return render_template('index.html')

@app.route('/minhalista')
def minha_lista():
    sql = '''select id, produto, valor from lista order by id desc'''
    cur = g.bd.execute(sql)
    listas = [dict(id=id, produto=produto, valor=valor)
                for id, produto, valor in cur.fetchall()]
    return render_template('lista.html', listas=listas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            erro = 'Usuario inválido'
        elif request.form['password'] != app.config['PASSWORD']:
            erro = 'Senha inválida'
        else:
            session['logado'] = True
            flash('Login OK')
            return redirect(url_for('minha_lista'))
    return render_template('login.html', erro=erro)
    
@app.route('/logout')
def logout():
    session.pop('logado', None)
    flash('Você saiu da conta.')
    return redirect(url_for('minha_lista'))

@app.route('/excluiritem', methods=['POST'])
def excluiritem():
    if not session.get('logado'):
        abort(401)
    sql = '''delete from lista where id=(?)'''
    g.bd.execute(sql, [request.form['id']])
    g.bd.commit()
    return redirect(url_for('minha_lista'))

@app.route('/adicionaritem', methods=['POST'])
def adicionaritem():
    if not session.get('logado'):
        abort(401)
    sql = '''insert into lista (produto, valor) values (?, ?)'''
    g.bd.execute(sql, [request.form['produto'], request.form['valor']])
    g.bd.commit()
    return redirect(url_for('minha_lista'))


if __name__ == "__main__":
    app.run()