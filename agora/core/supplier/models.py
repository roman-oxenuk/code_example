# -*- coding: utf-8 -*-
import datetime

from jsonfield import JSONField

from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.urlresolvers import reverse_lazy
from django.contrib.contenttypes import generic
from django.db import models, transaction
from django.dispatch import Signal
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as l_
from django.contrib.contenttypes.models import ContentType

from agora.core.company.models import Company
from agora.core.utils.cache import super_cached_property
from agora.core.utils.softdelete import SoftDeleteMixin
from agora.core.model_mixins import RatingMixin
from agora.core.holidays.utils import SCHEDULE_CHOICES
from .managers import PriceTypeManager, SupplierManager, RemindedProductManager
from .model_views import SupplierView


class Supplier(RatingMixin, SoftDeleteMixin):
    INTEGRATION_NONE = 1
    INTEGRATION_ERP = 2
    INTEGRATION_DATA_IMPORT = 3
    INTEGRATION_MY_WAREHOUSE = 4

    INTEGRATION_TYPES = [
        (INTEGRATION_NONE, l_(u'Не подключен')),
        (INTEGRATION_ERP, l_(u'Подключен через ERP')),
        (INTEGRATION_DATA_IMPORT, l_(u'Выгружен каталог')),
        (INTEGRATION_MY_WAREHOUSE, l_(u'Подключен через "МойСклад"')),
    ]

    RESTS_DISPLAY = 0
    RESTS_MUCHLESS = 1
    RESTS_BINARY = 2
    RESTS_BINARY_ALT = 3
    RESTS_MUCH = 4

    DISPLAY_RESTS_MODES = (
        (RESTS_DISPLAY, l_(u'Показывать остатки')),
        (RESTS_MUCH, l_(u'Показывать остатки/"много"')),
        (RESTS_MUCHLESS, l_(u'Показывать "много/"мало/"нет в наличии"')),
        (RESTS_BINARY, l_(u'Показывать "в наличии"/"нет в наличии"')),
        (RESTS_BINARY_ALT, l_(u'Показывать только склад, если на нем присутствуют остатки')),
    )

    STATUS_REGISTERED = 0
    STATUS_PREMODERATION = 1
    STATUS_VERIFIED = 2
    STATUSES = (
        (STATUS_REGISTERED, l_(u'Зарегистрирован')),
        (STATUS_PREMODERATION, l_(u'На премодерации')),
        (STATUS_VERIFIED, l_(u'Верифицирован')),
    )

    company = generic.GenericRelation(Company, unique=True)

    # entity_company = models.ForeignKey(Company, null=True, blank=True, related_name=u'entity_suppliers')
    created_at = models.DateTimeField(verbose_name=l_(u'Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=l_(u'Дата обновления'))

    # Custom supplier settings.
    order_process = models.BooleanField(default=True, verbose_name=l_(u'Автоматическое проведение заказа'))
    is_gen_act = models.BooleanField(default=False, verbose_name=l_(u'Доступна генерация акта сверки'))
    hide_warehouse_name = models.BooleanField(default=False, verbose_name=l_(u'Скрывать склад в заказе'))
    integration_type = models.IntegerField(choices=INTEGRATION_TYPES, default=INTEGRATION_NONE,
                                           verbose_name=l_(u'Тип подключения'))
    enable_data_import = models.BooleanField(
        default=settings.DEFAULT_SUPPLIER_ENABLE_DATA_IMPORT,
        verbose_name=l_(u'Доступна самостоятельная загрузка данных')
    )

    enable_preorder = models.BooleanField(default=False, verbose_name=l_(u'Доступен заказ товаров "Под заказ"'))
    enable_multi_warehouse_order = models.BooleanField(default=False, verbose_name=l_(u'Доступен заказ товаров в нескольких складах одновременно'))
    rests_display_mode = models.IntegerField(choices=DISPLAY_RESTS_MODES, default=RESTS_DISPLAY,
                                             verbose_name=l_(u'Отображение остатков'))
    rests_display_threshold = models.IntegerField(default=0, verbose_name=l_(u'Порог много/мало'))

    rests_notification_send = models.BooleanField(default=False, verbose_name=l_(u'Присылать уведомления о снижении остатков'))
    rests_notification_threshold = models.IntegerField(default=0, verbose_name=l_(u'Порог уведомления о снижении остатков'),
                                                       help_text=l_(u'Если установлен этот параметр, то уведомления о снижении остатков '
                                                                    u'будут присылаться по достижении этого порога'))

    rests_display_shop = models.BooleanField(default=False, verbose_name=l_(u'Показывать остатки на публичной витрине'))

    use_nds = models.BooleanField(default=True, verbose_name=l_(u'НДС'))

    autoconversion_currency = models.ForeignKey('currency.Currency', null=True, blank=True, on_delete=models.SET_NULL,
                                                verbose_name=l_(u'Валюта каталога'),
                                                help_text=l_(u'Пустой вариант означает отсутствие конвертации'))
    use_verification = models.BooleanField(verbose_name=l_(u'Использовать верификацию пользователей'),
                                           help_text=l_(u'Если установлен этот параметр, то пользователи, '
                                                        u'которые не отмечены в панели администрирования как'
                                                        u'"верифицированные", '
                                                        u'не будут иметь доступ к каталогу'),
                                           default=False)  # TODO: это нужно переносить в VisualDesignConfiguration

    seller_params = JSONField(verbose_name=u'Параметры мини-сайта в розничной части',
                              null=True, blank=True, editable=False)

    status = models.IntegerField(choices=STATUSES, default=STATUS_REGISTERED,
                                 verbose_name=l_(u'Статус поставщика в системе'))

    order_min_sum = models.DecimalField(verbose_name=l_(u'Минимальная сумма заказа'), max_digits=12, decimal_places=2,
                                        default=0, null=True, blank=True,
                                        help_text=l_(u'Данное значение будет учитываться перед отправкой заказа'),
                                        validators=[MinValueValidator(0)])
    order_min_sum_currency = models.ForeignKey('currency.Currency', null=True, blank=True, on_delete=models.SET_NULL,
                                               verbose_name=l_(u'Валюта минимальной суммы заказа'), related_name='supplier_order_min_sum_currency')

    """
    Стоимость доставки опт. и розн.
    """
    opt_price_delivery = models.DecimalField(verbose_name=l_(u'опт-стоимость доставки'), max_digits=12, decimal_places=2,
                                             default=0, null=True, blank=True,)
    opt_price_delivery_km = models.DecimalField(verbose_name=l_(u'опт-стоимость километра'), max_digits=12, decimal_places=2,
                                                default=0, null=True, blank=True,)
    opt_price_delivery_hour = models.DecimalField(verbose_name=l_(u'опт-стоимость часа'), max_digits=12, decimal_places=2,
                                                  default=0, null=True, blank=True,)

    rrc_price_delivery = models.DecimalField(verbose_name=l_(u'розн-стоимость доставки'), max_digits=12, decimal_places=2,
                                             default=0, null=True, blank=True,)
    rrc_price_delivery_km = models.DecimalField(verbose_name=l_(u'розн-стоимость километра'), max_digits=12, decimal_places=2,
                                                default=0, null=True, blank=True,)
    rrc_price_delivery_hour = models.DecimalField(verbose_name=l_(u'розн-стоимость часа'), max_digits=12, decimal_places=2,
                                                  default=0, null=True, blank=True,)

    is_virtual = models.BooleanField(default=False, db_index=True, verbose_name=l_(u'Виртуальный поставщик'),
                                     editable=False,
                                     help_text=l_(u'Данный поставщик не будет учавствовать в общей выборке'))

    delivery_schedule = models.PositiveSmallIntegerField(
        l_(u'Дни доставки'), choices=SCHEDULE_CHOICES, default=SCHEDULE_CHOICES.all,
        help_text=l_(u'Дни, доступные контрагентам для совершения доставки (в корзине)')
    )

    objects = SupplierManager()

    class Meta:
        verbose_name = l_(u'Поставщик')
        verbose_name_plural = l_(u'Поставщики')
        permissions = (
            ('register_contractor', l_(u'Может зарегистрировать контрагента')),
            ('view_contractors', l_(u'Может видеть список контрагентов')),
            ('edit_contractor', l_(u'Может редактировать контрагента')),
            ('view_supplier', l_(u'Может видеть список поставщиков и их контакты')),
        )

    @property
    def default_price_type(self):
        """
        Для частичной обратной совместимости. Получение типа цен по-умолчанию
        :return: PriceType instance
        """
        if hasattr(self, 'default_pricetype_id'):
            return PriceType.objects.get(pk=self.default_pricetype_id)

        return self.price_types.filter(default=True).first()

    @default_price_type.setter
    def default_price_type(self, price_type):
        """
        Проверим существует ли в БД наш поставщик И PT ещё не установлена как default И PT принадлежит поставщику
        При установки новой PT по-умолчанию, сначала снимем отметку с другой (других, если случайно выставили) PT
        И сделаем пришедшую PT - как default (по-умолчанию)
        :param price_type: PriceType instance
        :return:
        """
        if self.pk and not price_type.default and price_type.id in self.price_types.values_list('id', flat=True):
            # Используем атомарную транзакцию чтобы обойти ограничение (constraint) в БД о том,
            # что у поставщика обязательно должен быть один Тип цены по умолчанию
            with transaction.atomic():
                self.price_types.all().update(default=False)
                price_type.default = True
                price_type.save()

    @property
    def rrc_price_type(self):
        """
        Для частичной обратной совместимости. Получение РРЦ цены поставщика
        :return: PriceType instance
        """
        if hasattr(self, 'rrc_pricetype_id'):
            return PriceType.objects.get(pk=self.rrc_pricetype_id)

        return self.price_types.filter(rrc=True).first()

    @rrc_price_type.setter
    def rrc_price_type(self, pt):
        """
        Проверим существует ли в БД наш поставщик И PT ещё не установлена как rrc И PT принадлежит поставщику
        При установки новой PT РРЦ, сначала снимем отметку с другой (других, если случайно выставили) PT
        И сделаем пришедшую PT - как rrc (РРЦ)
        :param pt: PriceType instance
        :return:
        """

        if self.pk:
            if not pt:
                self.price_types.all().select_for_update().update(rrc=False)
            elif pt.id in self.price_types.values_list('id', flat=True):
                self.price_types.all().select_for_update().update(rrc=False)
                # Заново получаем объект из базы, тк объек мог измениться
                price_type = self.price_types.get(pk=pt.pk)
                price_type.rrc = True
                price_type.save()
            else:
                # пришел тип цен другого поставщика - ничего не делаем
                pass

    @cached_property
    def company_type(self):
        company = self._company
        if company:
            return company.type

    @cached_property
    def other_klass(self):
        company = self._company
        if company:
            return company.other_klass

    @property
    def name(self):
        # Переводимые поля не хранятся в МП и никто не знает какой перевод попадет в представление
        if settings.SOLID_I18N_USE_REDIRECTS:
            return self._company.name if self._company and self._company.name else 'Unknown'

        try:
            return self.supplier_view.company_name
        except SupplierView.DoesNotExist:
            return None

    @property
    def products_count(self):
        try:
            return self.supplier_view.products_count
        except SupplierView.DoesNotExist:
            return None

    @property
    def email(self):
        if self.profile.email:
            return self.profile.email
        elif self.user:
            return self.user.email
        return None

    @property
    def date_joined(self):
        if self.user:
            return self.user.date_joined
        return None

    @property
    def site(self):
        if self.profile.site:
            return self.profile.site
        return None

    @property
    def inn(self):
        return self._company.inn if self._company else None

    @property
    def kpp(self):
        return self._company.kpp if self._company else None

    @property
    def ogrn(self):
        return self._company.ogrn if self._company else None

    @property
    def jur_address(self):
        return self._company.jur_address if self._company else None

    @property
    def actual_address(self):
        return self._company.actual_address if self._company else None

    @property
    def bank(self):
        return self._company.bank if self._company else None

    @property
    def bik(self):
        return self._company.bik if self._company else None

    @property
    def corr_account(self):
        return self._company.corr_account if self._company else None

    @property
    def pay_account(self):
        return self._company.pay_account if self._company else None

    @property
    def klass(self):
        return self._company.klass if self._company else None

    @property
    def company_country(self):
        return self._company.country if self._company else None

    @property
    def external_key(self):
        # TODO: перенести в прокси-модель в стратеге
        from agora.gateways.models import ExternalLink

        external_link = ExternalLink.objects.filter(
            supplier=self,
            content_type=ContentType.objects.get_for_model(self.__class__),
            object_id=self.pk,
        ).first()

        if not external_link:
            return u'supplier_{}_{}'.format(1, self.pk)

        return external_link.uuid

    @external_key.setter
    def external_key(self, value):
        if self.pk:
            from agora.gateways.models import ExternalLink

            external_link = ExternalLink.objects.filter(
                supplier=self,
                content_type=ContentType.objects.get_for_model(self.__class__),
                uuid=value,
            ).first()

            if not external_link:
                external_link = ExternalLink()

            external_link.supplier = self
            external_link.content_type = ContentType.objects.get_for_model(self.__class__)

            external_link.object_id = self.pk

            external_link.uuid = value
            external_link.save()

            ExternalLink.objects.filter(
                supplier=self,
                content_type=ContentType.objects.get_for_model(self.__class__),
                object_id=self.pk,
            ).exclude(pk=external_link.pk).delete()

    @property
    def user(self):
        user = self.users.first()
        if not user:
            switcher = self.role_switcher_by_supplier.first()
            if switcher:
                return switcher.user
        return user

    def get_user_complicated(self):
        return self.user

    @property
    def has_requisites(self):
        return all([getattr(self, field) for field in settings.AGORA_COMPANY_FIELDS_REQUIRED if hasattr(self, field)])

    @property
    def supplier_params(self):
        return self.seller_params or {}

    @supplier_params.setter
    def supplier_params(self, value):
        for k, v in value.iteritems():
            self.seller_params = self.seller_params or {}
            self.seller_params[k] = v
        self.save()

    @property
    def shop_name(self):
        settings = self.supplier_params.get('settings', {})
        settings['main'] = settings.get('main', {})
        name = settings['main'].get('name', None)
        return name if bool(name) or self.company.exists() is None else self.company.first().name

    @property
    def rating(self):
        try:
            return xrange(self.supplier_view.rating)
        except SupplierView.DoesNotExist:
            return 0

    @property
    def rating_by_orders(self):
        return self._company.avg_rating

    @property
    def reward_percent(self):
        from agora.visual_design.models import VisualDesignConfiguration

        solo = VisualDesignConfiguration.get_solo()
        reward_percent = self.profile.reward_percent if self.profile and self.profile.reward_percent else solo.reward_percent
        return reward_percent or 0

    @super_cached_property
    def count_products(self):
        from agora.core.product.models import Product
        return Product.objects.search(supplier=self).count()

    @super_cached_property
    def count_products_shop(self):
        from agora.core.product.models import Product
        return Product.objects.search(supplier=self).filter(show_on_shop=True).count()

    def count_products_category(self, category=None):
        """
        Вернет количество товаров текущего поставщика в выбранной категории (или общее количество всех товаров)
        результат кешируется на время timeout секунд
        """

        if not category:
            return self.count_products

        from django.core.cache import cache
        from agora.core.product.models import Product

        timeout = 600   # 10 минут
        key = 'count_products_category_SUP-{supplier_id}_CAT-{category_id}'.format(
            supplier_id=self.id,
            category_id=category.id
        )

        count = cache.get(key)

        if count is None:
            count = Product.objects.search(supplier=self, category=category).count()
            cache.set(key, count, timeout)

        return count

    @cached_property
    def has_products(self):
        # TODO: какой-то маразм. Т.е. логика такая: если у поставщика не выбран тип цены по-умолчанию, то у него не товаров?
        return bool(self.default_price_type)

    @property
    def has_unbound_categories(self):
        return self.supplier_category.filter(category__isnull=True).exists()

    def get_current_price_type_id(self, session_pt=None):
        # TODO: тут проблема с логикой, для глупого agora.shop цена берется из supplier.rrc_price_type
        # TODO: срефакторил более-менее, надо проверить конечный результат как-то
        if self.default_price_type:
            if session_pt:
                return session_pt.get('id')

            if settings.AGORA_RETAIL_INSTALLATION:
                if self.rrc_price_type:
                    return self.rrc_price_type.id
                else:
                    return self.price_types.first().id
            else:
                return self.default_price_type.id
        else:
            return None

    def get_agreement(self, contractor_id):
        from agora.core.contractor.models import Agreement
        agreement = Agreement.objects.filter(contractor_id=contractor_id, supplier=self, is_active=True).first()
        return agreement

    @property
    def combo_integration(self):
        return self.integration_type == self.INTEGRATION_ERP and self.enable_data_import

    def clear_data(self):

        # Ключи доступа
        from agora.gateways.models import Token, ExternalLink
        Token.objects.filter(supplier=self.pk).delete()

        # Внешние ссылки
        ExternalLink.objects.filter(supplier=self.pk).delete()

        from agora.core.currency.models import CurrencyExchangeRate
        # Курсы валют
        CurrencyExchangeRate.objects.filter(supplier=self.pk).delete()

        from agora.core.product.models import Product, Price, Rest, SupplierCategory
        # Товары
        Product.objects.filter(supplier_category__supplier=self.pk).update(category=None)

        # Внутренние категории
        SupplierCategory.objects.filter(supplier=self.pk).delete()

        # Цены
        Price.objects.filter(price_type__supplier=self.pk).delete()

        # Остатки
        Rest.objects.filter(warehouse__supplier=self.pk).delete()

        # Договора
        from agora.core.contractor.models import Agreement
        Agreement.objects.filter(supplier=self.pk).update(deleted=True)

        # Типы цен
        from django.db import connection
        with transaction.atomic():
            # У нас на типах цен завязан триггер, который следит за тем, чтобы у поставщика всегда был один тип цен
            # отключим его на время вайпа данных по поставщику и обернем в транзакцию,
            # в теории тогда вся таблица supplier_pricetype будет заблокирована на время транзакции и другие транзакции
            # будут дожидаться её завершения => это отключение не скажется на других запросах к supplier_pricetype
            cursor = connection.cursor()
            cursor.execute('ALTER TABLE supplier_pricetype DISABLE TRIGGER only_one_default_price_type_for_single_supplier_trigger;')
            PriceType.objects.filter(supplier=self.pk).update(deleted=True)
            cursor.execute('ALTER TABLE supplier_pricetype ENABLE TRIGGER only_one_default_price_type_for_single_supplier_trigger;')

        # Склады (помечаются удаленными)
        Warehouse.objects.filter(supplier=self.pk).delete()

        # История очередь обмена
        from agora.gateways.models import ImportTask, SyncError
        ImportTask.objects.filter(supplier=self.pk).delete()
        SyncError.objects.filter(supplier=self.pk).delete()

    def __unicode__(self):
        return self.name or 'Unknown %s' % self.id

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.pk)

    @staticmethod
    def autocomplete_search_fields():
        return 'id__iexact', 'company__name__icontains'

    def __init__(self, *args, **kwargs):
        super(Supplier, self).__init__(*args, **kwargs)
        self.use_nds_initial = self.use_nds

    def save(self, *args, **kwargs):
        from agora.core.product.models import Product
        if self.use_nds_initial != self.use_nds:
            Product.objects.filter(supplier_category__supplier=self).update(
                rate_nds=Product._meta.get_field_by_name('rate_nds')[0].default if self.use_nds else 0)
        super(Supplier, self).save(*args, **kwargs)


class PriceType(SoftDeleteMixin):
    """
        На уровне БД для модели создан триггер only_one_default_price_type_for_single_supplier_trigger
        запускающий триггер-функцию validate_only_one_default_price_type_for_single_supplier
        которая проверяет, будет ли после внесённых изменений
        у Поставщика хотя бы один Тип цены выбранный по умолчанию (default=True).

        См. миграцию agora.core.supplier.migrations.0069_add_db_triggers_for_default_price_type
    """
    supplier = models.ForeignKey(Supplier, related_name='price_types')
    name = models.CharField(max_length=255)

    distribution_markets = models.ManyToManyField('product.DistributionMarket',
                                                  verbose_name=l_(u'Рынки сбыта'),
                                                  related_name='price_types',
                                                  null=True,
                                                  blank=True)

    position = models.IntegerField(verbose_name=l_(u'Позиция'), db_index=True,
                                   help_text=l_(u'Используется в дополнительной логике. При равных условиях '
                                                u'из нескольки типов цен будет выбран тот, '
                                                u'у которого меньшее значение позиции'),
                                   null=True, blank=True)

    default = models.BooleanField(
        verbose_name=l_(u'Тип цен по-умолчнию для текущего поставщика'),
        default=False,
        db_index=True,
        help_text=l_(u'Возможен только 1 тип цен по-умолчанию. '
                     u'Данный тип цен будет отображаться в каталоге по-умолчанию '
                     u'и устанавливать цену на товар при оформлении заказа на оптовой части')
    )

    rrc = models.BooleanField(
        verbose_name=l_(u'Тип цен РРЦ для текущего поставщика'),
        default=False,
        db_index=True,
        help_text=l_(u'Возможен только 1 тип цен РРЦ. '
                     u'Данный тип цен будет отображаться в каталоге как РРЦ'
                     u'и устанавливать цену на товар при оформлении заказа на розничной части (витрине)')
    )

    visible = models.BooleanField(
        verbose_name=l_(u'Отображать цены в каталоге'),
        default=False,
        db_index=True,
        help_text=l_(u'Данный тип цен будет отображаться в каталоге дополнительно с типом цен "по-умолчанию" и "РРЦ"'
                     u'Данная отметка носит исключительно визуальный характер')
    )

    objects = PriceTypeManager()

    class Meta:
        verbose_name = l_(u'Тип цен')
        verbose_name_plural = l_(u'Типы цен')

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.pk)

    @cached_property
    def currency_when_identical(self):
        assert len(set(self.price_set.all().values_list('currency_id', flat=True))) <= 1, \
            'Not all currencies in price_set are identical'
        price = self.price_set.first()
        if price:
            return price.currency

    def __unicode__(self):
        return self.name
