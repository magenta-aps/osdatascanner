from django.db import models
from ...core.models.background_job import BackgroundJob
from .scannerjobs.filescanner_model import FileScanner


class CheckDuplicatesJob(BackgroundJob):
    """A BackgroundJob that scan a file drive and checks for duplicate
    files."""

    filescanner = models.ForeignKey(FileScanner,
                                    on_delete=models.DO_NOTHING,
                                    blank=False,
                                    null=False)

    handles = models.IntegerField(blank=True, null=True)
    handles_checked = models.IntegerField(blank=True, null=True)

    @property
    def progress(self):
        if self.handles is None:
            return None

        return (self.handles_checked / self.handles
                if self.handles_checked is not None
                else None)

    @property
    def job_label(self) -> str:
        return "Check Duplicates Job"

    def run(self):
        sources = self.filescanner.generate_sources()

        for source in sources:
            print(f"Discovered source: {source}")
