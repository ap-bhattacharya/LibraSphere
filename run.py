from app import create_app
from flask import redirect

app = create_app()

# Add a root route to redirect to the login page
@app.route('/')
def root():
    return redirect('/auth/login')

if __name__ == '__main__':
    app.run(debug=True)
