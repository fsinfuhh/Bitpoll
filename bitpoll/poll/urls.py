from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^([a-zA-Z0-9_\-]+)/$', views.poll, name='poll'),
    url(r'^([a-zA-Z0-9_\-]+).csv$', views.poll, {'export': True}, name='poll_export_csv'),
    url(r'^([a-zA-Z0-9_\-]+)/comment/$', views.comment, name='poll_comment'),
    url(r'^([a-zA-Z0-9_\-]+)/comment/(\d+)/edit/$', views.comment, name='poll_comment_edit'),
    url(r'^([a-zA-Z0-9_\-]+)/comment/(\d+)/delete/$', views.delete_comment, name='poll_deleteComment'),
    url(r'^([a-zA-Z0-9_\-]+)/watch/$', views.watch, name='poll_watch'),
    url(r'^([a-zA-Z0-9_\-]+)/settings/$', views.settings, name='poll_settings'),

    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/$', views.edit_choice, name='poll_editChoice'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/date/$', views.edit_date_choice, name='poll_editDateChoice'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/date/$', views.edit_dt_choice_date, name='poll_editDTChoiceDate'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/time/$', views.edit_dt_choice_time, name='poll_editDTChoiceTime'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/combinations/$', views.edit_dt_choice_combinations,
        name='poll_editDTChoiceCombinations'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choices/universal/$', views.edit_universal_choice, name='poll_editUniversalChoice'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choicevalues/', views.edit_choicevalues, name='poll_editchoicevalues'),
    url(r'^([a-zA-Z0-9_\-]+)/edit/choicevalues_create', views.edit_choicevalues_create,
        name='poll_editchoicevalues_create'),

    url(r'^([a-zA-Z0-9_\-]+)/delete/$', views.delete, name='poll_delete'),

    url(r'^([a-zA-Z0-9_\-]+)/vote/$', views.vote, name='poll_vote'),
    url(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/assign/$', views.vote_assign, name='poll_voteAssign'),
    url(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/edit/$', views.vote, name='poll_voteEdit'),
    url(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/delete/$', views.vote_delete, name='poll_voteDelete'),

    url(r'^([a-zA-Z0-9_\-]+)/copy/$', views.copy, name='poll_copy'),
]
