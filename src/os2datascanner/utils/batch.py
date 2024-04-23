from abc import ABC, abstractmethod


class Batch(ABC):
    """A Batch is a convenient way of performing an operation once a certain
    number of objects have been collected. (It can also be used as a context
    manager: at exit time, it will perform the operation an extra time.)"""
    def __init__(self, batch_size=2000):
        self._batch = []
        self._batch_size = batch_size
        self._count = 0

    @property
    def count(self):
        """Returns the total number of objects operated on by this Batch.
        (Objects that have been added but not yet operated on are not included
        in this count.)"""
        return self._count

    def append(self, obj):
        """Adds an object to this Batch, triggering the operation if the
        required number of objects have been collected."""
        self._batch.append(obj)

        match len(self._batch):
            case 0:
                pass
            case k if k % self._batch_size == 0:
                self.flush()
            case _:
                pass

    @abstractmethod
    def flush(self):
        """Performs the operation associated with this Batch.

        Subclasses must implement this method, and should also call the
        parent class implementation to clear the internal object list."""
        self._count += len(self._batch)
        self._batch.clear()

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, traceback):
        self.flush()


class BatchUpdate(Batch):
    def __init__(self, manager, props, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._manager = manager
        self._props = list(props)

    def flush(self):
        self._manager.bulk_update(self._batch, self._props)
        return super().flush()
