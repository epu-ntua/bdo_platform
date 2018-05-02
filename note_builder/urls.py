from django.conf.urls import url
from note_builder.views import CkEditorFormView

urlpatterns = [
    url('createCkeditor/', CkEditorFormView.as_view(), name='create-editor'),

]
