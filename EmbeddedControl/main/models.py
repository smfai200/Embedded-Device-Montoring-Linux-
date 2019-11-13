from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

    def cleanname(self):
        return self.name.split('\n')[-1]