from django.test import TestCase
from .models import Inventario, Sala

class InventarioModelTestCase(TestCase):
    def setUp(self):
        # Configurando os dados de teste para Inventario
        self.inventario = Inventario.objects.create(
            num_inventario="INV001",
            denominacao="Cadeira de Escritório",
            localizacao="Bloco A",
            link_imagem="http://example.com/cadeira.jpg",
            sala="Sala 101",
            status_localizacao="localizado"
        )

    def test_inventario_criacao(self):
        # Verifica se o inventário foi criado corretamente
        self.assertEqual(self.inventario.num_inventario, "INV001")
        self.assertEqual(self.inventario.denominacao, "Cadeira de Escritório")
        self.assertEqual(self.inventario.localizacao, "Bloco A")
        self.assertEqual(self.inventario.link_imagem, "http://example.com/cadeira.jpg")
        self.assertEqual(self.inventario.sala, "Sala 101")
        self.assertEqual(self.inventario.status_localizacao, "localizado")

    def test_inventario_default_status(self):
        # Testa se o valor padrão de status_localizacao é "não localizado"
        inventario_sem_status = Inventario.objects.create(
            num_inventario="INV002",
            denominacao="Mesa de Reunião",
            localizacao="Bloco B",
        )
        self.assertEqual(inventario_sem_status.status_localizacao, "nao_localizado")

    def test_inventario_str_representation(self):
        # Testa a representação em string
        self.assertEqual(str(self.inventario), "INV001 - Cadeira de Escritório")

class SalaModelTestCase(TestCase):
    def setUp(self):
        # Configurando os dados de teste para Sala
        self.sala = Sala.objects.create(
            sala="Sala 101",
            descricao="Sala utilizada para reuniões e apresentações.",
            localizacao="Bloco A",
            link_imagem="http://example.com/sala.jpg",
            responsavel="João Silva",
            quantidade_itens=15,
            email_responsavel="joao.silva@example.com"
        )

    def test_sala_criacao(self):
        # Verifica se a sala foi criada corretamente
        self.assertEqual(self.sala.sala, "Sala 101")
        self.assertEqual(self.sala.descricao, "Sala utilizada para reuniões e apresentações.")
        self.assertEqual(self.sala.localizacao, "Bloco A")
        self.assertEqual(self.sala.link_imagem, "http://example.com/sala.jpg")
        self.assertEqual(self.sala.responsavel, "João Silva")
        self.assertEqual(self.sala.quantidade_itens, 15)
        self.assertEqual(self.sala.email_responsavel, "joao.silva@example.com")

    def test_sala_default_quantidade_itens(self):
        # Testa se o valor padrão de quantidade_itens é 0
        sala_sem_itens = Sala.objects.create(
            sala="Sala 102",
            descricao="Sala vazia para uso geral.",
            localizacao="Bloco B",
            responsavel="Maria Oliveira"
        )
        self.assertEqual(sala_sem_itens.quantidade_itens, 0)

    def test_sala_str_representation(self):
        # Testa a representação em string
        self.assertEqual(str(self.sala), "Sala 101")

class InventarioUnicidadeTestCase(TestCase):
    def setUp(self):
        # Criando um inventário inicial
        Inventario.objects.create(
            num_inventario="INV001",
            denominacao="Cadeira",
            localizacao="Bloco A"
        )

    def test_inventario_num_inventario_unico(self):
        # Tentando criar um inventário com o mesmo número
        with self.assertRaises(Exception):  # Deve lançar uma exceção
            Inventario.objects.create(
                num_inventario="INV001",
                denominacao="Mesa",
                localizacao="Bloco B"
            )

class SalaUnicidadeTestCase(TestCase):
    def setUp(self):
        # Criando uma sala inicial
        Sala.objects.create(
            sala="Sala 101",
            descricao="Sala de reuniões",
            localizacao="Bloco A",
            responsavel="João Silva"
        )

    def test_sala_nome_unico(self):
        # Tentando criar uma sala com o mesmo nome
        with self.assertRaises(Exception):  # Deve lançar uma exceção
            Sala.objects.create(
                sala="Sala 101",
                descricao="Outra descrição",
                localizacao="Bloco B",
                responsavel="Maria Oliveira"
            )

    def test_sala_responsavel_unico(self):
        # Tentando criar uma sala com o mesmo responsável
        with self.assertRaises(Exception):  # Deve lançar uma exceção
            Sala.objects.create(
                sala="Sala 102",
                descricao="Nova sala",
                localizacao="Bloco C",
                responsavel="João Silva"
            )

