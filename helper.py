"""Utility functions to support the notebook."""

import json
import watson_developer_cloud

def fetch_credentials(service_name, creds_file="service-credentials.json"):
    """Fetch credentials for cloud services from file.
    
    Params
    ======
    - service_name: a Watson service name, e.g. "discovery" or "conversation"
    - creds_file: file containing credentials in JSON format
    
    Returns
    =======
    creds: dictionary containing credentials for specified service
    """
    
    with open(creds_file, "r") as f:
        creds = json.load(f)
        return creds[service_name]


def fetch_object(service, obj_type, obj_name, create=False, create_args={}, **fetch_args):
    """Helper function to fetch objects from the Watson services.
    
    Params
    ======
    - service: a Watson service instance
    - obj_type: object type, one of: "environment", "configuration", "collection", "workspace"
    - obj_name: name used to look up / create object
    - create: whether to create object if not found (default: False)
    - create_args: arguments to pass in when creating, other than name
    - fetch_args: other arguments used to fetch object, e.g. environment_id
    
    Returns
    =======
    obj, obj_id: fetched object and its unique ID (for convenience)
    """

    # Methods for each object type
    list_methods = {
        "environment": "list_environments",
        "configuration": "list_configurations",
        "collection": "list_collections",
        "workspace": "list_workspaces"
    }
    get_methods = {
        "environment": "get_environment",
        "configuration": "get_configuration",
        "collection": "get_collection",
        "workspace": "get_workspace"
    }
    create_methods = {
        "environment": "create_environment",
        "configuration": "create_configuration",
        "collection": "create_collection",
        "workspace": "create_workspace"
    }
    
    # Look up by name
    obj = None
    obj_id = None
    obj_list = getattr(service, list_methods[obj_type])(**fetch_args)
    obj_list = obj_list.get_result()

    for o in obj_list[obj_type + "s"]:
        if o["name"] == obj_name:
            obj = o
            obj_id = obj[obj_type + "_id"]
            print("Found {}: {} ({})".format(obj_type, obj_name, obj_id))
            break
    
    if obj_id: # fetch object
        fetch_args[obj_type + "_id"] = obj_id
        obj = getattr(service, get_methods[obj_type])(**fetch_args)
        obj.get_result()
    elif create:  # create new, if desired
        if obj_type == "configuration":
            create_args["config_data"]["name"] = obj_name
        else:
            create_args["name"] = obj_name
            print(create_args)
        obj = getattr(service, create_methods[obj_type])(**create_args)
        obj = obj.get_result()
        obj_id = obj[obj_type + "_id"]
        obj = json.dumps(obj, indent=2)
        print("Created {}: {} ({})".format(obj_type, obj_name, obj_id))
    
    return obj, obj_id