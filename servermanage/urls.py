from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^servermanage/', include('servermanage.foo.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
