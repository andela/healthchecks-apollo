from datetime import timedelta
import time

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from hc.accounts.models import Profile
from hc.api.models import Check


def num_pinged_checks(profile):
    q = Check.objects.filter(user_id=profile.user.id, )
    q = q.filter(last_ping__isnull=False)
    return q.count()


class Command(BaseCommand):
    help = 'Sending due reports'
    tmpl = "Sending {0} report to {1}"

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            action='store_true',
            dest='loop',
            default=False,
            help='Keep running indefinitely in a 300 second wait loop',
        )

    def handle_one_run(self):
        periods = {'daily': 1, 'weekly': 7, 'monthly': 30}
        counter = 0
        for period in periods.items():
            print(period)
            counter += self.num_reports_sent(period)
        return counter

    def num_reports_sent(self, period):
        now = timezone.now()
        period_before = now - timedelta(days=period[1])
        report_due = Q(next_report_date__lt=now)
        report_not_scheduled = Q(next_report_date__isnull=True)
        q = Profile.objects.filter(report_due | report_not_scheduled)
        q = q.filter(reports_allowed=True)
        if period[0] == 'daily':
            q = q.filter(report_period=2)
        elif period[0] == 'weekly':
            q = q.filter(report_period=1)
        elif period[0] == 'monthly':
            q = q.filter(report_period=0)
        q = q.filter(user__date_joined__lt=period_before)
        sent = 0
        for profile in q:
            if num_pinged_checks(profile) > 0:
                self.stdout.write(self.tmpl.format(period[0], profile.user.email))
                profile.send_report()
                sent += 1
        return sent

    def handle(self, *args, **options):
        if not options["loop"]:
            return "Sent %d reports" % self.handle_one_run()

        self.stdout.write("sendreports is now running")
        while True:
            self.handle_one_run()

            formatted = timezone.now().isoformat()
            self.stdout.write("-- MARK %s --" % formatted)

            time.sleep(300)
