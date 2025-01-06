from flask import Blueprint, request, jsonify
from app.adapters import UsuarioAdapter, AtividadeAdapter, AnalyticsAdapter
from app import observable

# Blueprint para Activity Provider
activity_provider = Blueprint('activity_provider', __name__)

# Serviço para buscar usuário por email
@activity_provider.route('/usuarios/email/<string:email>', methods=['GET'])
def buscar_usuario_por_email(email):
    usuario = UsuarioAdapter.buscar_usuario_por_email(email)
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify({
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "senha": usuario.senha,  # Enviar senha pode ser um risco; ajuste conforme necessário.
        "tipo": usuario.tipo
    }), 200

# Serviço 1: Criar usuário
@activity_provider.route('/usuarios/criar', methods=['POST'])
def criar_usuario():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    tipo = data.get('tipo')

    if not all([nome, email, senha, tipo]):
        return jsonify({"error": "Dados incompletos"}), 400

    usuario = UsuarioAdapter.criar_usuario(nome, email, senha, tipo)
    return jsonify({"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "tipo": usuario.tipo}), 201


# Serviço 2: Criar atividade
@activity_provider.route('/atividades/criar', methods=['POST'])
def criar_atividade():
    data = request.json
    titulo = data.get('titulo')
    descricao = data.get('descricao')
    configuracoes = data.get('configuracoes')
    criado_por = data.get('criado_por')

    if not all([titulo, descricao, configuracoes, criado_por]):
        return jsonify({"error": "Dados incompletos"}), 400

    atividade = AtividadeAdapter.criar_atividade(titulo, descricao, configuracoes, criado_por)
    return jsonify({"id": atividade.id, "titulo": atividade.titulo, "descricao": atividade.descricao}), 201


# Serviço 3: Listar atividades
@activity_provider.route('/atividades/listar', methods=['GET'])
def listar_atividades():
    atividades = AtividadeAdapter.listar_atividades()
    return jsonify([{
        "id": a.id,
        "titulo": a.titulo,
        "descricao": a.descricao,
        "configuracoes": a.configuracoes  # Certifique-se de que 'configuracoes' é um campo no modelo
    } for a in atividades]), 200


# Serviço 4: Registrar progresso (analytics)
@activity_provider.route('/analytics/registrar', methods=['POST'])
def registrar_analytics():
    data = request.json
    atividade_id = data.get('atividade_id')
    aluno_id = data.get('aluno_id')
    progresso = data.get('progresso', 0.0)
    finalizado = data.get('finalizado', False)

    if not all([atividade_id, aluno_id]):
        return jsonify({"error": "Dados incompletos"}), 400

    analytics = AnalyticsAdapter.registrar_analytics(atividade_id, aluno_id, progresso, finalizado)
    return jsonify({"id": analytics.id, "progresso": analytics.progresso, "finalizado": analytics.finalizado}), 201


# Serviço 5: Consultar analytics por atividade
@activity_provider.route('/analytics/atividade/<int:atividade_id>', methods=['GET'])
def consultar_analytics_por_atividade(atividade_id):
    analytics = AnalyticsAdapter.buscar_analytics_por_atividade(atividade_id)
    return jsonify([
        {
            "id": a.id,
            "aluno_id": a.aluno_id,
            "aluno_nome": a.aluno.nome,  # Usando a relação para obter o nome do aluno
            "progresso": a.progresso,
            "finalizado": a.finalizado
        }
        for a in analytics
    ]), 200



# Serviço 6: Consultar analytics por aluno
@activity_provider.route('/analytics/aluno/<int:aluno_id>', methods=['GET'])
def consultar_analytics_por_aluno(aluno_id):
    analytics = AnalyticsAdapter.buscar_analytics_por_aluno(aluno_id)
    return jsonify(
        [{"id": a.id, "atividade_id": a.atividade_id, "progresso": a.progresso, "finalizado": a.finalizado} for a in
         analytics]), 200


# Observer para logging
@activity_provider.route('/log/evento', methods=['POST'])
def log_evento():
    data = request.json
    evento = data.get('evento')
    detalhes = data.get('detalhes')

    if not all([evento, detalhes]):
        return jsonify({"error": "Dados incompletos"}), 400

    observable.notify_observers(evento, detalhes)
    return jsonify({"message": "Evento registrado com sucesso"}), 200

# Serviço para buscar atividade por ID
@activity_provider.route('/atividades/<int:atividade_id>', methods=['GET'])
def buscar_atividade_por_id(atividade_id):
    atividade = AtividadeAdapter.buscar_atividade_por_id(atividade_id)
    if not atividade:
        return jsonify({"error": "Atividade não encontrada"}), 404
    return jsonify({
        "id": atividade.id,
        "titulo": atividade.titulo,
        "descricao": atividade.descricao,
        "configuracoes": atividade.configuracoes  # Ajuste se necessário
    }), 200

# Serviço para buscar usuários por tipo
@activity_provider.route('/usuarios/tipo/<string:tipo>', methods=['GET'])
def buscar_usuarios_por_tipo(tipo):
    usuarios = UsuarioAdapter.buscar_usuarios_por_tipo(tipo)
    if not usuarios:
        return jsonify([]), 200
    return jsonify([{
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "tipo": u.tipo
    } for u in usuarios]), 200

@activity_provider.route('/analytics/listar', methods=['GET'])
def listar_analytics():
    from app.adapters import AnalyticsAdapter  # Certifique-se de que o adapter correto está importado
    analytics = AnalyticsAdapter.listar_todos()
    if not analytics:
        return jsonify([]), 200
    return jsonify([{
        "id": a.id,
        "atividade_id": a.atividade_id,
        "aluno_id": a.aluno_id,
        "progresso": a.progresso,
        "finalizado": a.finalizado
    } for a in analytics]), 200

@activity_provider.route('/atividades/aluno/<int:aluno_id>', methods=['GET'])
def listar_atividades_por_aluno(aluno_id):
    from app.adapters import AnalyticsAdapter  # Certifique-se de que o adapter correto está importado
    analytics = AnalyticsAdapter.buscar_analytics_por_aluno(aluno_id)

    if not analytics:
        return jsonify([]), 200

    return jsonify([{
        "atividade_id": a.atividade_id,
        "titulo": a.atividade.titulo,
        "descricao": a.atividade.descricao,
        "progresso": a.progresso,
        "finalizado": a.finalizado
    } for a in analytics]), 200
