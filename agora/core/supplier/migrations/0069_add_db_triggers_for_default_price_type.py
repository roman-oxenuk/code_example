# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        if connection.vendor == 'postgresql':
            cursor = connection.cursor()
            cursor.execute('''

                CREATE FUNCTION validate_only_one_default_price_type_for_single_supplier() returns trigger as $$
                DECLARE
                    default_price_count int;
                BEGIN
                    default_price_count := (
                        SELECT count(id)
                        FROM supplier_pricetype
                        WHERE "supplier_id" = NEW.supplier_id AND "default" = true AND "deleted" = false);
                    IF (default_price_count != 1) THEN
                      RAISE EXCEPTION 'Default price type have to be only one for single supplier (suppler_id = %)', NEW.supplier_id;
                    END IF;
                      RETURN NULL;
                END;
                $$ language plpgsql;

                CREATE CONSTRAINT TRIGGER only_one_default_price_type_for_single_supplier_trigger
                AFTER INSERT OR UPDATE ON supplier_pricetype
                DEFERRABLE INITIALLY DEFERRED
                FOR EACH ROW
                EXECUTE PROCEDURE validate_only_one_default_price_type_for_single_supplier();
            ''')

    def backwards(self, orm):
        if connection.vendor == 'postgresql':
            cursor = connection.cursor()
            cursor.execute('''
                DROP FUNCTION validate_only_one_default_price_type_for_single_supplier() CASCADE;
            ''')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'company.city': {
            'Meta': {'ordering': "['-rank', 'city']", 'object_name': 'City'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cities'", 'null': 'True', 'to': u"orm['company.Country']"}),
            'fed_region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'company.country': {
            'Meta': {'ordering': "('country',)", 'object_name': 'Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'iso_code_short': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'ru'", 'max_length': '5'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contractor.contractor': {
            'Meta': {'object_name': 'Contractor'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contractors'", 'null': 'True', 'to': u"orm['contractor.ContractorGroup']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contractor_groups'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['contractor.ContractorGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_retail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sync': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'sync_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contractor.contractorgroup': {
            'Meta': {'object_name': 'ContractorGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'text_discount': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'text_sum': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'users'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['contractor.Contractor']"}),
            'current_contractor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'user'", 'null': 'True', 'to': u"orm['contractor.Contractor']"}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'external': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'extra_data': ('django_pgjson.fields.JsonBField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_activity_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'order_sort_str': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '64'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'users'", 'null': 'True', 'to': u"orm['supplier.Supplier']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'currency.currency': {
            'Meta': {'object_name': 'Currency'},
            'char_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'primary_key': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exchange_rate': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '31'})
        },
        u'product.category': {
            'Meta': {'object_name': 'Category'},
            'active_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'column': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': (u'sorl.thumbnail.fields.ImageField', [], {'max_length': '192', 'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'meta_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'min_order_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nonactive_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'notify_emails': ('multi_email_field.fields.MultiEmailField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': u"orm['product.Category']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'users_favorite': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'favorite_categories'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['core.User']"})
        },
        u'product.categorysuppliercategory': {
            'Meta': {'object_name': 'CategorySupplierCategory'},
            'category': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['product.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'supplier_category': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['product.SupplierCategory']"})
        },
        u'product.distributionchannel': {
            'Meta': {'object_name': 'DistributionChannel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'min_count': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'multiplicity': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'root': ('mptt.fields.TreeOneToOneField', [], {'to': u"orm['product.Category']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'warehouse_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['supplier.WarehouseGroup']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'product.distributioncompany': {
            'Meta': {'object_name': 'DistributionCompany'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'product.distributionmarket': {
            'Meta': {'object_name': 'DistributionMarket'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'markets'", 'to': u"orm['product.DistributionChannel']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'markets'", 'to': u"orm['product.DistributionCompany']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'product.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['company.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'product.measureunit': {
            'Meta': {'object_name': 'MeasureUnit'},
            'base_unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'additional_units'", 'null': 'True', 'to': u"orm['product.MeasureUnit']"}),
            'coef': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'common': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.MeasureUnitCommon']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'denominator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dist_market': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'units'", 'null': 'True', 'to': u"orm['product.DistributionCompany']"}),
            'factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'height_comment': ('django.db.models.fields.CharField', [], {'default': "u'\\u043c'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'length_comment': ('django.db.models.fields.CharField', [], {'default': "u'\\u043c'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'numerator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['supplier.Supplier']"}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'volume_comment': ('django.db.models.fields.CharField', [], {'default': "u'\\u043c\\xb3'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'weight_comment': ('django.db.models.fields.CharField', [], {'default': "u'\\u043a\\u0433'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'width_comment': ('django.db.models.fields.CharField', [], {'default': "u'\\u043c'", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'product.measureunitcommon': {
            'Meta': {'object_name': 'MeasureUnitCommon'},
            'base_unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'additional_units'", 'null': 'True', 'to': u"orm['product.MeasureUnitCommon']"}),
            'coef': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'product.product': {
            'Meta': {'object_name': 'Product'},
            '_measure_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.MeasureUnit']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'analog_products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'analog_master_products'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.Product']"}),
            'avg_rating': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'b_placement_state': ('django_states.fields.StateField', [], {'default': "'placed'", 'max_length': '100'}),
            'categories': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['product.Category']", 'null': 'True', 'blank': 'True'}),
            'category': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['product.Category']"}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_reference': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'markets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'products'", 'symmetrical': 'False', 'through': u"orm['product.ProductDistributionMarket']", 'to': u"orm['product.DistributionMarket']"}),
            'measure_units': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'products_other'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.MeasureUnit']"}),
            'meta_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.ProductPattern']", 'null': 'True', 'blank': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'product_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rate_nds': ('django.db.models.fields.FloatField', [], {'default': '18'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'rating_position': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'reference_product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'real_products'", 'null': 'True', 'to': u"orm['product.Product']"}),
            'related_products': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'master_products'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.Product']"}),
            'rest': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '10'}),
            'rest_indicator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'show_on_landing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_on_shop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'supplier_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['product.SupplierCategory']"}),
            'supplier_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'product.productdistributionmarket': {
            'Meta': {'object_name': 'ProductDistributionMarket'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.DistributionMarket']"}),
            'measure_unit_common': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'product_dms'", 'null': 'True', 'to': u"orm['product.MeasureUnitCommon']"}),
            'measure_unit_of_multiplicity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'product_dms2'", 'null': 'True', 'to': u"orm['product.MeasureUnitCommon']"}),
            'multiplicity': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.Product']"})
        },
        u'product.productpattern': {
            'Meta': {'object_name': 'ProductPattern'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'product_patterns'", 'symmetrical': 'False', 'to': u"orm['product.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'properties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'product_patterns'", 'symmetrical': 'False', 'to': u"orm['product.Property']"})
        },
        u'product.property': {
            'Meta': {'ordering': "['-priority']", 'object_name': 'Property'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'properties'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.Category']"}),
            'dc_recalculation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_by': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filter_template': ('django.db.models.fields.IntegerField', [], {'default': '2', 'max_length': '10'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'properties'", 'null': 'True', 'to': u"orm['product.PropertyGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_base': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_cascade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_global': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'measure_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['product.MeasureUnit']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'on_product_catalog': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'on_product_detail': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'priority': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'unimportant': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        },
        u'product.propertygroup': {
            'Meta': {'object_name': 'PropertyGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'product.suppliercategory': {
            'Meta': {'object_name': 'SupplierCategory'},
            'category': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'supplier_category'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['product.Category']"}),
            'd_categories': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['product.Category']", 'null': 'True', 'through': u"orm['product.CategorySupplierCategory']", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': u"orm['product.SupplierCategory']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'supplier_category'", 'to': u"orm['supplier.Supplier']"}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'supplier.assortmentupdateinfo': {
            'Meta': {'object_name': 'AssortmentUpdateInfo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'send_reminder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'supplier': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['supplier.Supplier']", 'unique': 'True'}),
            'updates_frequency_days': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'supplier.contractorsuppliermanager': {
            'Meta': {'object_name': 'ContractorSupplierManager', 'db_table': "'portal_contractorsuppliermanager'"},
            'department_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'department_uuid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'dist_channels': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'managers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.DistributionChannel']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'notify_about_new_order': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_about_order_change_status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_about_order_corrected': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'managers'", 'to': u"orm['supplier.Supplier']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'current_manager'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.User']"}),
            'warehouses': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cs_managers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['supplier.Warehouse']"})
        },
        u'supplier.pricetype': {
            'Meta': {'object_name': 'PriceType'},
            'default': ('django.db.models.fields.NullBooleanField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'distribution_markets': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'price_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.DistributionMarket']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'rrc': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'price_types'", 'to': u"orm['supplier.Supplier']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'supplier.remindedproduct': {
            'Meta': {'object_name': 'RemindedProduct'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'reminded_about_update'", 'unique': 'True', 'to': u"orm['product.Product']"})
        },
        u'supplier.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'autoconversion_currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['currency.Currency']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'avg_rating': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_data_import': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_multi_warehouse_order': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_preorder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_warehouse_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integration_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'is_gen_act': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'opt_price_delivery': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'opt_price_delivery_hour': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'opt_price_delivery_km': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'order_min_sum': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'order_min_sum_currency': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'supplier_order_min_sum_currency'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['currency.Currency']"}),
            'order_process': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rating_position': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'rests_display_mode': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rests_display_shop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rests_display_threshold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rests_notification_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rests_notification_threshold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rrc_price_delivery': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'rrc_price_delivery_hour': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'rrc_price_delivery_km': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'seller_params': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_nds': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'use_verification': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'supplier.supplierprofile': {
            'Meta': {'object_name': 'SupplierProfile'},
            'about_us': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'assortment_of': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bid_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['product.Category']", 'null': 'True', 'blank': 'True'}),
            'brands': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'suppliers'", 'null': 'True', 'to': u"orm['company.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'suppliers'", 'null': 'True', 'to': u"orm['company.Country']"}),
            'delivery': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'discount_of_orders_per_month': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'discounts_on_aggregate': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'dropshipment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'erp_system': ('django.db.models.fields.CharField', [], {'default': "'NO'", 'max_length': '2'}),
            'features_of_logistics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_order': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_discount_for_single_order': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_discount_is_not_saved': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_own_production': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_private_courier_services': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_production_of_individual_models': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_work_with_individuals': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_working_with_ip': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'limit_sum': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'logo': (u'sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'min_delivery_time_to_tk': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'min_number_of_items': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'min_order_quantity_per_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_time_shipment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'other_information': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'quantity_produced': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reward_percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '18', 'decimal_places': '15'}),
            'schedule': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'selling_brands': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'shares_for_retailers': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['supplier.Supplier']"}),
            'terms_of_constant_prices': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'terms_of_use_returns': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'trade_categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'suppliers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['product.Category']"}),
            'transport_companies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'warehouses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['company.City']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'supplier.warehouse': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Warehouse'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'coordinates': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'district': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'warehouses'", 'null': 'True', 'to': u"orm['supplier.WarehouseGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'warehouses'", 'to': u"orm['supplier.Supplier']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'})
        },
        u'supplier.warehousegroup': {
            'Meta': {'object_name': 'WarehouseGroup'},
            'abbr': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'supplier.warehouseschedule': {
            'Meta': {'unique_together': "(('warehouse', 'weekday'),)", 'object_name': 'WarehouseSchedule'},
            'close_break_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'close_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'open_break_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'open_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schedules'", 'to': u"orm['supplier.Warehouse']"}),
            'weekday': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['supplier']