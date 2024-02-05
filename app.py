from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required,logout_user
from flask_security import roles_required, roles_accepted
from flask_mail import Mail
from flask_migrate import Migrate, upgrade

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/flaskS2'
app.config['SECRET_KEY'] = 'supersecret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'supersecretsalt'
app.config['MAIL_SERVER'] = '127.0.0.1'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'email@example.com'  # Byt ut mot din e-post
app.config['MAIL_PASSWORD'] = 'password'  # Byt ut mot ditt lösenord
app.config['MAIL_DEFAULT_SENDER'] = 'dittgmail@example.com'  # Byt ut mot din e-post
app.config['SECURITY_EMAIL_SENDER'] = '"MyApp"<norepyly@example.com>'  # Byt ut mot din e-post


db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(app)

# Definiera modeller för användare och roller
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Lägg till denna rad
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))

# Sätt upp Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Skapa en grundläggande vy
@app.route('/')
@login_required
def home():
    return 'Välkommen! Du är inloggad.<a href="/logout">Logga ut</a>'

@app.route('/public')
def public():
    return 'Detta är en offentlig sida.'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register2', methods=['GET', 'POST'])
def register2():
    if request.method == 'POST':
        email = request.form.get('email', None)
        password = request.form.get('password', "1234")
        role = request.form.get('role', 'user')
        # Antag att vi har formdata med användarnamn, e-post, lösenord etc.
        print(email, password, role)
        user_datastore.create_user(email=email, password=password, roles=[role])
        # user_datastore.create_user(email=email, password=password, roles=[User(roles=Role.query.where(Role.name==role).first())])
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('register2.html')

@app.route('/admin')
@roles_required('Admin')
def admin_page():
    return "Admin Page"

@app.route('/users')
@roles_accepted('Admin', 'User')
def user_pate():
    return render_template('users.html')


def create_user():
    db.create_all()
    if not Role.query.first():
        user_datastore.create_role(name='Admin')
        user_datastore.create_role(name='User')
    db.session.commit()
    if not User.query.first():
        user_datastore.create_user(email='test@example.com', password='password', roles=['Admin','User'])
        user_datastore.create_user(email='c@c.com', password='password', roles=['User'])
        user_datastore.create_user(email='d@d.com', password='password', roles=['Admin'])
        db.session.commit()
 

if __name__ == '__main__':
    with app.app_context():
        upgrade()
        create_user()   
    app.run(debug=True)
