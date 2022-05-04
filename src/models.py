from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def serialize(self):
        return{
            "id":self.id,
            "user":self.user,
            "email":self.email
        }

class Favorites(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    Planets = db.relationship("Planets")
    People = db.relationship("People")
    User = db.relationship("User")   

    def serialize(self):
        return{
            "id":self.id,
            "user_id":self.user_id,
            "planets_id":self.planets_id,
            "people_id":self.people_id
        }

class People(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(250))
    name = db.Column(db.String(50), nullable=False)
    height = db.Column(db.String(100))
    mass = db.Column(db.String(50))
    hair_color = db.Column(db.String(50))
    skin_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    birth_year = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    homeworld = db.Column(db.String(100))  

    def serialize(self):
        return{
            "id":self.id,
            "image":self.image,
            "height":self.height,
            "mass":self.mass,
            "hair_color":self.hair_color,
            "skin_color":self.skin_color,
            "eye_color":self.eye_color,
            "birth_year":self.birth_year,
            "gender":self.gender,
            "name":self.name,
            "homeworld":self.homeworld,
        }

        def serialize2(self):
            return{
                "id":self.id,
                "name":self.name,
            }

class Planets(db.Model):
    #__tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(250))
    name = db.Column(db.String(100), nullable=False)
    climate = db.Column(db.String(100))
    diameter = db.Column(db.String(100))
    gravity = db.Column(db.String(100))
    orbital_period = db.Column(db.String(100))
    population = db.Column(db.String(100))
    rotation_period = db.Column(db.String(100))
    surface_water = db.Column(db.String(100))
    terrain = db.Column(db.String(100))

    def serialize(self):
        return{
            "id":self.id,
            "image":self.image,
            "climate":self.climate,
            "diameter":self.diameter,
            "gravity":self.gravity,
            "name":self.name,
            "orbital_period":self.orbital_period,
            "population":self.population,
            "rotation_period":self.rotation_period,
            "surface_water":self.surface_water,
            "terrain":self.terrain,
        }
    
    def serialize2(self):
        return{
            "id":self.id,
            "name":self.name,
        }

    def __init__(self, *args, **kwargs):
        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type 
                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore all the other values : {error.args}")

    @classmethod
    def create(cls, data):
        ##creating instancing.
        instance = cls(**data)
        ##checking if the instance is on the same class
        if (not isinstance(instance,cls)):
            print("blew up")
            return None
        db.session.add(instance)

        try:
            db.session.commit()
            print(f"created: {instance.name}")
        except Exception as error:
            db.session.rollback()
            print(error.args)