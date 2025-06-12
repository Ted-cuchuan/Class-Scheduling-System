# %%
import numpy as np
import pandas as pd
from itertools import chain
from collections.abc import Iterable


# %%
class Schedule:
    def __init__(
        self, row: int = 0, col: int = 0, name: str = "", row_name=None, col_name=None
    ):
        self.table = pd.DataFrame(
            np.full((row, col), None), index=row_name, columns=col_name
        )
        self.name = name

    def __str__(self):
        return f"Schedule:\n{self.table}"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row, col = key
            return self.table.iloc[row, col]
        else:
            raise TypeError("You can only get one course now")

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            row, col = key
            self.set_course(value, row, col)
        else:
            raise TypeError("You can only set one course now")

    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def set_table(self, table: pd.DataFrame):
        self.table = table

    def get_table(self):
        return self.table

    def set_course(self, course, row: int, col: int):
        if self.table.iloc[row, col] is not None:
            self.drop_course(row, col)
        self.table.iloc[row, col] = course
        self.table.iloc[row, col].schedule_row = row
        self.table.iloc[row, col].schedule_col = col

    def get_course(self, row: int, col: int):
        return self.table.iloc[row, col]

    def drop_course(self, row: int, col: int):
        self.table.iloc[row, col].schedule_row = None
        self.table.iloc[row, col].schedule_col = None
        self.table.iloc[row, col] = None

    def update(self):
        self.table.map(lambda e: e and e.update())


class Teacher_or_Class:
    def __init__(self, schedule: Schedule, name="", type=""):
        self.name = name
        self.type = type
        self.schedule = schedule
        self.schedule.name = self.name

    def __str__(self):
        return f"{self.type}: name={self.name}\n{self.schedule}"

    def __repr__(self):
        return self.__str__()

    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def set_schedule(self, schedule: Schedule):
        self.schedule = schedule
        self.schedule.name = self.name

    def get_schedule(self):
        return self.schedule

    def set_course(self, course, row: int, col: int):
        self.schedule.set_course(course, row, col)

    def get_course(self, row: int, col: int):
        return self.schedule.get_course(row, col)

    def drop_course(self, row: int, col: int):
        self.schedule.drop_course(row, col)

    def update(self):
        self.schedule.update()


class Class(Teacher_or_Class):
    def __init__(self, schedule: Schedule, name=""):
        super().__init__(schedule, name, "Class")

    @staticmethod
    def empty(name: str = ""):
        return Class(schedule=Schedule(name=name), name=name)

    @staticmethod
    def empty_schedule(row: int = 0, col: int = 0, name: str = ""):
        return Class(schedule=Schedule(row, col, name=name), name=name)


class Teacher(Teacher_or_Class):
    def __init__(self, schedule: Schedule, name=""):
        super().__init__(schedule, name, "Teacher")

    @staticmethod
    def empty(name: str = ""):
        return Teacher(schedule=Schedule(name=name), name=name)

    @staticmethod
    def empty_schedule(row: int, col: int, name: str):
        return Teacher(schedule=Schedule(row, col, name=name), name=name)


# %%
class ObjectDict:
    def __init__(self, objs: list, name: str, init_func, **kwarg):
        self.name = name
        self.dict = {}
        if isinstance(objs, Iterable):
            for obj in objs:
                if obj not in self.dict:
                    self.dict[obj] = []
                self.dict[obj].append(init_func(**kwarg, name=obj))
        elif isinstance(objs, str):
            self.dict[objs] = [init_func(**kwarg, name=objs)]

    def __init__(self, name: str, *objs):
        self.name = name
        self.dict = {}
        for obj in objs:
            if obj.name not in self.dict:
                self.dict[obj.name] = []
            self.dict[obj.name].append(obj)

    def __iter__(self):
        return iter(chain.from_iterable(self.dict.values()))

    def items(self):
        return iter(self.dict.items())

    def __len__(self):
        return len(tuple(chain.from_iterable(self.dict.values())))

    def __str__(self):
        return f"{self.name}: " + ", ".join(self.get_names())

    def __repr__(self):
        return self.__str__()

    def get_dict(self):
        return self.dict

    def get_name(self):
        return ", ".join(
            set(map(lambda e: e.get_name(), chain.from_iterable(self.dict.values())))
        )

    def get_names(self):
        return tuple(
            set(map(lambda e: e.get_name(), chain.from_iterable(self.dict.values())))
        )

    def append(self, obj):
        if obj not in self.dict:
            self.dict[obj.name] = []
        self.dict[obj.name].append(obj)

    def extend(self, objs):
        for key, value in objs.items():
            if key not in self.dict:
                self.dict[key] = value
            else:
                self.dict[key].extend(value)

    def update(self):
        for obj in self:
            obj.update()

    def remove(self, obj):
        if isinstance(obj, str):
            self.dict.pop(obj, -1)
        else:
            if obj.name in self.dict:
                self.dict[obj.name].remove(obj)

    def get(self, obj: str):
        o = self.dict.get(obj, -1)
        if o == -1:
            return -1
        if len(o) == 1:
            return o[0]
        return o


class TeacherDict(ObjectDict):
    def __init__(
        self,
        *teachers: Iterable,
        init: bool = False,
        schedule_row: int = 0,
        schedule_col: int = 0,
    ):
        if init:
            super().__init__(
                teachers,
                "Teachers",
                Teacher.empty_schedule,
                row=schedule_row,
                col=schedule_col,
            )
        else:
            super().__init__("Teachers", *teachers)


class ClassDict(ObjectDict):
    def __init__(
        self,
        *classes: Iterable,
        init: bool = False,
        schedule_row: int = 0,
        schedule_col: int = 0,
    ):
        if init:
            super().__init__(
                classes,
                "Classes",
                Class.empty_schedule,
                row=schedule_row,
                col=schedule_col,
            )
        else:
            super().__init__("Classes", *classes)


class CourseDict(ObjectDict):
    def __init__(
        self,
        *courses: Iterable,
        init: bool = False,
        teacher: Teacher = Teacher.empty(),
        cls: Class = Class.empty(),
    ):
        if init:
            super().__init__(
                courses,
                "Courses",
                Course,
                teacher=teacher,
                cls=cls,
            )
        else:
            super().__init__("Courses", *courses)


class Course:
    def __init__(
        self,
        name: str = "",
        teacher: TeacherDict = TeacherDict(),
        cls: ClassDict = ClassDict(),
    ):
        self.name = name
        self.set_teacher(teacher)
        self.set_class(cls)
        self.schedule_row = None
        self.schedule_col = None

    def __str__(self):
        return self.show_all()

    def __repr__(self):
        return self.__str__()

    def set_teacher(self, teacher: TeacherDict):
        if isinstance(teacher, Teacher):
            self.teacher = TeacherDict(teacher)
        elif isinstance(teacher, TeacherDict):
            self.teacher = teacher
        elif teacher is None:
            self.teacher = TeacherDict()
        elif isinstance(teacher, str):
            self.set_class(Teacher.empty(teacher))
        else:
            raise TypeError(
                "You can only use the type of Teacher, TeacherDict, None and str"
            )

    def get_teacher(self):
        return self.teacher

    def drop_teacher(self, name: Teacher):
        self.teacher.remove(name)

    def set_class(self, cls: Class):
        if isinstance(cls, Class):
            self.cls = ClassDict(cls)
        elif isinstance(cls, ClassDict):
            self.cls = cls
        elif cls is None:
            self.cls = ClassDict()
        elif isinstance(cls, str):
            self.set_class(Class.empty(cls))
        else:
            raise TypeError(
                "You can only use the type of Class, ClassDict, None and str"
            )

    def get_class(self):
        return self.cls

    def drop_class(self, name):
        self.cls.remove(name)

    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def show_teacher(self):
        return f"{self.name}, {self.cls.get_name() if self.cls else ''}"

    def show_class(self):
        return f"{self.name}, {self.teacher.get_name() if self.teacher else ''}"

    def show_all(self):
        return f"Course(name={self.name}, teacher={self.teacher.get_name() if self.teacher else ''}, class={self.cls.get_name() if self.cls else ''})"

    def update(self):
        if self.schedule_row is not None and self.schedule_col is not None:
            if len(self.teacher) != 0:
                for t in self.teacher:
                    t.set_course(self, self.schedule_row, self.schedule_col)
            if len(self.cls) != 0:
                for c in self.cls:
                    c.set_course(self, self.schedule_row, self.schedule_col)


# %%
if __name__ == "__main__":
    alex = Teacher.empty_schedule(3, 3, "Alex")
    bob = Teacher.empty_schedule(3, 3, "Bob")
    j1a = Class.empty_schedule(3, 3, "J1A")
    cl = CourseDict(Course("Chinese", alex, j1a))
    cl.get("Chinese").get_teacher().append(bob)
    print(cl.get("Chinese"))
    print("-" * 20)
    print(alex)
    print("-" * 20)
    alex.set_course(cl.get("Chinese"), 0, 0)
    print(alex)
    print("-" * 20)
    print(j1a)
    print("-" * 20)
    cl.update()
    print(j1a)
    print("-" * 20)
# %%
