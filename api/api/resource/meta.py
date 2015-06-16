metas = {}


def add_meta(ep_name, m):
    metas[ep_name] = m


def get_all_meta():
    return metas


def api_metable(orginal_class):
    add_meta(orginal_class.ep_name, orginal_class.description)
    return orginal_class
