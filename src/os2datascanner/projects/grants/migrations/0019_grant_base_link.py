from django.db import migrations, models
import django.db.models.deletion
import uuid


def set_parent(apps, schema_editor):
    """ Create a parent Grant for every soon-to-be subclass. """
    Grant = apps.get_model("grants", "Grant")
    EWSGrant = apps.get_model("grants", "EWSGrant")
    GoogleApiGrant = apps.get_model("grants", "GoogleApiGrant")
    GraphGrant = apps.get_model("grants", "GraphGrant")
    SMBGrant = apps.get_model("grants", "SMBGrant")

    grants = [EWSGrant, GoogleApiGrant, GraphGrant, SMBGrant]

    for grant_type in grants:
        for grant in grant_type.objects.all():
            parent_grant = Grant.objects.create(uuid=grant.uuid,
                                                organization=grant.organization)
            grant.grant_ptr = parent_grant
            grant.save(update_fields=["grant_ptr"])


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0018_remove_ewsgrant_id_remove_googleapigrant_id_and_more'),
        ('organizations', '0061_organization_leadertab_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('last_updated', models.DateTimeField(auto_now=True, null=True, verbose_name='last updated')),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(class)s',
                    related_query_name='%(class)ss',
                    to='organizations.organization',
                    verbose_name='Organization'
                )),
            ],
        ),

        # Adds the pointer field to parent class - but set nullable, as we can't default to anything
        # Next migration (0020) will alter these to be non-nullable.
        migrations.AddField(
            model_name='ewsgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                auto_created=True,
                serialize=False,
            ),
        ),
        migrations.AddField(
            model_name='googleapigrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                auto_created=True,
                serialize=False,
            ),
        ),
        migrations.AddField(
            model_name='graphgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                auto_created=True,
                serialize=False,
            ),
        ),
        migrations.AddField(
            model_name='smbgrant',
            name='grant_ptr',
            field=models.OneToOneField(
                to='grants.grant',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                auto_created=True,
                serialize=False,
            ),
        ),
        migrations.RunPython(set_parent, reverse_code=migrations.RunPython.noop),
    ]
