from django.core.management.base import BaseCommand
from django.core.management.commands import loaddata
from django.core import management
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'sets up all necessary credentials for the app to work'

    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument(
            '--test',
            action='store_true',
            help='load test data as well for test purposes',
        )
        #parser.add_argument('-en', '--env_name', type=str,help = "indicates the environmenntal name")
        #parser.add_argument('-wd_id','--webhook_id',type=str,help = "webhook id to be deleted")

    main_data = [
        "currency.json",
        "country.json"
    ]

    test_data = [
        'users.json',
    ]

    def download_dependencies(self):
        # NLTK
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')

    def load_data(self):
        self.stdout.write("setting up to load initial database data ...")
        self.stdout.write("")
        self.stdout.write("loading main data")
        self.stdout.write("")
        for data in self.main_data:
            self.stdout.write("loading {} ...".format(data))
            management.call_command("loaddata", data, verbosity=0)

        if self.is_test:
            self.stdout.write("")
            self.stdout.write("loading test data")
            self.stdout.write("")
            for data in self.test_data:
                self.stdout.write("loading {} ...".format(data))
                management.call_command("loaddata", data, verbosity=0)

    def create_admin(self):

        if not get_user_model().objects.filter(username="fiberswift_admin").exists():
            self.stdout.write("creating super user 'fiberswift_admin' ")
            get_user_model().objects.create_superuser("fiberswift_admin",
                                                      "admin@fiberswift.com", "#@Kyletech99-tethub")
            self.stdout.write(
                "superuser 'fiberswift_admin' created successfully")
        else:
            self.stdout.write("superuser 'fiberswift_admin' already exists..")

        self.stdout.write("proceeding..")

    def handle(self, *args, **options):
        self.is_test = options.get("test", False)
        self.stdout.write("setting up server ...")
        #self.download_dependencies()
        #self.create_admin()
        self.load_data()

        self.stdout.write("setup is complete, finishing...")
