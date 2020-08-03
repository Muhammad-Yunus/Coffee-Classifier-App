from . import AdminIndexView, expose

# Home views
class MyHomeView(AdminIndexView):

    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose('/')
    def index(self):
        return self.render('admin/home.html')