# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from os2datascanner.utils.batch import Batch


class DummyBatch(Batch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accumulator = 0

    def flush(self):
        self.accumulator += sum(self._batch)
        return super().flush()


class TestBatch:
    def test_autoflush(self):
        with DummyBatch(batch_size=50) as batch:
            for i in range(0, 49):
                batch.append(i)
            assert batch.count == 0
            batch.append(49)
            assert batch.count == 50

        assert batch.accumulator == sum(range(0, 50))

    def test_context_flush(self):
        with DummyBatch(batch_size=50) as batch:
            for i in range(0, 49):
                batch.append(i)
            assert batch.count == 0
        assert batch.count == 49

        assert batch.accumulator == sum(range(0, 49))

    def test_manual_flush(self):
        with DummyBatch(batch_size=50) as batch:
            for i in range(0, 49):
                batch.append(i)
            assert batch.count == 0
            batch.flush()
            assert batch.count == 49

        assert batch.accumulator == sum(range(0, 49))
