from familytree.models.base_model import FamilyTreeBaseResponse


class PyvisGraphRenderResponse(FamilyTreeBaseResponse):
    graph_html: str


class CustomGraphRenderResponse(FamilyTreeBaseResponse):
    pass
