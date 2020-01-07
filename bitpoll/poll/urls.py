from django.conf.urls import url
from django.urls import include, path

from . import views

#app_name = 'poll'

urlpatterns = [
    path('<slug:poll_url>.csv', views.poll, {'export': True}, name='poll_export_csv'),
    path('<slug:poll_url>/', include([
        path('', views.poll, name='poll'),
        path('comment/', views.comment, name='poll_comment'),
        path('comment/<int:comment_id>/edit/', views.comment, name='poll_comment_edit'),
        path('comment/<int:comment_id>/delete/', views.delete_comment, name='poll_deleteComment'),

        path('watch/', views.watch, name='poll_watch'),
        path('settings/', views.settings, name='poll_settings'),

        path('edit/', include([
            path('choices/', views.edit_choice, name='poll_editChoice'),
            path('choices/date/', views.edit_date_choice, name='poll_editDateChoice'),
            path('choices/dateTime/date/', views.edit_dt_choice_date, name='poll_editDTChoiceDate'),
            path('choices/dateTime/time/', views.edit_dt_choice_time, name='poll_editDTChoiceTime'),
            path('choices/dateTime/combinations/', views.edit_dt_choice_combinations,
                name='poll_editDTChoiceCombinations'),
            path('choices/universal/', views.edit_universal_choice, name='poll_editUniversalChoice'),

            path('choicevalues/', views.edit_choicevalues, name='poll_editchoicevalues'),
            path('choicevalues_create/', views.edit_choicevalues_create,
                name='poll_editchoicevalues_create'),
        ])),
        path('delete/', views.delete, name='poll_delete'),

        path('vote/', views.vote, name='poll_vote'),
        path('vote/<int:vote_id>/', include([
            path('assign/', views.vote_assign, name='poll_voteAssign'),
            path('edit/', views.vote, name='poll_voteEdit'),
            path('delete/', views.vote_delete, name='poll_voteDelete'),
        ])),
        path('copy/', views.copy, name='poll_copy'),
    ])),

]
