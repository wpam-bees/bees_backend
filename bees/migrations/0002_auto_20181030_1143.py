# Generated by Django 2.1.2 on 2018-10-30 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='JobFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range', models.PositiveIntegerField()),
                ('min_price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('categories', models.ManyToManyField(related_name='interests', to='bees.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=9)),
                ('accepted', models.BooleanField(default=False)),
                ('bidder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bees.WorkerBee')),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='principal',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bees.EmployerBee'),
        ),
        migrations.AlterField(
            model_name='employerbee',
            name='credit_card',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employer', to='bees.CreditCardData'),
        ),
        migrations.AddField(
            model_name='offer',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bees.Job'),
        ),
        migrations.AddField(
            model_name='job',
            name='category',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='bees.Category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workerbee',
            name='filters',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='worker', to='bees.JobFilter'),
            preserve_default=False,
        ),
    ]
