# Generated by Django 3.2.4 on 2021-09-30 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import_services', '0006_alter_ldapconfig_users_dn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapconfig',
            name='import_into',
            field=models.CharField(choices=[('group', 'Grupper'), ('ou', 'Organizational units')], default='ou', max_length=32, verbose_name='import users into'),
        ),
        migrations.AlterField(
            model_name='ldapconfig',
            name='search_scope',
            field=models.PositiveSmallIntegerField(choices=[(1, 'One level'), (2, 'Subtree')], help_text='For one level, the search applies only for users in the DNs specified by User DNs. For subtree, the search applies to the whole subtree. See LDAP documentation for more details.', verbose_name='search scope'),
        ),
        migrations.AlterField(
            model_name='ldapconfig',
            name='vendor',
            field=models.CharField(choices=[('ad', 'Active Directory'), ('other', 'Other')], max_length=32, verbose_name='vendor'),
        ),
    ]