from django import forms





class usersearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search for items...',
                'class': 'form-control',
                'style': 'width: 250px;'  # Set static width
            }
        ),
        label=''  # Hide label
    )

class qtyForm(forms.Form):
    qty = forms.IntegerField(min_value=1, label='Quantity')