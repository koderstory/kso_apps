from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountManagersTests(TestCase):

    def test_create_user(self):
        Account = get_user_model()
        account = Account.objects.create_user(email='normal@account.com', password='foo')
        self.assertEqual(account.email, 'normal@account.com')
        self.assertTrue(account.is_active)
        self.assertFalse(account.is_staff)
        self.assertFalse(account.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(account.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            Account.objects.create_user()
        with self.assertRaises(TypeError):
            Account.objects.create_user(email='')
        with self.assertRaises(ValueError):
            Account.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        Account = get_user_model()
        admin_user = Account.objects.create_superuser(email='super@account.com', password='foo')
        self.assertEqual(admin_user.email, 'super@account.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            Account.objects.create_superuser(
                email='super@account.com', password='foo', is_superuser=False)