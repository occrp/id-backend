from django.conf.urls import patterns, include, url
from projects import views


urlpatterns = patterns('',
    url(r'^$', views.api_root),

    url(r'^projects/$',                                                 views.ProjectList.as_view(), name='project_list'),
    url(r'^projects/(?P<pk>[0-9]+)/$',                                  views.ProjectDetail.as_view(), name='project_detail'),
    url(r'^projects/(?P<pk>[0-9]+)/users/$',                            views.ProjectUsers.as_view(), name='project_users'),

    url(r'^projects/(?P<pk>[0-9]+)/plans/$',                            views.ProjectPlanList.as_view(), name='project_plan_list'),
    url(r'^projects/plans/(?P<pk>[0-9]+)/$',                            views.ProjectPlanDetail.as_view(), name='project_plan_detail'),

    url(r'^projects/(?P<pk>[0-9]+)/stories/$',                          views.StoryList.as_view(), name='story_list'),
    url(r'^stories/(?P<pk>[0-9]+)/$',                                   views.StoryDetail.as_view(), name='story_detail'),

    url(r'^stories/(?P<pk>[0-9]+)/live/(?P<language_code>[a-zA-Z]+)/$', views.StoryVersionLive.as_view(), name='story_live_version_in_language'),
    url(r'^stories/(?P<pk>[0-9]+)/versions/$',                          views.StoryVersionList.as_view(), name='story_version_list'),
    url(r'^stories/versions/(?P<pk>[0-9]+)/$',                          views.StoryVersionDetail.as_view(), name='story_version_detail'),

    url(r'^versions/(?P<pk>[0-9]+)/translations/$',                    views.StoryTranslationList.as_view(), name='story_translation_list'),
    url(r'^versions/translations/(?P<pk>[0-9]+)/$',                    views.StoryTranslationDetail.as_view(), name='story_translation_detail')

)

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]