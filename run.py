from app import SingletonApp

# Obter a instância única da aplicação
app = SingletonApp.get_instance()

if __name__ == '__main__':
    # Executar o servidor Flask
    app.run(debug=True, host='127.0.0.1', port=5000)
