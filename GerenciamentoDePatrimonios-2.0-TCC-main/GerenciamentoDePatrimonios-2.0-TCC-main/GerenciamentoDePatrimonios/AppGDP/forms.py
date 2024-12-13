from django import forms
from .models import Inventario, Sala
from django.core.exceptions import ValidationError


class formCadastroUsuario(forms.Form):
    first_name = forms.CharField(label="Nome", max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Sobrenome", max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user = forms.CharField(label="Usuário", max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    sala = forms.CharField(label="Sala", max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    group = forms.ChoiceField(
        label="Grupo", 
        choices=[('Professor', 'Professor'), ('Coordenador', 'Coordenador')], 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_sala(self):
        sala_nome = self.cleaned_data['sala']
        try:
            sala = Sala.objects.get(sala=sala_nome)
        except Sala.DoesNotExist:
            raise ValidationError("A sala informada não existe. Por favor, selecione uma sala válida.")
        return sala_nome
    
class FormLogin(forms.Form):
    user = forms.CharField(label="Usuario", max_length=40)
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['num_inventario', 'denominacao', 'localizacao','sala', 'link_imagem']  

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['sala', 'descricao', 'localizacao', 'link_imagem', 'responsavel']

