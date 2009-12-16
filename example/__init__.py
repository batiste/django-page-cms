from example.views import blog
from pages.views_registry import register_view

register_view('Blog', blog)