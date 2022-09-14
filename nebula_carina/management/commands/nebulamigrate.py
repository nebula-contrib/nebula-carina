try:
    from django.core.management.base import BaseCommand, CommandError
    from nebula_carina.models.migrations import make_migrations, migrate


    class Command(BaseCommand):
        help = 'Run Nebula Graph migrations'

        def handle(self, *args, **options):
            migrations = make_migrations()
            if not migrations:
                self.stdout.write('No Nebula Graph schema change found')
                return
            self.stdout.write('The following migration NGQLs will be executed: \n\n%s' % ('\n'.join(migrations)))
            if input("Type 'yes' to continue, or 'no' to cancel\n") == 'yes':
                migrate(make_migrations())
                self.stdout.write(self.style.SUCCESS('Nebula migration succeeded.'))
            else:
                self.stdout.write(self.style.NOTICE('Nebula migration cancelled.'))

except ModuleNotFoundError:
    pass
