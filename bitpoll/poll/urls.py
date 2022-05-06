from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^([a-zA-Z0-9_\-]+)/$', views.poll, name='poll'),
    re_path(r'^([a-zA-Z0-9_\-]+).csv$', views.poll, {'export': True}, name='poll_export_csv'),
    re_path(r'^([a-zA-Z0-9_\-]+)/comment/$', views.comment, name='poll_comment'),
    re_path(r'^([a-zA-Z0-9_\-]+)/comment/(\d+)/edit/$', views.comment, name='poll_comment_edit'),
    re_path(r'^([a-zA-Z0-9_\-]+)/comment/(\d+)/delete/$', views.delete_comment, name='poll_deleteComment'),
    re_path(r'^([a-zA-Z0-9_\-]+)/watch/$', views.watch, name='poll_watch'),
    re_path(r'^([a-zA-Z0-9_\-]+)/settings/$', views.settings, name='poll_settings'),

    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/$', views.edit_choice, name='poll_editChoice'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/date/$', views.edit_date_choice, name='poll_editDateChoice'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/date/$', views.edit_dt_choice_date, name='poll_editDTChoiceDate'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/time/$', views.edit_dt_choice_time, name='poll_editDTChoiceTime'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/dateTime/combinations/$', views.edit_dt_choice_combinations,
        name='poll_editDTChoiceCombinations'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choices/universal/$', views.edit_universal_choice, name='poll_editUniversalChoice'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choicevalues/', views.edit_choicevalues, name='poll_editchoicevalues'),
    re_path(r'^([a-zA-Z0-9_\-]+)/edit/choicevalues_create', views.edit_choicevalues_create,
        name='poll_editchoicevalues_create'),

    re_path(r'^([a-zA-Z0-9_\-]+)/delete/$', views.delete, name='poll_delete'),

    re_path(r'^([a-zA-Z0-9_\-]+)/vote/$', views.vote, name='poll_vote'),
    re_path(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/assign/$', views.vote_assign, name='poll_voteAssign'),
    re_path(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/edit/$', views.vote, name='poll_voteEdit'),
    re_path(r'^([a-zA-Z0-9_\-]+)/vote/(\d+)/delete/$', views.vote_delete, name='poll_voteDelete'),

    re_path(r'^([a-zA-Z0-9_\-]+)/copy/$', views.copy, name='poll_copy'),
]
