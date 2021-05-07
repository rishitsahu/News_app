from django.db import models
import os
# Create your models here.
def get_upload_path(instance, filename):
    fileName, fileExtension = os.path.splitext(filename)
    return os.path.join("user.{1}" .format(fileExtension) )

class Document(models.Model):
    result_file=models.FileField(upload_to=get_upload_path)


class Contact(models.Model):
    name=models.CharField(max_length=122)
    email=models.CharField(max_length=122)
    desc=models.TextField()
    date=models.DateField()
    #so that the form isn't saved as contact.object instead its ssaved as name of the person
    class Meta:  
        db_table = "issues"  