from graph.models import models, fields


class Figure(models.TagModel):
    vid: int = fields.VIDField(..., )
    name: str = fields.StringField(..., max_length=50, )
    is_male: bool = fields.BoolField(True)


class Source(models.TagModel):
    vid: int = fields.VIDField(..., )
    name: str = fields.StringField(..., max_length=50, )


class Belong(models.EdgeTypeModel):
    pass
