from django.db import models

    
class Senai(models.Model):
    titulo = models.CharField(max_length=50)
    descricao = models.TextField(max_length=1500)
    logo = models.ImageField(upload_to='logo/')

    def __str__(self):
        return self.titulo
    



class Inventario(models.Model):
    LOCALIZACAO_CHOICES = [
        ('localizado', 'Localizado'),
        ('nao_localizado', 'Não Localizado')
    ]
    
    num_inventario = models.CharField(max_length=10, unique=True)
    denominacao = models.CharField(max_length=255)
    localizacao = models.CharField(max_length=10)
    link_imagem = models.URLField(max_length=500, blank=True, null=True)
    sala = models.CharField(max_length=30, blank=True, null=True)

    status_localizacao = models.CharField(
        max_length=15,
        choices=LOCALIZACAO_CHOICES,
        default='nao_localizado'  # Valor padrão ajustado para "não localizado"
    )

    def __str__(self):
        return f"{self.num_inventario} - {self.denominacao}"

    

class Sala(models.Model):
    sala = models.CharField(max_length=30, unique=True)
    descricao = models.CharField(max_length=255) 
    localizacao = models.CharField(max_length=10)
    link_imagem = models.URLField(max_length=500, blank=True, null=True)
    responsavel = models.CharField(max_length=50, unique=True)
    email_responsavel = models.EmailField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return self.sala
