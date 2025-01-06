from app.models import Usuario, Atividade, Analytics, db
from app import observable

class UsuarioAdapter:
    @staticmethod
    def criar_usuario(nome, email, senha, tipo):
        usuario = Usuario(nome=nome, email=email, senha=senha, tipo=tipo)
        db.session.add(usuario)
        db.session.commit()
        observable.notify_observers("Criação de Usuário", f"Usuário {nome} ({email}) criado com sucesso.")
        return usuario

    @staticmethod
    def buscar_usuario_por_email(email):
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        return Usuario.query.get(usuario_id)

    @staticmethod
    def listar_alunos():
        return Usuario.query.filter_by(tipo='aluno').all()

    @staticmethod
    def buscar_usuarios_por_tipo(tipo):
        return Usuario.query.filter_by(tipo=tipo).all()

class AtividadeAdapter:
    @staticmethod
    def criar_atividade(titulo, descricao, configuracoes, criado_por):
        atividade = Atividade(titulo=titulo, descricao=descricao, configuracoes=configuracoes, criado_por=criado_por)
        db.session.add(atividade)
        db.session.commit()
        observable.notify_observers("Criação de Atividade", f"Atividade '{titulo}' criada pelo usuário {criado_por}.")
        return atividade

    @staticmethod
    def listar_atividades():
        return Atividade.query.all()

    @staticmethod
    def buscar_atividade_por_id(atividade_id):
        return Atividade.query.get(atividade_id)

class AnalyticsAdapter:
    @staticmethod
    def registrar_analytics(atividade_id, aluno_id, progresso, finalizado):
        """Registra ou atualiza os dados analíticos de um aluno em uma atividade."""
        analytics = Analytics.query.filter_by(atividade_id=atividade_id, aluno_id=aluno_id).first()
        if not analytics:
            analytics = Analytics(atividade_id=atividade_id, aluno_id=aluno_id, progresso=progresso, finalizado=finalizado)
            db.session.add(analytics)
        else:
            analytics.progresso = progresso
            analytics.finalizado = finalizado
        db.session.commit()
        return analytics

    @staticmethod
    def buscar_analytics_por_atividade(atividade_id):
        """Retorna os dados analíticos de todos os alunos para uma atividade específica."""
        from app.models import Analytics
        return Analytics.query.filter_by(atividade_id=atividade_id).all()

    @staticmethod
    def buscar_analytics_por_aluno(aluno_id):
        from app.models import Analytics  # Certifique-se de importar o modelo correto
        return Analytics.query.filter_by(aluno_id=aluno_id).all()

    @staticmethod
    def listar_analytics():
        """Lista todos os dados analíticos disponíveis."""
        return Analytics.query.all()

    @staticmethod
    def listar_todos():
        from app.models import Analytics  # Certifique-se de importar o modelo correto
        return Analytics.query.all()