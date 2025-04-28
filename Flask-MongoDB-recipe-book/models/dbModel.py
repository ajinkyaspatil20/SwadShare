from bson.objectid import ObjectId


class DbModel:
    Mongo = None
    TableName = None

    def __init__(self, mongo, table_name):
        self.Mongo = mongo

        self.TableName = table_name
        self.db = mongo.db[table_name]

    def delete_by_id(self, table_id: ObjectId):
        return self.db.remove({'_id': table_id})

    def get_one_by_id(self, table_id: ObjectId):
        return self.db.find_one({'_id': table_id})

    def get_one_by_attr(self, attr_name: str, attr_value: str):
        return self.db.find_one({attr_name: attr_value})

    def get_all(self):
        return self.db.find()

    def update_one(self, attr: dict):
        key_name = attr['name']
        value = attr['value']
        data = attr['data']

        return self.db.update_one(
            {key_name: value},
            {'$set': data}
        )

    def update_counter(self, counter_name: str, updated_value: int, id: ObjectId):
        self.db.update_one(
            {'_id': id},
            {'$set': {
                counter_name: updated_value
            }}
        )
