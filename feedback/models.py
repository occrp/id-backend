from django.db import models

class Feedback(models.Model):
    name = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __unicode__(self):
        return u"From: %s <%s>\nDate: %s\n\n%s\n" % (self.name, self.email,
            self.timestamp, self.message)

