from django import forms
from .models import Instrument, Category
from django import forms
from .models import Category
from django.forms import ModelForm
from django import forms
from .models import Instrument
from decimal import Decimal
import datetime
import re
from django.contrib import messages

# ==============Formularul de filtrare pentru instrumente de pe pagina shop-ului===================
class InstrumentFilterForm(forms.Form):
    
    model = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Cauta dupa model...'
    }))
    
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Min'
    }))
    
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'placeholder': 'Max'
    }))

    category = forms.ChoiceField(required=False)
    
    type = forms.ChoiceField(required=False)
    
    min_rating = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'step': '0.5'
        })
    )
    
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Implicit'),
            ('price_low', 'Pret crescator'),
            ('price_high', 'Pret descrescator'),
            ('rating', 'Dupa rating'),
        ],
    )

    # Cand se creeaza un formular de filtrare, se populeaza 
    # cu categoriile si tipurile existente in baza de date
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.values_list('instrument', flat=True).distinct()
        self.fields['category'].choices = [('', 'Toate categoriile')] + [(c, c) for c in categories]
        
        types = Category.objects.values_list('type', 'type').distinct()
        self.fields['type'].choices = [('', 'Toate tipurile')] + list(types)



# ===============================Formularul de contact =========================================
class ContactForm(forms.Form):
    nume = forms.CharField(
        max_length=35,
        label='Nume'
    )
    
    prenume = forms.CharField(
        max_length=35,
        label='Prenume'
    )
    
    data_nasterii = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'Zi-Luna-An'}),
        label='Data nasterii',
        error_messages={'invalid': 'Data trebuie sa fie in formatul an.luna.zi'}
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder':'example@example.com'}),
        error_messages={'invalid': 'Introduceti o adresa de email valida.'}
    )
    
    confirm_email = forms.EmailField(
        label='Confirmare Email',
        widget=forms.EmailInput(attrs={'placeholder':'example@example.com'})
    )
    
    tip_mesaj = forms.ChoiceField(
        label='Tip mesaj',
        choices=[
            ('reclamatie', 'Reclamatie'),
            ('intrebare', 'Intrebare'),
            ('review', 'Review'),
            ('cerere', 'Cerere'),
            ('programare', 'Programare')
        ]
    )
    
    subiect = forms.CharField(
        label='Subiect',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Introduceti subiectul...',
        })
    )
    
    minim_zile_asteptare = forms.IntegerField(
        min_value=1,
        label='Minim zile asteptare',
        error_messages={'min_value': 'Numarul de zile trebuie sa fie mai mare ca zero'}
    )
    
    mesaj = forms.CharField(
        widget=forms.Textarea,
       
        error_messages={'semnatura': 'Mesajul trebuie sa se termine cu numele dumneavoastra ca semnatura.'}
    )


    def clean(self):
        cleaned_data = super().clean()
        
        # Validare email
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError("Adresele de email nu coincid.")

        # Validare varsta
        data_nastere = cleaned_data.get("data_nasterii")
        if data_nastere:
            varsta = (datetime.date.today() - data_nastere).days // 365
            if varsta < 18:
                raise forms.ValidationError("Trebuie sa aveti minim 18 ani.")

        # Validare campuri text
        text_fields = {
            'nume': 'Numele',
            'prenume': 'Prenumele',
            'subiect': 'Subiectul'
        }
        # Validare Nume Prenume Subiect
        for field, display_name in text_fields.items():
            value = cleaned_data.get(field)
            if not value:
                raise forms.ValidationError(f"{display_name} este obligatoriu.")
            elif value:
                if not value[0].isupper():
                    raise forms.ValidationError(f"{display_name} trebuie sa inceapa cu litera mare.")
                if not all(c.isalpha() or c.isspace() for c in value):
                    raise forms.ValidationError(f"{display_name} trebuie sa contina doar litere si spatii.")

        # Validare mesaj
        mesaj = cleaned_data.get("mesaj")
        if mesaj:
            mesaj = ' '.join(mesaj.split())
            
            # Verificare numar cuvinte
            cuvinte = re.findall(r'\w+', mesaj)
            if len(cuvinte) < 5:
                raise forms.ValidationError("Mesajul trebuie sa contina minim 5 cuvinte.")
            if len(cuvinte) > 100:
                raise forms.ValidationError("Mesajul trebuie sa contina maxim 100 cuvinte.")
            
            # Verificare linkuri
            if any(cuvant.lower().startswith(('http://', 'https://')) for cuvant in cuvinte):
                raise forms.ValidationError("Mesajul nu poate contine linkuri.")
                
            # Verificare semnatura
            nume = cleaned_data.get("nume")
            if cuvinte[-1] != nume:
                raise forms.ValidationError("Mesajul trebuie sa se termine cu numele dumneavoastra ca semnatura.")
                
            cleaned_data['mesaj'] = mesaj 
            
            # Calculam varsta in ani si luni
            if data_nastere:
                today = datetime.date.today()
                ani = today.year - data_nastere.year
                luni = today.month - data_nastere.month
                cleaned_data['varsta'] = f"{ani} ani si {luni} luni"
                
        return cleaned_data

class InstrumentForm(ModelForm):
    class Meta:
        model = Instrument
        fields = ['model', 'description', 'stock']
        labels = {
            'model': 'Numele modelului',
            'description': 'Descriere',
            'stock': 'Stoc disponibil'
        }
        help_texts = {
            'description': 'Descrieti caracteristicile principale ale instrumentului (min. 50 caractere)'
        }
        error_messages = {
            'model': {
                'required': 'Numele modelului este obligatoriu!',
                'max_length': 'Numele modelului este prea lung!'
            },
            'description': {
                'required': 'Descrierea este obligatorie!'
            },
            'stock': {
                'required': 'Stocul este obligatoriu!',
                'min_value': 'Stocul trebuie să fie cel puțin 0!'
            }
        }

    # Câmpuri adiționale pentru calcularea prețului final
    cost_productie = forms.DecimalField(
        label='Cost de producție (lei)',
        min_value=0,
        error_messages={
            'required': 'Costul de producție este obligatoriu!',
            'min_value': 'Costul de producție nu poate fi negativ!'
        }
    )
    
    marja_profit = forms.DecimalField(
        label='Marja de profit (%)',
        min_value=0,
        max_value=100,
        error_messages={
            'required': 'Marja de profit este obligatorie!',
            'min_value': 'Marja de profit nu poate fi negativă!',
            'max_value': 'Marja de profit nu poate depăși 100%!'
        }
    )

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 50:
            raise forms.ValidationError(
                'Descrierea trebuie să conțină cel puțin 50 de caractere!'
            )
        if not description[0].isupper():
            raise forms.ValidationError(
                'Descrierea trebuie să înceapă cu literă mare!'
            )
        return description

    def clean_model(self):
        model = self.cleaned_data.get('model')
        if not all(char.isalnum() or char.isspace() for char in model):
            raise forms.ValidationError(
                'Numele modelului poate conține doar litere, cifre și spații!'
            )
        return model

    def clean(self):
        cleaned_data = super().clean()
        cost_productie = cleaned_data.get('cost_productie')
        marja_profit = cleaned_data.get('marja_profit')
        stock = cleaned_data.get('stock')

        if cost_productie and marja_profit:
            if cost_productie < 100 and marja_profit > 50:
                raise forms.ValidationError(
                    'Pentru produse cu cost sub 100 lei, marja de profit nu poate depăși 50%!'
                )

        if stock and cost_productie:
            valoare_totala = stock * cost_productie
            if valoare_totala > 10000:
                raise forms.ValidationError(
                    'Valoarea totală a stocului nu poate depăși 10.000 lei!'
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculăm prețul final folosind costul de producție și marja de profit
        cost_productie = self.cleaned_data.get('cost_productie')
        marja_profit = self.cleaned_data.get('marja_profit')
        
        # Calculăm prețul final
        profit = cost_productie * (marja_profit / 100)
        pret_final = cost_productie + profit
        
        # Rotunjim la cel mai apropiat număr întreg
        instance.price = Decimal(pret_final).quantize(Decimal('0'))
        
        # Setăm un rating inițial de 0
        instance.rating = 0
        
        if commit:
            instance.save()
        return instance