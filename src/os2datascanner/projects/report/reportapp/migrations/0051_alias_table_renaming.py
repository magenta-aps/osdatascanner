# Generated by Django 3.2.11 on 2022-05-11 12:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0004_alias'),
        ('os2datascanner_report', '0050_alias_reportapp_populate_missing_values'),
    ]

    operations = [
        # These fields and models can safely be removed
        # all data we actually need, now lives in parent table Alias
        migrations.RemoveField(
            model_name='emailalias',
            name='alias_ptr',
        ),
        migrations.RemoveField(
            model_name='webdomainalias',
            name='alias_ptr',
        ),
        migrations.DeleteModel(
            name='ADSIDAlias',
        ),
        migrations.DeleteModel(
            name='EmailAlias',
        ),
        migrations.DeleteModel(
            name='WebDomainAlias',
        ),

        # This field is needed to allow this table to 1-1 fit the
        # structure of organizations app's Alias model.
        migrations.AddField(
            model_name='Alias',
            name='account',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE,
                                    related_name='aliases',
                                    to='organizations.account',
                                    verbose_name='account',
                                    blank=True,
                                    null=True
                                    )
        ),

        # Because we moved Alias to live in the organizations app, we must perform some
        # migration magic:
        # We want to keep Django's naming convention, and keep the old data.
        # Therefore, we must safely rename the old Alias table.
        # SeparateDatabaseAndState avoids prematurely dropping the old table and its FK's
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='alias',
                    name='user',
                ),
                migrations.DeleteModel(
                    name='Alias',
                ),

            ],
            # Don't delete the table; rename it.
            # organizations/migrations/0004_alias.py
            database_operations=[
                migrations.AlterModelTable(
                    name='Alias',
                    table='organizations_alias'
                ),
            ],
        ),
        # Relation handling
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='documentreport',
                    name='alias_relation',
                    field=models.ManyToManyField(blank=True, db_table='new_alias_relation',
                                                 related_name='match_relation',
                                                 to='organizations.Alias',
                                                 verbose_name='Alias relation'),
                ),
            ],

            # We are reusing an existing table; Do nothing..
            database_operations=[]
        )
    ]
