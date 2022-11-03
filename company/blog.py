from django.views.generic import ListView


"""
class News(ListView) :
    model = Blog
    template_name = 'blog-list-xchange.html' 
    context_object_name = 'blogs'
    
    def get_queryset(self,*args,**kwargs) :
        _all = self.model.objects.filter(blog_type = 'XCHANGE').order_by('-date')[:4]
        return _all

    def get_context_data(self,*args,**kwargs) : 
        context = super(News,self).get_context_data(*args,**kwargs) 
        context['bclass'] = 'active'
        return context    """