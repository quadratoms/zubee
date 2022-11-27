from django.contrib import admin
from .models import *
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import ZubyUser


class UserCreationForm(forms.ModelForm):
	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
	
	class Meta:
		model = ZubyUser
		fields = ('phone',)
	
	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise ValidationError("Passwords don't match")
		return password2
	
	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	# password = ReadOnlyPasswordHashField()
	password = ReadOnlyPasswordHashField(label=("Password"),
        help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))
	class Meta:
		model = ZubyUser
		fields = ('phone', 'password', 'is_active', 'is_admin', 'is_supervisor', 'is_collector')
	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]


class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances
	form = UserChangeForm
	add_form = UserCreationForm
	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display = ('phone', 'is_admin','is_supervisor', 'is_collector', 'activate')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('phone', 'password')}),
		('Personal info', {'fields': ('email','activate')}),
		('Permissions', {'fields': ('is_admin','is_supervisor', 'is_collector')}),
		)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
	(None, {
	'classes': ('wide',),
	'fields': ('phone', 'email', 'password1', 'password2', 'is_admin','is_supervisor', 'is_collector', 'activate'),
	}),
	)
	search_fields = ('phone',)
	ordering = ('phone',)
	filter_horizontal = ()
# Now register the new UserAdmin...
admin.site.register(ZubyUser,UserAdmin)
# admin.site.register(MybUser)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

admin.site.register(Costumer)
admin.site.register(Level)
admin.site.register(Bankdetail)
admin.site.register(Guarantor)
admin.site.register(Loan)
admin.site.register(LoanPayment)
admin.site.register(Card)
admin.site.register(VirtualAccount)
admin.site.register(Repayment)
admin.site.register(Otp)
admin.site.register(Loanstatus)
admin.site.register(Contactlist)
admin.site.register(Supervisor)
admin.site.register(Collector)
# admin.site.register(CollectorRecord)
# admin.site.register(Order)

# Register your models here.
