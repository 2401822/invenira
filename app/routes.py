import requests
from flask import request, jsonify, render_template, redirect, url_for, session
from app import observable


def register_routes(app):
    def get_base_url():
        """Obtém a URL base do servidor atual."""
        return request.host_url.rstrip('/')

    # Página inicial
    @app.route('/')
    def index():
        if 'user_id' in session:
            response = requests.get(f"{get_base_url()}/api/usuarios/{session['user_id']}")
            if response.status_code == 200:
                usuario = response.json()
                if usuario['tipo'] == 'instrutor':
                    return redirect(url_for('instrutor_dashboard'))
                elif usuario['tipo'] == 'aluno':
                    return redirect(url_for('aluno_dashboard'))
        return redirect(url_for('login'))

    # Página de login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.json
            email = data.get('email')
            senha = data.get('senha')

            response = requests.get(f"{get_base_url()}/api/usuarios/email/{email}")
            if response.status_code == 200:
                usuario = response.json()
                if usuario and usuario['senha'] == senha:
                    session['user_id'] = usuario['id']
                    session['user_nome'] = usuario['nome']
                    session['user_tipo'] = usuario['tipo']

                    observable.notify_observers("Login", f"Usuário {usuario['nome']} fez login.")
                    return jsonify({"message": "Login realizado com sucesso!", "tipo": usuario['tipo']}), 200
            return jsonify({"message": "Credenciais inválidas"}), 401

        return render_template('login.html')

    # Página de registro
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            data = request.json
            response = requests.post(f"{get_base_url()}/api/usuarios/criar", json=data)
            if response.status_code == 201:
                usuario = response.json()
                observable.notify_observers("Registro", f"Novo usuário registrado: {usuario['nome']}.")
                return jsonify({"message": "Usuário registrado com sucesso"}), 201
            return jsonify({"message": "Erro ao registrar usuário"}), 400

        return render_template('register.html')

    # Logout
    @app.route('/logout', methods=['GET'])
    def logout():
        usuario_nome = session.get('user_nome', 'Usuário desconhecido')
        session.clear()
        observable.notify_observers("Logout", f"Usuário {usuario_nome} fez logout.")
        return redirect(url_for('login'))


    # Dashboard do Instrutor
    @app.route('/instrutor/dashboard', methods=['GET'])
    def instrutor_dashboard():
        response = requests.get(f"{get_base_url()}/api/atividades/listar")
        atividades = response.json() if response.status_code == 200 else []
        return render_template('dashboard_instrutor.html', atividades=atividades, usuario_nome=session.get('user_nome'))

    # Criar Atividade
    @app.route('/instrutor/atividades/criar', methods=['GET', 'POST'])
    def criar_atividade():
        if request.method == 'POST':
            data = {
                "titulo": request.form.get('titulo'),
                "descricao": request.form.get('descricao'),
                "configuracoes": {
                    "dificuldade": request.form.get('dificuldade'),
                    "tempo_estimado": int(request.form.get('tempo_estimado'))
                },
                "criado_por": session['user_id']
            }
            response = requests.post(f"{get_base_url()}/api/atividades/criar", json=data)
            if response.status_code == 201:
                atividade = response.json()
                observable.notify_observers("Criação de Atividade", f"Atividade criada: {atividade['titulo']}")
            return redirect(url_for('instrutor_dashboard'))
        return render_template('criar_atividade.html', usuario_nome=session.get('user_nome'))

    # Editar Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/editar', methods=['GET', 'POST'])
    def editar_atividade(atividade_id):
        response = requests.get(f"{get_base_url()}/api/atividades/{atividade_id}")
        atividade = response.json() if response.status_code == 200 else None

        if request.method == 'POST' and atividade:
            data = {
                "titulo": request.form.get('titulo'),
                "descricao": request.form.get('descricao'),
                "configuracoes": {
                    "dificuldade": request.form.get('dificuldade'),
                    "tempo_estimado": int(request.form.get('tempo_estimado'))
                }
            }
            response = requests.put(f"{get_base_url()}/api/atividades/{atividade_id}", json=data)
            if response.status_code == 200:
                observable.notify_observers("Edição de Atividade", f"Atividade editada: {data['titulo']}")
                return redirect(url_for('instrutor_dashboard'))
        return render_template('editar_atividade.html', atividade=atividade, usuario_nome=session.get('user_nome'))

    # Excluir Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/excluir', methods=['POST'])
    def excluir_atividade(atividade_id):
        response = requests.delete(f"{get_base_url()}/api/atividades/{atividade_id}")
        if response.status_code == 200:
            observable.notify_observers("Exclusão de Atividade", f"Atividade ID {atividade_id} excluída.")
        return redirect(url_for('instrutor_dashboard'))

    # Associar Atividade a Aluno
    @app.route('/instrutor/atividades/<int:atividade_id>/associar', methods=['GET', 'POST'])
    def associar_atividade(atividade_id):
        # Buscar a atividade para exibir no template
        response_atividade = requests.get(f"{get_base_url()}/api/atividades/{atividade_id}")
        atividade = response_atividade.json() if response_atividade.status_code == 200 else None

        # Buscar alunos disponíveis para associar
        response_alunos = requests.get(f"{get_base_url()}/api/usuarios/tipo/aluno")
        alunos = response_alunos.json() if response_alunos.status_code == 200 else []

        if request.method == 'POST' and atividade:
            aluno_id = request.form.get('aluno_id')
            data = {
                "atividade_id": atividade_id,
                "aluno_id": int(aluno_id),
                "progresso": 0.0,
                "finalizado": False
            }
            response = requests.post(f"{get_base_url()}/api/analytics/registrar", json=data)
            if response.status_code == 201:
                observable.notify_observers(
                    "Associação de Atividade",
                    f"Atividade {atividade_id} associada ao aluno {aluno_id}"
                )
                return redirect(url_for('instrutor_dashboard'))

        return render_template(
            'associar_atividade.html',
            atividade=atividade,
            alunos=alunos,
            usuario_nome=session.get('user_nome')
        )

    # Analytics de Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/analytics', methods=['GET'])
    def analytics_atividade(atividade_id):
        response = requests.get(f"{get_base_url()}/api/analytics/atividade/{atividade_id}")
        analytics = response.json() if response.status_code == 200 else []
        return render_template('analytics_atividade.html', analytics=analytics, usuario_nome=session.get('user_nome'))

    # Atualizar progresso de uma atividade
    @app.route('/aluno/atividade/<int:atividade_id>/atualizar_progresso', methods=['POST'])
    def atualizar_progresso(atividade_id):
        if 'user_id' not in session or session.get('user_tipo') != 'aluno':
            return redirect(url_for('login'))

        data = {
            "atividade_id": atividade_id,
            "aluno_id": session['user_id'],
            "progresso": request.json.get('progresso', 0.0)
        }
        response = requests.post(f"{get_base_url()}/api/analytics/registrar", json=data)
        if response.status_code == 201:
            observable.notify_observers(
                "Atualização de Progresso",
                f"Aluno {session.get('user_nome')} atualizou o progresso da atividade {atividade_id}."
            )
        return jsonify({"message": "Progresso atualizado com sucesso"}), 200

    # Concluir uma atividade
    @app.route('/aluno/atividade/<int:atividade_id>/concluir', methods=['POST'])
    def concluir_atividade(atividade_id):
        if 'user_id' not in session or session.get('user_tipo') != 'aluno':
            return redirect(url_for('login'))

        data = {
            "atividade_id": atividade_id,
            "aluno_id": session['user_id'],
            "progresso": 100.0,
            "finalizado": True
        }
        response = requests.post(f"{get_base_url()}/api/analytics/registrar", json=data)
        if response.status_code == 201:
            observable.notify_observers(
                "Conclusão de Atividade",
                f"Aluno {session.get('user_nome')} concluiu a atividade {atividade_id}."
            )
        return jsonify({"message": "Atividade concluída com sucesso"}), 200

    @app.route('/instrutor/analytics/listar', methods=['GET'])
    def listar_analytics():
        response = requests.get(f"{get_base_url()}/api/analytics/listar")
        analytics = response.json() if response.status_code == 200 else []
        return render_template('listar_analytics.html', analytics=analytics, usuario_nome=session.get('user_nome'))

    @app.route('/aluno/dashboard', methods=['GET'])
    def aluno_dashboard():
        if 'user_id' not in session or session.get('user_tipo') != 'aluno':
            return redirect(url_for('login'))

        response = requests.get(f"{get_base_url()}/api/atividades/aluno/{session['user_id']}")
        atividades = response.json() if response.status_code == 200 else []

        return render_template('dashboard_aluno.html', atividades=atividades, usuario_nome=session.get('user_nome'))
