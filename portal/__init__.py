import functools
from flask import Flask, render_template, session, request, redirect, url_for, g, flash
from werkzeug.security import check_password_hash, generate_password_hash

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DB_NAME='portal',
        DB_USER='portal_user',
        UPLOAD_FOLDER='portal/uploads/',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import courses
    app.register_blueprint(courses.bp)
    from . import sessions
    app.register_blueprint(sessions.bp)
    from . import assignments
    app.register_blueprint(assignments.bp)


    from . import db
    db.init_app(app)

    @app.route('/', methods=["GET", "POST"])
    def index():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            error = None

            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute(
                        'SELECT * FROM users WHERE email = %s', (email,)
                    )
                    user = cur.fetchone()


            if user is None:
                error = 'Incorrect email.'

            elif not check_password_hash(user[2], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['id'] = user[0]
                g.user = user

            flash(error)

        return render_template('index.html')


    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))


    @app.before_request
    def load_logged_in_user():
        user_id = session.get('id')

        if user_id is None:
            g.user = None
        else:
            with db.get_db() as con:
                with con.cursor() as cur:
                    cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                    g.user = cur.fetchone()

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template('errors/unauthorized.html'), 401

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/not_found.html'), 404

    return app

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view
