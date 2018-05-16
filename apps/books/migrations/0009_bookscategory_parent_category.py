# Generated by Django 2.0.5 on 2018-05-16 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_books_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookscategory',
            name='parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_cat', to='books.BooksCategory', verbose_name='父类目级别'),
        ),
    ]