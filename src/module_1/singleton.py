from datetime import date


class MetaClassWithDate(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        namespace["created_at"] = date.today()
        return super().__new__(mcs, name, bases, namespace, **kwargs)


class SingletonMeta(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
            return cls.__instance
        return cls.__instance


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class User(Singleton):
    def __init__(self, name: str):
        self.name = name


class Animal(metaclass=SingletonMeta):
    def __init__(self, name: str):
        self.name = name


class Car(metaclass=MetaClassWithDate):
    def __init__(self, name: str):
        self.name = name


if __name__ == "__main__":
    user_1 = User("Bob")
    user_2 = User("Mike")
    print(user_1 is user_2)
    animal_1 = Animal("Fluffy")
    animal_2 = Animal("Kitty")
    print(id(animal_1), id(animal_2))
    car_1 = Car("Toyota")
    print(car_1.created_at)
