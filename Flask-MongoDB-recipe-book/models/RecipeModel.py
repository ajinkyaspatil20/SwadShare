from datetime import datetime
from models.dbModel import DbModel
import math
from werkzeug.datastructures import MultiDict


class RecipeModel(DbModel):
    TableName = 'recipes'
    RecipeNoArchive = 24

    def __init__(self, mongo):
        super().__init__(mongo, self.TableName)

    def add(self, data, author):
        recipe = {
            'title': data.title.data,
            'introduction': data.introduction.data,
            'method': data.method.data,
            'ingredients': data.ingredients.data,
            'allergens': self.list_to_lower(data.allergens.data),
            'categories': self.list_to_lower(data.categories.data),
            'cuisines': self.list_to_lower(data.cuisines.data),
            'author': author,
            'views': 0,
            'likes': 0,
            'edited': datetime.now(),
            'created': datetime.now()
        }

        id = self.db.insert_one(recipe)
        return id.inserted_id

    def update(self, data, recipe_id):
        recipe = {
            'title': data.title.data,
            'introduction': data.introduction.data,
            'method': data.method.data,
            'ingredients': data.ingredients.data,
            'allergens': self.list_to_lower(data.allergens.data),
            'categories': self.list_to_lower(data.categories.data),
            'cuisines': self.list_to_lower(data.cuisines.data),
            'edited': datetime.now()
        }
        attr = {
            'name': '_id',
            'value': recipe_id,
            'data': recipe
        }
        self.update_one(attr)

    def archive(self, query, page_no, order_by):
        page_no -= 1

        return self.db.find({'$query': query, '$orderby': {order_by: -1}}) \
            .skip(self.RecipeNoArchive * page_no) \
            .limit(self.RecipeNoArchive)

    def archive_pagination(self, query):
        return math.ceil(self.db.count_documents(query) / self.RecipeNoArchive)

    def view(self, recipe_id):
        return self.get_one_by_id(recipe_id)

    def update_view_counter(self, recipe_id):

        self.db.update_one(
            {'_id': recipe_id},
            {'$inc': {
                'views': +1,
            }}
        )

    def delete(self, recipe_id, username):
        recipe = self.get_one_by_id(recipe_id)
        if not recipe or recipe['author'] != username:
            return False

        self.delete_by_id(recipe_id)
        return True

    def get_edit_data(self, recipe_id, username):
        recipe = self.get_one_by_id(recipe_id)
        if not recipe:
            return False
        if recipe['author'] != username:
            return False

        editable_keys = [
            'title',
            'introduction',
            'method',
            'ingredients',
            'categories',
            'cuisines',
            'allergens'
        ]

        editable = []
        for key in recipe.keys():
            if key in editable_keys:
                if isinstance(recipe[key], list):
                    c = 0
                    for item in recipe[key]:
                        if item:
                            editable.append(('{}-{}'.format(key, c), item))
                            c += 1
                else:
                    editable.append((key, recipe[key]))
        return MultiDict(editable)

    def related(self, exclude, tags, tag_type):
        if len(tags) == 0:
            return []
        limit = 6
        related = []
        for category in tags:
            recipes = list(self.db.find(
                {'$query': {
                    tag_type: {'$in': [category]}},
                    '$orderby': {'views': -1}}).limit(limit))

            limit -= len(related)
            for recipe in recipes:
                if len(related) == 6:
                    return related
                if exclude != recipe['_id']:
                    related.append(recipe)
            return related

    def vote(self, recipe_id, username):
        recipe = self.get_one_by_id(recipe_id)
        if recipe and recipe['author'] != username:
            likes = int(recipe['likes'])
            if 'liked_by' in recipe and recipe['liked_by'] is not None:
                if username in recipe['liked_by']:
                    likes -= 1
                    liked_by = recipe['liked_by'].remove(username)
                else:
                    likes += 1
                    liked_by = recipe['liked_by'].append(username)

            else:
                likes += 1
                liked_by = [username]

            self.db.update_one(
                {'_id': recipe_id},
                {'$set': {
                    'likes': likes,
                    'liked_by': liked_by
                }}
            )

            return likes
        return False

    @staticmethod
    def list_to_lower(data):
        if len(data) == 1 and data[0] == '':
            return []
        return [x.lower() for x in data]
