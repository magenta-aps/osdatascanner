# Generated by Django 3.2.11 on 2023-09-14 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0023_account_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='dpo_contact_style',
            field=models.CharField(choices=[('NO', 'None'), ('SD', 'Single DPO'), ('UD', 'Unit DPO')], default='NO', max_length=2, verbose_name='DPO contact style'),
        ),
        migrations.AddField(
            model_name='organization',
            name='dpo_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='DPO name'),
        ),
        migrations.AddField(
            model_name='organization',
            name='dpo_value',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='DPO value'),
        ),
        migrations.AddField(
            model_name='organization',
            name='show_support_button',
            field=models.BooleanField(default=False, verbose_name='show support button'),
        ),
        migrations.AddField(
            model_name='organization',
            name='support_contact_style',
            field=models.CharField(choices=[('NO', 'None'), ('WS', 'Website'), ('EM', 'Email')], default='NO', max_length=2, verbose_name='support contact style'),
        ),
        migrations.AddField(
            model_name='organization',
            name='support_name',
            field=models.CharField(blank=True, default='IT', max_length=100, verbose_name='support name'),
        ),
        migrations.AddField(
            model_name='organization',
            name='support_value',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='support value'),
        ),
    ]
