from pykube.objects import APIObject


def adopt(owner: APIObject, children: APIObject) -> APIObject:
    if not children.metadata.get("ownerReferences", None):
        children.metadata["ownerReferences"] = list()
    owner_reference = {
        "apiVersion": owner.version,
        "kind": owner.__class__.__name__,
        "name": owner.name,
        "uid": owner.metadata["uid"]
    }
    if not any(child_owner.get("uid") == owner.metadata["uid"]
               for child_owner in children.metadata["ownerReferences"]):
        children.metadata["ownerReferences"].append(owner_reference)
    return children


def ensure(resource: APIObject, owner: APIObject) -> APIObject:
    if not resource.exists():
        if owner.namespace == resource.namespace:
            resource = adopt(owner, resource)
        resource.create()
    else:
        resource.update()
    return resource
