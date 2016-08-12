oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    request_token_params=None,
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login/github/authorization')
def authorized():
    resp = github.authorized_response()

    if resp is None:
        return unauthorized('{}: {}'.format(
                request.args['error'], request.args['error_description']
            )
        )

    # format required to fetch user profile
    session['oauth_token'] = (resp['access_token'], '')
    me = github.get('user')
    username = session['username'] = me.data['login']
    session['avatar_url'] = me.data.get('avatar_url', '')
    session['oauth_provider'] = 'github'

    # create a user model if one does not exist
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()

    return redirect(url_for('index'))

@github.tokengetter
def get_github_oauth_token():
    return session.get('oauth_token')

@app.route('/')
def index():
    username = session.get('username', '')
    avatar_url = session.get('avatar_url', '')
    return render_template('index.html', username=username,
        avatar_url=app.confi['APP_AVA'],
        title=title,
        logo_url=app.config.get('APP_LOGO_URL',
            url_for('static', filename='images/logo.png')))
