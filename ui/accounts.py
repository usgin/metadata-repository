from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.contrib.auth.models import User
from models import UserProfile
from captcha.fields import ReCaptchaField

class UpdateForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    organization_name = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=50, required=False)
    street_address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    state = forms.CharField(max_length=255, required=False)
    zip = forms.CharField(max_length=255, required=False)
    
class RegistrationForm(UpdateForm):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    captcha = ReCaptchaField()
    
    def clean_username(self):
        if self.cleaned_data['username'] in User.objects.values_list('username', flat=True):
            raise forms.ValidationError('Username "%s" is already in use.' % self.cleaned_data['username'])
        return self.cleaned_data['username']
    
class ChangePasswordForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user
    
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    new_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    repeat_password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    
    def clean_old_password(self):
        data = self.cleaned_data['old_password']
        if not self.user.check_password(data): raise forms.ValidationError('Incorrect current password')
        return data
        
    def clean(self):
        if self.cleaned_data['new_password'] != self.cleaned_data['repeat_password']:
            raise forms.ValidationError('New passwords do not match')
        return self.cleaned_data
       
def profile(req):
    allowed = [ 'GET', 'POST' ] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    if req.method == 'POST':
        form = UpdateForm(req.POST)
        if form.is_valid():
            update_user(req.user, form)
            return HttpResponseRedirect('/accounts/profile?updated=True')            
    else:        
        user_data = {'first_name': req.user.first_name,
                     'last_name': req.user.last_name,
                     'email': req.user.email}
        try:
            user_profile = req.user.get_profile()
            user_data['organization_name'] = user_profile.organization_name
            user_data['phone'] = user_profile.phone
            user_data['street_address'] = user_profile.street_address
            user_data['city'] = user_profile.city
            user_data['state'] = user_profile.state
            user_data['zip'] = user_profile.zip
        except UserProfile.DoesNotExist:
            pass
        
        form = UpdateForm(user_data)
        
    context = {'form': form,
               'block_title': 'Welcome, %s' % req.user.username,
               'submit_text': 'Save Changes',
               'update': True,
               'title': 'Profile',
               'showUpdateMessage': req.GET.get('updated', False) == 'True'}
    return render_to_response('accounts/register.jade', context, context_instance=RequestContext(req))

def register(req):
    allowed = [ 'GET', 'POST' ] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    if req.method == 'POST':
        form = RegistrationForm(req.POST)
        if form.is_valid():
            create_user(form)
            return render_to_response('accounts/thanks.jade', {}, context_instance=RequestContext(req))
    else:
        form = RegistrationForm()
    
    context = {'form': form,
               'block_title': 'Create An Account',
               'submit_text': 'Register',
               'update': False,
               'title': 'Register'}        
    return render_to_response('accounts/register.jade', context, context_instance=RequestContext(req))
    
def change_password(req):
    allowed = [ 'GET', 'POST' ] 
    if req.method not in allowed:
        return HttpResponseNotAllowed(allowed)
    
    if req.method == 'POST':        
        form = ChangePasswordForm(req.user, req.POST)
        if form.is_valid():
            req.user.set_password(form.cleaned_data['new_password'])
            return HttpResponseRedirect('/accounts/profile?updated=True')
    else:
        form = ChangePasswordForm(req.user)
        
    return render_to_response('accounts/change-password.jade', {'form': form}, context_instance=RequestContext(req))
    
def create_user(validForm):
    user = User.objects.create_user(validForm.cleaned_data['username'], validForm.cleaned_data['email'], validForm.cleaned_data['password'])
    update_user(user, validForm)
    
def update_user(user, validForm):
    user.is_active = False
    user.first_name = validForm.cleaned_data['first_name']
    user.last_name = validForm.cleaned_data['last_name']
    user.save()
    
    try:
        user_profile = user.get_profile()
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
        
    user_profile.organization_name = validForm.cleaned_data['organization_name']
    user_profile.phone = validForm.cleaned_data['phone']
    user_profile.street_address = validForm.cleaned_data['street_address']
    user_profile.city = validForm.cleaned_data['city']
    user_profile.state = validForm.cleaned_data['state']
    user_profile.zip = validForm.cleaned_data['zip']
    user_profile.save()
    

    
    