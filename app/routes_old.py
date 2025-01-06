from flask import request, jsonify, render_template, redirect, url_for, session
from app.adapters import UsuarioAdapter, AtividadeAdapter, AnalyticsAdapter
from app import observable


def register_routes(app):
    # Página inicial
    @app.route('/')
    def index():
        if 'user_id' in session:
            usuario = UsuarioAdapter.buscar_usuario_por_id(session['user_id'])
            if usuario.tipo == 'instrutor':
                return redirect(url_for('instrutor_dashboard'))
            elif usuario.tipo == 'aluno':
                return redirect(url_for('aluno_dashboard'))
        return redirect(url_for('login'))

    # Página de login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.json
            email = data.get('email')
            senha = data.get('senha')

            usuario = UsuarioAdapter.buscar_usuario_por_email(email)
            if usuario and usuario.senha == senha:
                session['user_id'] = usuario.id
                session['user_nome'] = usuario.nome
                session['user_tipo'] = usuario.tipo

                observable.notify_observers("Login", f"Usuário {usuario.nome} fez login.")
                if usuario.tipo == 'instrutor':
                    return jsonify({"message": "Login realizado com sucesso!", "tipo": "instrutor"}), 200
                elif usuario.tipo == 'aluno':
                    return jsonify({"message": "Login realizado com sucesso!", "tipo": "aluno"}), 200
            return jsonify({"message": "Credenciais inválidas"}), 401

        return render_template('login.html')

    # Página de registro
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            data = request.json
            nome = data.get('nome')
            email = data.get('email')
            senha = data.get('senha')
            tipo = data.get('tipo')  # 'instrutor' ou 'aluno'

            if not all([nome, email, senha, tipo]):
                return jsonify({"message": "Dados incompletos"}), 400

            UsuarioAdapter.criar_usuario(nome, email, senha, tipo)
            observable.notify_observers("Registro", f"Novo usuário registrado: {nome}, Tipo: {tipo}.")
            return jsonify({"message": "Usuário registrado com sucesso"}), 201

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
        atividades = AtividadeAdapter.listar_atividades()
        return render_template('dashboard_instrutor.html', atividades=atividades, usuario_nome=session.get('user_nome'))

    # Criar Atividade
    @app.route('/instrutor/atividades/criar', methods=['GET', 'POST'])
    def criar_atividade():
        if request.method == 'POST':
            data = request.form
            titulo = data.get('titulo')
            descricao = data.get('descricao')
            configuracoes = {
                "dificuldade": data.get('dificuldade'),
                "tempo_estimado": int(data.get('tempo_estimado'))
            }
            atividade = AtividadeAdapter.criar_atividade(titulo, descricao, configuracoes, criado_por=session['user_id'])
            observable.notify_observers("Criação de Atividade", f"Atividade criada: {atividade.titulo}")
            return redirect(url_for('instrutor_dashboard'))
        return render_template('criar_atividade.html', usuario_nome=session.get('user_nome'))

    # Editar Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/editar', methods=['GET', 'POST'])
    def editar_atividade(atividade_id):
        atividade = AtividadeAdapter.buscar_atividade_por_id(atividade_id)
        if request.method == 'POST':
            data = request.form
            atividade.titulo = data.get('titulo')
            atividade.descricao = data.get('descricao')
            atividade.configuracoes = {
                "dificuldade": data.get('dificuldade'),
                "tempo_estimado": int(data.get('tempo_estimado'))
            }
            AtividadeAdapter.salvar_atividade(atividade)
            observable.notify_observers("Edição de Atividade", f"Atividade editada: {atividade.titulo}")
            return redirect(url_for('instrutor_dashboard'))
        return render_template('editar_atividade.html', atividade=atividade, usuario_nome=session.get('user_nome'))

    # Excluir Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/excluir', methods=['POST'])
    def excluir_atividade(atividade_id):
        atividade = AtividadeAdapter.excluir_atividade(atividade_id)
        observable.notify_observers("Exclusão de Atividade", f"Atividade excluída: {atividade.titulo if atividade else 'ID inválido'}")
        return redirect(url_for('instrutor_dashboard'))

    # Associar Atividade a Aluno
    @app.route('/instrutor/atividades/<int:atividade_id>/associar', methods=['GET', 'POST'])
    def associar_atividade(atividade_id):
        atividade = AtividadeAdapter.buscar_atividade_por_id(atividade_id)
        alunos = UsuarioAdapter.listar_alunos()

        if request.method == 'POST':
            aluno_id = request.form.get('aluno_id')
            if aluno_id:
                AnalyticsAdapter.registrar_analytics(atividade_id, int(aluno_id), progresso=0.0, finalizado=False)
                observable.notify_observers("Associação de Atividade", f"Atividade {atividade.titulo} associada ao aluno {aluno_id}")
                return redirect(url_for('instrutor_dashboard'))

        return render_template('associar_atividade.html', atividade=atividade, alunos=alunos, usuario_nome=session.get('user_nome'))

    # Analytics de Atividade
    @app.route('/instrutor/atividades/<int:atividade_id>/analytics', methods=['GET'])
    def analytics_atividade(atividade_id):
        analytics = AnalyticsAdapter.buscar_analytics_por_atividade(atividade_id)
        return render_template('analytics_atividade.html', analytics=analytics, usuario_nome=session.get('user_nome'))

    # Atualizar progresso de uma atividade
    @app.route('/aluno/atividade/<int:atividade_id>/atualizar_progresso', methods=['POST'])
    def atualizar_progresso(atividade_id):
        if 'user_id' not in session or session.get('user_tipo') != 'aluno':
            return redirect(url_for('login'))

        data = request.json
        progresso = data.get('progresso')

        if progresso is not None:
            AnalyticsAdapter.registrar_analytics(
                atividade_id=atividade_id,
                aluno_id=session['user_id'],
                progresso=float(progresso),
                finalizado=False
            )
            observable.notify_observers(
                "Atualização de Progresso",
                f"Aluno {session.get('user_nome')} atualizou o progresso da atividade {atividade_id} para {progresso}%."
            )
        return jsonify({"message": "Progresso atualizado com sucesso"}), 200

    # Concluir uma atividade
    @app.route('/aluno/atividade/<int:atividade_id>/concluir', methods=['POST'])
    def concluir_atividade(atividade_id):
        if 'user_id' not in session or session.get('user_tipo') != 'aluno':
            return redirect(url_for('login'))

        AnalyticsAdapter.registrar_analytics(
            atividade_id=atividade_id,
            aluno_id=session['user_id'],
            progresso=100.0,
            finalizado=True
        )
        observable.notify_observers(
            "Conclusão de Atividade",
            f"Aluno {session.get('user_nome')} concluiu a atividade {atividade_id}."
        )
        return jsonify({"message": "Atividade concluída com sucesso"}), 200

    # Dashboard do Aluno
    @app.route('/aluno/dashboard', methods=['GET'])
    def aluno_dashboard():
        analytics = AnalyticsAdapter.buscar_analytics_por_aluno(session['user_id'])
        return render_template('dashboard_aluno.html', analytics=analytics, usuario_nome=session.get('user_nome'))

    # Listar Analytics Disponíveis
    @app.route('/instrutor/analytics/listar', methods=['GET'])
    def listar_analytics_disponiveis():
        if 'user_id' not in session or session.get('user_tipo') != 'instrutor':
            return redirect(url_for('login'))

        analytics = AnalyticsAdapter.listar_analytics()
        observable.notify_observers("Listagem de Analytics", f"Instrutor {session.get('user_nome')} listou os analytics disponíveis.")
        return render_template('listar_analytics.html', analytics=analytics, usuario_nome=session.get('user_nome'))


    @app.route('/config', methods=['GET'])
    def config_url():
        return render_template('config.html')

    @app.route('/json_params', methods=['GET'])
    def json_params_url():
        return jsonify({"parameters": ["titulo", "descricao", "dificuldade", "tempo_estimado"]})

    @app.route('/deploy', methods=['GET'])
    def deploy_url():
        activity_id = request.args.get('activity_id')
        if not activity_id:
            return jsonify({"error": "ID da atividade não fornecido"}), 400
        deploy_url = url_for('atividade', atividade_id=activity_id, _external=True)
        return jsonify({"deploy_url": deploy_url})

    # Analytics de Atividade
    @app.route('/analytics', methods=['POST'])
    def analytics_url():
        data = request.json
        activity_id = data.get('activityID')
        if not activity_id:
            return jsonify({"error": "ID da atividade não fornecido"}), 400
        analytics = AnalyticsAdapter.listar_analytics()
        return jsonify([
            {
                "inveniraStdID": a.aluno_id,
                "quantAnalytics": [
                    {"name": "Progresso", "value": f"{a.progresso}%"}
                ],
                "qualAnalytics": [
                    {"Student activity profile": url_for('analytics_profile', aluno_id=a.aluno_id, _external=True)}
                ]
            }
            for a in analytics if a.atividade_id == int(activity_id)
        ])

# Rota de perfil de analytics (exemplo)
    @app.route('/analytics/<int:aluno_id>/profile', methods=['GET'])
    def analytics_profile(aluno_id):
        return jsonify({"profile": f"Perfil analítico do aluno {aluno_id}"})