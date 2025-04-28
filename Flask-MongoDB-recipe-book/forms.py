from wtforms import Form, TextAreaField, HiddenField, StringField, PasswordField, validators, FieldList


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class RecipeForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    introduction = TextAreaField('Introduction')
    method = FieldList(TextAreaField('Method', [validators.required()]), min_entries=1)
    ingredients = FieldList(StringField('Ingredient', [validators.required()]), min_entries=1)
    categories = FieldList(HiddenField('Categories'), validators=[validators.DataRequired()], min_entries=1)
    cuisines = FieldList(HiddenField('Cuisines'), validators=[validators.DataRequired()], min_entries=1)
    allergens = FieldList(HiddenField('Allergens'), validators=[validators.DataRequired()], min_entries=1)
