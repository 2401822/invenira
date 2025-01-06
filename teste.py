from sqlalchemy import create_engine, MetaData, Table, select

# Configuração do banco de dados SQLite
DATABASE_URI = 'sqlite:///invenira.db'

# Criação da engine de conexão
engine = create_engine(DATABASE_URI)

# Função para listar todos os registros da tabela usuarios
def listar_usuarios():
    try:
        # Refletir a tabela existente
        metadata = MetaData()
        metadata.reflect(bind=engine)

        if 'usuarios' not in metadata.tables:
            print("A tabela 'usuarios' não foi encontrada no banco de dados.")
            return

        usuarios = metadata.tables['usuarios']

        # Realizar a consulta
        with engine.connect() as connection:
            result = connection.execute(select(usuarios))
            registros = result.fetchall()

            # Exibir os registros
            print("Registros encontrados na tabela 'usuarios':")
            for row in registros:
                print(dict(row))  # Converte cada linha em um dicionário para facilitar a leitura

    except Exception as e:
        print(f"Erro ao listar registros: {e}")

# Executar o programa
if __name__ == '__main__':
    listar_usuarios()
