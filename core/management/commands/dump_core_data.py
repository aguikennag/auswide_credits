from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata
from django.core import management
from django.contrib.auth import get_user_model
from django.conf import settings
import os



class Command(BaseCommand) :
    def handle(self, *args, **options) :
        
        models = {
            "shop.productclass" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_class.json"),
            "shop.productcategory" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_category.json"),
            "shop.productattribute" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_attribute.json"),
            "shop.productattributeoption" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_attribute_option.json"),
            "shop.productattributeoptiongroup" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_attribute_option_group.json"),
            "shop.productattributevalue" : os.path.join(settings.BASE_DIR,"shop","fixtures","product_attribute_value.json"),
            "core.state" : os.path.join(settings.BASE_DIR,"core","fixtures","state.json"),
            "core.campus" : os.path.join(settings.BASE_DIR,"core","fixtures","campus.json"),
            "core.location" : os.path.join(settings.BASE_DIR,"core","fixtures","location.json"), 
        }


        for model,output_path in models.items() :
            if not os.path.exists(output_path) :
                #obtain the file name
                dir,filename = os.path.split(output_path)
                if not os.path.exists(dir) :
                    os.makedirs(dir)
                #then create file
                with open(output_path,"w") :
                    pass
            self.stdout.write("dumping {} data".format(model))
            management.call_command("dumpdata",model,output = output_path)