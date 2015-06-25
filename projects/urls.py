from django.conf.urls import patterns, include, url
from projects.views import dummy_view, dummy_story_view, dummy_translation_view


urlpatterns = patterns('',
    url(r'^project/create/$',                                           dummy_view, name='project_create'),
    url(r'^project/list/$',                                             dummy_view, name='project_list'),
    url(r'^project/(?P<id>.+)/$',                                       dummy_view, name='project_get'),
    url(r'^project/(?P<id>.+)/alter/$',                                 dummy_view, name='project_alter'),
    url(r'^project/(?P<id>.+)/delete/$',                                dummy_view, name='project_delete'),
    url(r'^project/(?P<id>.+)/add_users/$',                             dummy_view, name='project_add_users'),
    url(r'^project/(?P<id>.+)/remove_users/$',                          dummy_view, name='project_remove_users'),
    url(r'^project/(?P<id>.+)/list_users/$',                            dummy_view, name='project_list_users'),

    url(r'^story/create/$',                                             dummy_story_view, name='story_create'),
    url(r'^story/(?P<id>.+)/list/$',                                    dummy_story_view, name='story_list'),
    url(r'^story/(?P<id>.+)/alter/$',                                 dummy_story_view, name='story_alter'),
    url(r'^story/(?P<id>.+)/details/$',                                 dummy_story_view, name='story_details'),
    url(r'^story/(?P<id>.+)/delete/$',                                  dummy_story_view, name='story_delete'),

    url(r'^story/(?P<id>\d+)/version/create/$',                          dummy_story_view, name='story_version_create'),
    url(r'^story/version/(?P<id>\d+)/translation/(?P<language_code>\w+)/$',
        dummy_translation_view,
        name='story_version_most_recent_with_translation'),
    url(r'^story/(?P<id>\d+)/live/$',                                   dummy_story_view, name='story_version_get'),
    url(r'^story/version/(?P<id>\d+)/alter/$',                          dummy_story_view, name='story_version_alter'),
    url(r'^story/version/(?P<id>\d+)/delete/$',                          dummy_story_view, name='story_version_delete'),

    url(r'^story/version/(?P<id>\d+)/translation/(?P<language_code>\w+)/$', dummy_translation_view, name='version_translation_get'),
    url(r'^story/version/(?P<id>\d+)/translation/create/$',             dummy_translation_view, name='version_translation_create'),

)
