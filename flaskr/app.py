from flaskr import create_app  
import os

# Crear la aplicación
app = create_app()

# Inicializar la app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
