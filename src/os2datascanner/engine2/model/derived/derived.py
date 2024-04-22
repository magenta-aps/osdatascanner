from ..core import Source, Handle
import inspect


class DerivedSource(Source):
    """A DerivedSource is a convenience class for a Source backed by a Handle.
    It provides sensible default implementations of Source.handle,
    Source.censor, Source.remap, and Source.to_json_object, and automatically
    registers the constructor of every (non-abstract) subclass as a JSON object
    decoder for Sources."""

    derived_from: type | None = None

    def __init__(self, handle):
        if self.derived_from and not isinstance(handle, self.derived_from):
            raise TypeError(
                    f"expected '{self.derived_from.__name__}',"
                    f" but got '{type(handle).__name__}'")
        self._handle = handle

    @classmethod
    def _make(cls, *args, **kwargs):
        if not cls.derived_from:
            raise TypeError(
                    "make() is only supported for DerivedSources with a"
                    " single valid Handle derivation")
        return cls(cls.derived_from(*args, **kwargs))

    @property
    def handle(self):
        return self._handle

    def censor(self):
        return type(self)(self.handle.censor())

    def to_json_object(self):
        return dict(**super().to_json_object(), handle=self.handle.to_json_object())

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Class creation controller. Whenever a concrete subclass is
        initialised, registers its constructor as a JSON object decoder for
        Sources."""
        super().__init_subclass__(**kwargs)

        if not inspect.isabstract(cls):
            @Source.json_handler(cls.type_label)
            def _from_json_object(obj):
                return cls(Handle.from_json_object(obj["handle"]))

    def remap(self, mapping) -> Source:
        if self in mapping:
            # This DerivedSource is directly identified in the mapping
            return mapping.get(self)
        else:
            remapped_handle = self.handle.remap(mapping)
            if remapped_handle is self.handle:
                # The remapping would do nothing, so there's no need to make a
                # new object
                return self
            else:
                return type(self)(remapped_handle)
