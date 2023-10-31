from .types import OutputType
from .registry import conversion


@conversion(OutputType.LastModified)
def last_modified_processor(resource):
    if hasattr(resource, "get_last_modified"):
        return resource.get_last_modified()
    else:
        return None


@conversion(OutputType.LastMetadataChange)
def last_metadata_change_processor(resource):
    if hasattr(resource, "get_last_metadata_change"):
        return resource.get_last_metadata_change()
    else:
        return last_modified_processor(resource)
