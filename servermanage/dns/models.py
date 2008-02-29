from django.db import models
from servermanage.customer.models import Customer



class Zone(models.Model):
    id = models.IntegerField(default=1, editable=False, primary_key=True)
    domain_name = models.CharField(max_length=255, blank=False)
    prepend_www = models.BooleanField(default=True)
    add_mx = models.BooleanField(default=True)
    soa = models.CharField(max_length=255, default="a.ns.myns.net hostmaster.myns.net 0 10800 3600 604800 3600")
    a_record = models.CharField(max_length=255, default="127.0.0.1")
    mx_record = models.CharField(max_length=255, default="a.mx.mymx.net")
    mx_prio = models.CharField(max_length=255, default="10")
    ns1_record = models.CharField(max_length=255, default="a.ns.myns.net")
    ns2_record = models.CharField(max_length=255, default="b.ns.myns.net")
    owner = models.ForeignKey(Customer)

    class Admin:
        pass

    def __str__(self):
        return self.domain_name

    def save(self):
        super(Zone, self).save()
        self.process_zone()
        super(Zone, self).delete()

    def process_zone(self):
        domain = Domain.objects.create(name=self.domain_name, type="MASTER", customer=self.owner)
        if domain:
            soa = Record.objects.create(domain=domain, name=self.domain_name, type="SOA", content=self.soa)
            a_record = Record.objects.create(domain=domain, name=self.domain_name, type="A", content=self.a_record)
            ns = Record.objects.create(domain=domain, name=self.domain_name, type="NS", content=self.ns1_record)
            ns = Record.objects.create(domain=domain, name=self.domain_name, type="NS", content=self.ns2_record)
            if self.prepend_www:
                www = Record.objects.create(domain=domain, name="www.%s" % self.domain_name, type="A", content=self.a_record)
            if self.add_mx:
                mx = Record.objects.create(domain=domain, name=self.domain_name, type="MX", content=self.mx_record, prio=self.mx_prio)


class Domain(models.Model):
    DOMAIN_TYPE_CHOICES = (
        ('NATIVE', 'Native'),
        ('MASTER', 'Master'),
        ('SLAVE', 'Slave'),
    )

    name = models.CharField(max_length=255, blank=False, unique=True, help_text='Example: example.com')
    master = models.CharField(max_length=128, blank=True, null=True, help_text='Master for the domain informations')
    last_check = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=6, blank=False, null=False, choices=DOMAIN_TYPE_CHOICES, help_text="Domain type, example: Native")
    notified_serial = models.IntegerField(null=True, blank=True)
    account = models.CharField(max_length=40, blank=True, null=False)
    customer = models.ForeignKey(Customer)

    class Meta:
        ordering = ('name',)
        db_table = 'domains'
      
    class Admin:
        fields = (
            (None, {
                'fields': ('name', 'type', 'customer'),
            }),
            ('Advanced options', {
                'fields': ('master', 'notified_serial', 'account'),
                'classes': 'collapse',
                'description': 'Additional domain options'}),
            )
    
        list_display = ('name', 'type', 'last_check', 'customer',)
        list_display_links = ('name', 'type')
        list_filter = ('customer',)
        search_fields = ('name',)
    
    def __str__(self):
        return '%s' % (self.name)
   
   
class Record(models.Model):
    RECORD_TYPE_CHOICES = (
        ('A', 'A'),
        ('AAAA', 'AAAA'),
        ('AFSDB', 'AFSDB'),
        ('CERT', 'CERT'),
        ('CNAME', 'CNAME'),
        ('DNSKEY', 'DNSKEY'),
        ('DS', 'DS'),
        ('HINFO', 'HINFO'),
        ('KEY', 'KEY'),
        ('LOC', 'LOC'),
        ('MX', 'MX'),
        ('NAPTR', 'NAPTR'),
        ('NS', 'NS'),
        ('NSEC', 'NSEC'),
        ('PTR', 'PTR'),
        ('RP', 'RP'),
        ('RRSIG', 'RRSIG'),
        ('SOA', 'SOA'),
        ('SPF', 'SPF'),
        ('SSHFP', 'SSHFP'),
        ('SRV', 'SRV'),
        ('TXT', 'TXT'),
    )
    domain = models.ForeignKey(Domain, related_name="record_set")
    name = models.CharField(max_length=255, db_index=True, null=True, blank=False, help_text='www.example.com')
    type = models.CharField(max_length=6, db_index=True, null=True, blank=False, choices=RECORD_TYPE_CHOICES)
    content = models.CharField(max_length=255, null=True, blank=False, help_text='192.168.1.100')
    ttl = models.IntegerField(null=True, blank=False, default=86400, help_text='TTL in seconds', verbose_name='TTL')
    prio = models.IntegerField(null=True, blank=True, help_text='Mail exchange priority', verbose_name="Priority")
    change_date = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        ordering = ('domain','type', 'name',)
        db_table = 'records'
      
      class Admin:
          list_display = ('domain', 'name', 'type', 'content', 'change_date')
          list_display_links = ('domain', 'name')
          list_filter = ('type', 'domain',)
          search_fields = ('domain', 'name', 'content')
    
      def __str__(self):
          return '%s' % (self.name) 

      def gen_bind_slavezone(self, file_path='/etc/bind/slave/', master_ips=('213.133.101.87',)):
          return 'zone "%s" { type slave; file "%s%s";  allow-transfer {default-ns;}; masters { %s; }; };' % ( self.name, file_path, self.name, ';'.join(master_ips) )

      @staticmethod
      def update_dyn(name, ip):
          """Update DynIP-Zone
          FIXME... make name dynamic 
          """
          try:
              name = name + '.dyn.myzone.net'
              rec = Record.objects.get(name=name, type="A")
              rec.content = ip
              rec.save()
              return u'OK: "%s" updated' % name
          except DoesNotExist:
              return u'Error while updating "%s". Not in database.' % name
          except:
              return u'Error while updating "%s"' % name
