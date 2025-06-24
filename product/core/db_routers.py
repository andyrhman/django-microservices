class OldDBRouter:
    route_app_labels = {'core'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return hints.get('using') or None
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'old_data':
            return False
        return None
    
class CategoryDBRouter:
    route_app_labels = {'category'}   # we’ll give your Category model app_label='category'

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'category_db'
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db != 'category_db'
