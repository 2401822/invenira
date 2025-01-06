from app import db, SingletonApp

def initialize_db():
    app = SingletonApp.get_instance()
    with app.app_context():
        db.create_all()
        print("Banco inicializado com sucesso!")

if __name__ == "__main__":
    initialize_db()
