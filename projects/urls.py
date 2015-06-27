from django.conf.urls import patterns, include, url
from projects.views import dummy_view, dummy_story_view, dummy_translation_view, dummy_plan_view
from projects import views


urlpatterns = patterns('',
    url(r'^$', views.api_root),

    url(r'^projects/$',                                                 views.ProjectList.as_view(), name='project_list'),
    url(r'^projects/(?P<pk>[0-9]+)/$',                                  views.ProjectDetail.as_view()),

    url(r'^project/create/$',                                           dummy_view, name='project_create'),
    url(r'^project/list/$',                                             dummy_view, name='project_list_old'),
    url(r'^project/(?P<id>.+)/$',                                       dummy_view, name='project_get'),
    url(r'^project/(?P<id>.+)/alter/$',                                 dummy_view, name='project_alter'),
    url(r'^project/(?P<id>.+)/delete/$',                                dummy_view, name='project_delete'),
    url(r'^project/(?P<id>.+)/add_users/$',                             dummy_view, name='project_add_users'),
    url(r'^project/(?P<id>.+)/remove_users/$',                          dummy_view, name='project_remove_users'),
    url(r'^project/(?P<id>.+)/list_users/$',                            dummy_view, name='project_list_users'),

    url(r'^project/(?P<id>\d+)/plan/create/$',                          dummy_plan_view, name='project_plan_create'),
    url(r'^project/(?P<id>\d+)/plan/list/$',                          dummy_plan_view, name='project_plan_list'),
    url(r'^project/plan/(?P<id>\d+)/$',                                 dummy_plan_view, name='project_plan_get'),
    url(r'^project/plan/(?P<id>\d+)/alter/$',                          dummy_plan_view, name='project_plan_alter'),
    url(r'^project/plan/(?P<id>\d+)/delete/$',                          dummy_plan_view, name='project_plan_delete'),

    url(r'^story/create/$',                                             dummy_story_view, name='story_create'),
    url(r'^story/(?P<id>.+)/list/$',                                    dummy_story_view, name='story_list'),
    url(r'^story/(?P<id>.+)/alter/$',                                 dummy_story_view, name='story_alter'),
    url(r'^story/(?P<id>.+)/details/$',                                 dummy_story_view, name='story_details'),
    url(r'^story/(?P<id>.+)/delete/$',                                  dummy_story_view, name='story_delete'),

    url(r'^story/(?P<id>\d+)/version/create/$',                          dummy_story_view, name='story_version_create'),
    url(r'^story/most_recent_version/(?P<id>\d+)/translation/(?P<language_code>\w+)/$',
        dummy_translation_view,
        name='story_version_most_recent_with_translation'),
    url(r'^story/(?P<id>\d+)/live/$',                                   dummy_story_view, name='story_version_get'),
    url(r'^story/version/(?P<id>\d+)/alter/$',                          dummy_story_view, name='story_version_alter'),
    url(r'^story/version/(?P<id>\d+)/delete/$',                          dummy_story_view, name='story_version_delete'),

    url(r'^story/version/(?P<id>\d+)/translation/(?P<language_code>\w+)/$', dummy_translation_view, name='version_translation_get'),
    url(r'^story/version/(?P<id>\d+)/translation/create/$',             dummy_translation_view, name='version_translation_create'),
    url(r'^story/version/translation/(?P<id>\d+)/alter/$',             dummy_translation_view, name='version_translation_alter'),
    url(r'^story/version/translation/(?P<id>\d+)/delete/$',             dummy_translation_view, name='version_translation_delete'),

)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]