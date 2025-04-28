from flask import Flask, session, request, render_template, redirect, url_for, flash, Response, jsonify
from flask_pymongo import PyMongo
from passlib.hash import sha256_crypt
from datetime import datetime
from bson.objectid import ObjectId
from functools import wraps
from dotenv import load_dotenv
import json
import os
from models.AuthorModel import AuthorModel
from models.RecipeModel import RecipeModel
from forms import RegistrationForm, LoginForm, RecipeForm
from webpackManifest import WebpackManifest

load_dotenv()

app = Flask(__name__)
if os.getenv('ENVIRONMENT', 'development'):
    app.secret_key = os.getenv('SECRET_KEY')
    app.config["MONGO_URI"] = os.getenv('MONGO_URI')
else:
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config["MONGO_URI"] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

manifest_params = {
    'static_folder': '/static',
    'manifest_path': './static/manifest.json'
}

manifest = WebpackManifest(app, manifest_params)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not AuthorModel.is_logged():
            flash('You need to login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


def returns_json(f):
    """
    Decorator returns json content-type in the header used for API endpoint
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json; charset=utf-8')

    return decorated_function


@app.template_filter()
def capitalize(text):
    """Convert a string to capitalize"""
    return text[0].upper() + text[1:] if len(text) > 0 else ''


@app.template_filter()
def truncate_text(text):
    return text[:120] + '...' if len(text) >= 120 else text


@app.context_processor
def template_functions():
    """ Inject global data to templates """
    def string_limit(text, limit):
        short_text = text.split(' ')[:limit]
        str = '...' if len(short_text) >= limit else ''
        return ' '.join(short_text) + str

    def pagination_url(link_type, attr, page_no, order, total_pages=None):
        paginate = page_no

        if link_type == 'prev':
            if page_no <= 1:
                return '#'
            paginate -= 1
        elif link_type == 'next':
            if total_pages <= page_no:
                return '#'
            paginate += 1

        if attr['name'] == 'author':
            if 'liked' in attr:
                return url_for('index', page_no=paginate, order_by=order, author_name=attr['author'],
                               author_types='liked')
            return url_for('index', page_no=paginate, order_by=order, author_name=attr['author'])
        elif attr['name'] == 'tag':
            return url_for('index', page_no=paginate, order_by=order,
                           tag_name=attr['tag']['name'], tag_value=attr['tag']['value'])

        return url_for('index', page_no=paginate, order_by=order)

    def recipe_vote_class(recipe):
        if 'user' not in session:
            return ''

        if session['user']['username'] == recipe['author']:
            return 'disabled'

        if 'liked_by' in recipe and \
                recipe['liked_by'] is not None and \
                session['user']['username'] in recipe['liked_by']:
            return 'voted'
        return ''

    return dict(string_limit=string_limit,
                pagination_url=pagination_url,
                recipe_vote_class=recipe_vote_class,
                user=author_model.logged_as())


"""
Initialize models
"""
author_model = AuthorModel(mongo)
recipe_model = RecipeModel(mongo)


@app.route('/author/<author_name>/show/<author_types>/page/<page_no>')
@app.route('/author/<author_name>/show/<author_types>/page/<page_no>/order-by/<order_by>')
@app.route('/author/<author_name>/show/<author_types>/order-by/<order_by>')
@app.route('/author/<author_name>/show/<author_types>')
@app.route('/author/<author_name>/page/<page_no>')
@app.route('/author/<author_name>/page/<page_no>/order-by/<order_by>')
@app.route('/author/<author_name>/order-by/<order_by>')
@app.route('/author/<author_name>')
@app.route('/tag/<tag_name>/<tag_value>/page/<page_no>')
@app.route('/tag/<tag_name>/<tag_value>/page/<page_no>/order-by/<order_by>')
@app.route('/tag/<tag_name>/<tag_value>/order-by/<order_by>')
@app.route('/tag/<tag_name>/<tag_value>/')
@app.route('/page/<page_no>')
@app.route('/page/<page_no>/order-by/<order_by>')
@app.route('/order-by/<order_by>')
@app.route('/')
def index(page_no=None, order_by=None, author_name=None, tag_name=None, tag_value=None, author_types=None):
    if not page_no:
        page_no = 1
    else:
        page_no = int(page_no)
        # check if page_no is greater than 0
        page_no = page_no if page_no > 0 else 1

    if not order_by:
        order_by = 'created'

    query = {}
    page_attr = {
        'name': 'index',
        'link': ''
    }
    title = ''
    if author_name is not None:
        page_attr = {
            'name': 'author',
            'author': author_name,
            'link': '/author/' + author_name
        }
        query = {'author': author_name}

        title += capitalize(author_name) + '\'s '
        if 'user' in session and session['user']['username'] == author_name:
            title = 'Your '
            page_attr.update({
                'own_recipes': True
            })

        if author_types is not None:
            page_attr.update({
                'link': '/author/' + author_name + '/show/liked',
                'liked': True,
            })

            title += 'liked '

            query = {'liked_by': {'$in': [author_name]}}

    elif tag_name is not None and tag_value is not None:
        page_attr = {
            'name': 'tag',
            'tag': {
                'name': tag_name,
                'value': tag_value
            },
            'link': '/tag/' + tag_name + '/' + tag_value
        }
        query = {tag_name: {'$in': [tag_value]}}

        if tag_name == 'categories':
            title = 'Category '
        elif tag_name == 'cuisines':
            title = 'Cuisines '

        title += capitalize(tag_value)

    title += ' most' if title else 'Most'

    if order_by == 'views':
        title += ' popular recipes'
    elif order_by == 'likes':
        title += ' liked recipes'
    else:
        title += ' recent recipes'

    recipes = recipe_model.archive(query, page_no, order_by)
    return render_template('archive.html',
                           body_class='archive',
                           page_attr=page_attr,
                           recipes=list(recipes),
                           title=title,
                           page=page_no,
                           order_by=order_by,
                           pagination=recipe_model.archive_pagination(query))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global author_model
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():

        author = author_model.authenticate(request.form.to_dict())
        if author is not False:
            session['user'] = {
                'id': str(ObjectId(author['_id'])),
                'username': author['username']
            }
            flash('Successfully logged in', 'success')
            return redirect(url_for('index', author_name=author['username']))

        flash('Wrong username or password', 'error')
        return redirect(url_for('login'))

    if 'user' in session:
        session.pop('user', None)
    return render_template('login.html', form=form, body_class='login')


@app.route('/logout')
def logout():
    flash('Successfully logged out', 'success')
    return redirect('login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Method is used for register user
    :return: template register or redirect to login
    """
    global author_model
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        if author_model.get_by_username(username):
            flash(u'Username {} is already registered'.format(username), 'error')
            return redirect(url_for('register'))
        data = {
            'username': username.lower(),
            'password': sha256_crypt.encrypt(request.form.get('password')),
            'registered': datetime.now(),
        }
        author_model.register(data)
        flash(u'You have been registered', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title="Register", body_class='register')


@app.route('/recipe/add', methods=['GET', 'POST'])
@requires_auth
def new_recipe():
    form = RecipeForm(request.form)
    if request.method == 'POST' and form.validate():
        added_id = recipe_model.add(form, session['user']['username'])
        flash('Recipe has been added', 'success')
        return redirect(url_for('view_recipe', recipe_id=added_id))
    return render_template('recipe_edit.html',
                           form=form,
                           form_action=url_for('new_recipe'),
                           title='Add recipe',
                           body_class='edit_recipe')


@app.route('/recipe/edit/<recipe_id>', methods=['GET', 'POST'])
@requires_auth
def edit_recipe(recipe_id):
    if not ObjectId.is_valid(recipe_id):
        return render_template('recipe_error.html',
                               message="No recipe found",
                               message_class='warning',
                               btn_class='red darken-4')
    recipe = recipe_model.get_edit_data(ObjectId(recipe_id), session['user']['username'])
    if recipe is False:
        return render_template('recipe_error.html',
                               message="You can't edit someone recipe",
                               message_class='error',
                               btn_class='')
    init_form = RecipeForm(recipe, request.form)
    if request.method == 'POST' and init_form.validate():
        data = RecipeForm(request.form)
        recipe_model.update(data, ObjectId(recipe_id))
        flash('Recipe has been edited', 'success')
        return redirect(url_for('view_recipe', recipe_id=recipe_id))

    return render_template('recipe_edit.html',
                           form=init_form,
                           form_action=url_for('edit_recipe', recipe_id=recipe_id),
                           recipe_id=recipe_id,
                           title='Edit recipe',
                           body_class='edit_recipe')


@app.route('/recipe/delete/<recipe_id>')
@requires_auth
def delete_recipe(recipe_id):
    if not ObjectId.is_valid(recipe_id):
        return render_template('recipe_error.html',
                               message="No recipe found",
                               message_class='warning',
                               btn_class='red darken-4')

    if recipe_model.delete(ObjectId(recipe_id), session['user']['username']):
        flash('Recipe has been successfully deleted', 'success')
        return redirect(url_for('index', author_name=session['user']['username']))

    return render_template('recipe_error.html',
                           message="You can't delete someone recipe",
                           message_class='error',
                           btn_class='')


@app.route('/recipe/<recipe_id>')
def view_recipe(recipe_id):
    """
    session['recipe_views'] is used to avoid fake statistic with recipe views
    """
    if 'recipe_views' not in session:
        session['recipe_views'] = []

    if ObjectId.is_valid(recipe_id) and recipe_id not in session['recipe_views']:
        session['recipe_views'].append(recipe_id)
        recipe_model.update_view_counter(ObjectId(recipe_id))
        session.modified = True

    recipe = False
    related = []

    if ObjectId.is_valid(recipe_id):
        recipe = recipe_model.view(ObjectId(recipe_id))

        related_data = recipe['categories']
        related_type = 'categories'
        if len(recipe['categories']) < 1:
            related_data = recipe['cuisines']
            related_type = 'cuisines'

        related = recipe_model.related(ObjectId(recipe_id), related_data, related_type)

    return render_template('recipe_single.html',
                           body_class='single_recipe',
                           related=related,
                           recipe=recipe)


@app.route('/api/recipe-vote', methods=['POST'])
@returns_json
def recipe_vote():
    if 'user' not in session:
        return json.dumps({
            'status': 'error',
            'message': 'You need to login to vote for the recipe'
        })

    try:
        recipe_id = ObjectId(request.form['id'])
        total_votes = recipe_model.vote(recipe_id, session['user']['username'])

        if isinstance(total_votes, int) and total_votes is not False:
            return json.dumps({
                'status': 'success',
                'votes': total_votes
            })
    except Exception as error:
        print(error)

    return json.dumps({
        'status': 'error',
        'message': 'An error occurred. Please try again'
    })


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=os.environ.get('PORT'), debug=False)
