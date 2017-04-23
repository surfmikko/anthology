"""Just for fun implementation of parallel distributable aggregate workflow
with Luigi. This would be calculating sums in mongo gluster, hadoop or similar
etc."""

import logging

from json import loads

import luigi
import luigi.contrib.mongodb
import luigi.scheduler
import luigi.worker

# tests will monkeypatch database, so we use direct import
import anthology.database

logging.basicConfig(loglevel=logging.DEBUG)


class SongsData(luigi.ExternalTask):
    """Check that input file created by some other process exists"""

    filename = luigi.Parameter(default='tests/data/songs.json')

    def output(self):
        """Return our source file"""
        return luigi.LocalTarget(self.filename)


class SongsByLevel(luigi.Task):
    """Since our source data is in single file, we just simulate here that we
    would get each level from different data set.
    """

    level = luigi.IntParameter()

    def output(self):
        """Output target"""
        return luigi.LocalTarget('tmp/songs_by_level_%s.json' % self.level)

    def requires(self):
        """Requires songs data"""
        return SongsData()

    def run(self):
        """Write songs by level to our target file"""
        with self.output().open('w') as outfile:
            for song_json in self.input().open():
                song = loads(song_json)
                if song["level"] == self.level:
                    outfile.write(song_json)


class CalculateTotalDifficulty(luigi.Task):
    """Calculate averages for given level"""

    level = luigi.IntParameter()

    def requires(self):
        """Requires songs data for given leven"""
        return SongsByLevel(self.level)

    def run(self):
        """Write averages to database"""

        total_difficulty = 0
        number_of_songs = 0

        for song_json in self.input().open():
            song = loads(song_json)
            number_of_songs += 1
            total_difficulty += song["difficulty"]

        anthology.database.db_averages().update(
            {'_id': self.level},
            {'_id': self.level,
             'level': self.level,
             'total_difficulty': total_difficulty,
             'number_of_songs': number_of_songs},
            upsert=True)

    def complete(self):
        """Return complete when given result exists"""
        result = anthology.database.db_averages().find_one(
            {'_id': self.level})
        return result is not None


class RunTotals(luigi.WrapperTask):
    """Calculate difficulty averages for all levels"""

    def requires(self):
        """Requires average calculation for each level"""
        for level in range(0, 20):
            yield CalculateTotalDifficulty(level)


def calculate_totals():
    """Run the average workflow"""

    scheduler = luigi.scheduler.Scheduler()
    worker = luigi.worker.Worker(scheduler=scheduler, worker_processes=5)

    averages = RunTotals()

    with worker:
        worker.add(averages)
        worker.run()

    print luigi.execution_summary.summary(worker)
