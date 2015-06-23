from django.db import models
from settings.settings import AUTH_USER_MODEL

STORYSTATUSES = (
    (1, "Research"),
    (2, "Writing"),
    (3, "Editing"),
    (4, "Copy-editing"),
    (5, "Fact-checking"),
    (6, "Translation"),
    (7, "Artwork"),
    (8, "Postponed"),
    (10, "Embargoed"),
    (11, "Published"),
)


class Project(models.Model):
    title = models.CharField(max_length=250)
    coordinator = models.ForeignKey(AUTH_USER_MODEL, related_name="coordinator")
    # podaci_root = models.CharField(max_length=50)
    users = models.ManyToManyField(AUTH_USER_MODEL, related_name="members")

    def has_access(self, user):
        if user == self.coordinator:
            return True
        if user in self.users.all():
            return True
        return False


class Story(models.Model):
    project = models.ForeignKey(Project)
    reporters = models.ManyToManyField(AUTH_USER_MODEL, related_name="reporters")
    researchers = models.ManyToManyField(AUTH_USER_MODEL, related_name="researchers")
    editors = models.ManyToManyField(AUTH_USER_MODEL, related_name="editors")
    copy_editors = models.ManyToManyField(AUTH_USER_MODEL, related_name="copy_editors")
    fact_checkers = models.ManyToManyField(AUTH_USER_MODEL, related_name="fact_checkers")
    translators = models.ManyToManyField(AUTH_USER_MODEL, related_name="translators")
    artists = models.ManyToManyField(AUTH_USER_MODEL, related_name="artists")

    published = models.DateField()
    podaci_root = models.CharField(max_length=50)

    def get_newest_status(self):
        return self.storystatus_set.latest('timestamp')

    def get_history(self):
        return self.storystatus_set.all()


# class StoryVersion(models.Model):
#     timestamp = models.DateTimeField(auto_now_add=True)
#     authored = models.ForeignKey(AUTH_USER_MODEL)
#     title = models.CharField(max_length=250)
#     text = models.TextField()


# class StoryTranslation(models.Model):
#     version = models.ForeignKey(StoryVersion)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     translator = models.ForeignKey(AUTH_USER_MODEL)
#     verified = models.BooleanField(default=False)
#     live = models.DateTimeField(default=False)
#     title = models.CharField(max_length=250)
#     text = models.TextField()


class StoryStatus(models.Model):
    story = models.ForeignKey(Story)
    set_by = models.ForeignKey(AUTH_USER_MODEL)
    timestamp = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()
    status = models.IntegerField(choices=STORYSTATUSES)
    description = models.CharField(max_length=500)


# class ProjectPlan(models.Model):
#     project = models.ForeignKey(Project)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     title = models.CharField(max_length=250)
#     description = models.TextField()
#     responsible_users = models.ManyToManyField(AUTH_USER_MODEL)
#     related_stories = models.ManyToManyField(Story)
#     order = models.IntegerField()


# class CommentModel(models.Model):
#     class Meta:
#         abstract = True

#     timestamp = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     user = models.ForeignKey(AUTH_USER_MODEL)
#     text = models.TextField()

# class ProjectComments(CommentModel):
#     ref = models.ForeignKey(Project)

# class StoryComments(CommentModel):
#     ref = models.ForeignKey(Story)

# class StoryVersionComments(CommentModel):
#     ref = models.ForeignKey(StoryVersion)

# class Translation(models.Model):
#     pass

# class TranslationComments(CommentModel):
#     ref = models.ForeignKey(Translation)

# class ProjectPlanComments(CommentModel):
#     ref = models.ForeignKey(ProjectPlan)
