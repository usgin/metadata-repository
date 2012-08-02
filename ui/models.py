from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib import admin

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    
    organization_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return self.user.username

    def to_contact(self):
        return {
            "Name": "%s %s" % (self.user.first_name, self.user.last_name),
            "OrganizationName": self.organization_name,
            "ContactInformation": {
                "Phone": self.phone,
                "email": self.user.email,
                "Address": {
                    "Street": self.street_address,
                    "City": self.city,
                    "State": self.state,
                    "Zip": self.zip            
                }
            }           
        }
        
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_filter = ['organization_name']
    
admin.site.register(UserProfile, ProfileAdmin)

# This bit should automatically generate a user profile for each created user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)        
post_save.connect(create_user_profile, sender=User)    
