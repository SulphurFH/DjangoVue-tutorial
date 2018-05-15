# Generated by Django 2.0.5 on 2018-05-14 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_auto_20180514_1032'),
    ]

    operations = [
        migrations.CreateModel(
            name='BooksCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_update', models.DateTimeField(auto_now=True, verbose_name='最后修改时间')),
                ('name', models.CharField(default='', help_text='类别名', max_length=30, verbose_name='类别名')),
                ('category_type', models.IntegerField(choices=[(1, '一级类别'), (2, '二级类别'), (3, '三级类别')], help_text='类目级别', verbose_name='类目级别')),
            ],
            options={
                'verbose_name': '类别',
                'verbose_name_plural': '类别',
            },
        ),
        migrations.AddField(
            model_name='books',
            name='category',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='books.BooksCategory', verbose_name='类别'),
        ),
    ]
