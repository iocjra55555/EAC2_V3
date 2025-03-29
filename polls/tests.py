from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User

class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    # fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari

    def setUp(self):
        # Creem superusuari dins de setUp, que s'executa abans de cada test
        user = User.objects.create_superuser("isard", "pirineus", "pirineus")
        user.save()

    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual(self.selenium.title, "Log in | Django site admin")

        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")

    def test_login_error(self):
        # comprovem que amb un usuari i contrasenya inexistent, el test falla
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )
 
        # introduim dades de login
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('usuari_no_existent')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('contrasenya_incorrecta')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()
 
        # utilitzem assertNotEqual per testejar que NO hem entrat
        self.assertNotEqual( self.selenium.title , "Site administration | Django site admin" )

    def test_crear_usuario_sense_permisos_i_login_fallit(self):
        # document:  https://selenium-python.readthedocs.io/locating-elements.html 
        # 1. Navegar al panell d'administració de Django
        self.selenium.get(self.live_server_url + "/admin")

        # 2. Iniciar sessió com a superusuari i entrar web-admin
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("isard")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("pirineus")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # 3. Navegar a la pàgina de creació d'usuaris
        #va directament a la pagina per entrar usuari
        #self.selenium.get(self.live_server_url + "/admin/auth/user/add/")
        #self.selenium.find_element(By.LINK_TEXT, "Users").click()
        #self.selenium.find_element(By.LINK_TEXT, "Add").click()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/main/div/div[1]/div[1]/table/tbody/tr[2]/th/a').click()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/main/div/div/ul/li/a').click()

        # 4. Omplir el formulari per crear un nou usuari sense permisos
        #username1_input = self.selenium.find_element(By.NAME, "username")
        #username1_input = self.selenium.find_element("id", "id_username")
        #username1_input = self.selenium.find_element(By.XPATH, '//input[@value="username"]')
        #username1_input = self.selenium.find_element("css selector", "#id_username")
        username1_input = self.selenium.find_element(By.ID, 'id_username')
        username1_input.send_keys("ioc")
        #password1_input = self.selenium.find_element(By.NAME, "password")
        password1_input = self.selenium.find_element(By.ID, 'id_password1')
        password1_input.send_keys("12345678ioc")
        #password1_confirm_input = self.selenium.find_element(By.NAME, "password2")
        password1_confirm_input = self.selenium.find_element(By.ID, 'id_password2')
        password1_confirm_input.send_keys("12345678ioc")
        #email_input = self.selenium.find_element(By.NAME, "email")
        #email_input.send_keys("ioc@ioc.cat")
        #self.selenium.find_element(By.XPATH, '//input[@value="Save"]').click()
        self.selenium.find_element(By.NAME, "_save").click()

        #4.5 LOG OUT, per provar el usuari nou sense permissos
        self.selenium.find_element(By.ID, 'logout-form').click()

        # 5. Intentar iniciar sessió amb l'usuari sense permisos
        self.selenium.get(self.live_server_url + "/admin/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("ioc")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("12345678ioc")
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # 6. Verificar que l'inici de sessió ha fallat
        self.assertIn("Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.", self.selenium.page_source)