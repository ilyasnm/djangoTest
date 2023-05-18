from django.test import TestCase

class PageAPITestCase(TestCase):
   class PageAPITestCase(TestCase):
    def test_get_page_list(self):
        # Créez une page fictive pour les besoins du test
        Page.objects.create(title="Page 1", content="Contenu de la page 1")
        Page.objects.create(title="Page 2", content="Contenu de la page 2")

        # Effectuez une requête GET sur le point d'accès
        response = self.client.get('/api/pages/')

        # Vérifiez que la réponse renvoie le code de statut 200 OK
        self.assertEqual(response.status_code, 200)

        # Vérifiez que la réponse contient une liste de pages
        pages = response.json()
        self.assertIsInstance(pages, list)

        # Vérifiez que le nombre de pages dans la réponse correspond au nombre de pages créées
        self.assertEqual(len(pages), 2)

    def setUp(self):
        # Créez une page fictive pour le test
        self.page = Page.objects.create(title="Page de test", content="Contenu de la page de test")

    def test_get_page_details(self):
        # Effectuez une requête GET sur le point d'accès avec l'ID de la page
        response = self.client.get(f'/api/pages/{self.page.id}/')

        # Vérifiez que la réponse renvoie le code de statut 200 OK
        self.assertEqual(response.status_code, 200)

        # Vérifiez que la réponse contient les détails de la page
        page_details = response.json()
        self.assertEqual(page_details['id'], self.page.id)
        self.assertEqual(page_details['title'], self.page.title)
        self.assertEqual(page_details['content'], self.page.content)

    def setUp(self):
        # Créez une page fictive pour le test
        self.page = Page.objects.create(title="Page de test", content="Contenu de la page de test")

    def test_update_page(self):
        # Effectuez une requête PATCH sur le point d'accès avec l'ID de la page et les données de mise à jour
        updated_data = {'title': 'Nouveau titre'}
        response = self.client.patch(f'/api/pages/{self.page.id}/', updated_data)

        # Vérifiez que la réponse renvoie le code de statut 200 OK
        self.assertEqual(response.status_code, 200)

        # Vérifiez que la page a été mise à jour avec les nouvelles données
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, updated_data['title'])